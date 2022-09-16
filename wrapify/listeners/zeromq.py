import logging
import json
import time

import numpy as np
import zmq

from wrapify.connect.listeners import Listener, ListenerWatchDog, Listeners
from wrapify.middlewares.zeromq import ZeroMQMiddleware
from wrapify.encoders import JsonDecodeHook


class ZeroMQListener(Listener):

    def __init__(self, name, in_port, carrier="tcp",
                 socket_ip="127.0.0.1", socket_port=5555, **kwargs):
        carrier = carrier if carrier else "tcp"
        super().__init__(name, in_port, carrier=carrier, **kwargs)
        ZeroMQMiddleware.activate()
        self.socket_address = f"{carrier}://{socket_ip}:{socket_port}"

    def await_connection(self, port=None, repeats=None):
        connected = False
        if port is None:
            port = self.in_port
        logging.info(f"Waiting for input port: {port}")
        if repeats is None:
            if self.should_wait:
                repeats = -1
            else:
                repeats = 1

            while repeats > 0 or repeats <= -1:
                repeats -= 1
                # TODO (fabawi): communicate with proxy broker to check whether publisher exists
                connected = True
                if connected:
                    logging.info(f"Connected to input port: {port}")
                    break
                time.sleep(0.2)
        return connected

    def read_port(self, port):
        while True:
            obj = port.read(shouldWait=False)
            if self.should_wait and obj is None:
                time.sleep(0.005)
            else:
                return obj


@Listeners.register("NativeObject", "zeromq")
class ZeroMQNativeObjectListener(ZeroMQListener):

    def __init__(self, name, in_port, carrier="tcp", **kwargs):
        super().__init__(name, in_port, carrier=carrier, **kwargs)
        self._json_object_hook = JsonDecodeHook(**kwargs).object_hook
        self._port = self._netconnect = None
        if not self.should_wait:
            ListenerWatchDog().add_listener(self)

    def establish(self, repeats=None, **kwargs):
        established = self.await_connection(repeats=repeats)
        if established:
            self._port = zmq.Context.instance().socket(zmq.SUB)
            self._port.connect(self.socket_address)
            self._topic = self.in_port.encode("utf-8")
            self._port.setsockopt_string(zmq.SUBSCRIBE, self.in_port)

        return self.check_establishment(established)

    def listen(self):
        if not self.established:
            established = self.establish()
            if not established:
                return None
        if self._port.poll(timeout=None if self.should_wait else 0):
            obj = self._port.recv_multipart()
            return json.loads(obj[1].decode(), object_hook=self._json_object_hook) if obj is not None else None
        else:
            return None


# @Listeners.register("Image", "zeromq")
# class ZeroMQImageListener(ZeroMQListener):
#
#     def __init__(self, name, in_port, carrier="", width=-1, height=-1, rgb=True, fp=False, **kwargs):
#         super().__init__(name, in_port, carrier=carrier, **kwargs)
#         self.width = width
#         self.height = height
#         self.rgb = rgb
#         self.fp = fp
#         self._port = self._type = self._netconnect = None
#         if not self.should_wait:
#             ListenerWatchDog().add_listener(self)
#
#     def establish(self, repeats=None, **kwargs):
#         established = self.await_connection(repeats=repeats)
#         if established:
#             if self.rgb:
#                 self._port = yarp.BufferedPortImageRgbFloat() if self.fp else yarp.BufferedPortImageRgb()
#             else:
#                 self._port = yarp.BufferedPortImageFloat() if self.fp else yarp.BufferedPortImageMono()
#             self._type = np.float32 if self.fp else np.uint8
#             in_port_connect = f"{self.in_port}:in{np.random.randint(100000, size=1).item()}"
#             self._port.open(in_port_connect)
#             self._netconnect = yarp.Network.connect(self.in_port, in_port_connect, self.carrier)
#         return self.check_establishment(established)
#
#     def listen(self):
#         if not self.established:
#             established = self.establish()
#             if not established:
#                 return None
#         yarp_img = self.read_port(self._port)
#         if yarp_img is None:
#             return None
#         elif 0 < self.width != yarp_img.width() or 0 < self.height != yarp_img.height():
#             raise ValueError("Incorrect image shape for listener")
#         if self.rgb:
#             img = np.zeros((yarp_img.height(), yarp_img.width(), 3), dtype=self._type, order='C')
#             wrapper_img = yarp.ImageRgbFloat() if self.fp else yarp.ImageRgb()
#         else:
#             img = np.zeros((yarp_img.height(), yarp_img.width()), dtype=self._type, order='C')
#             wrapper_img = yarp.ImageFloat() if self.fp else yarp.ImageMono()
#         wrapper_img.resize(img.shape[1], img.shape[0])
#         wrapper_img.setExternal(img, img.shape[1], img.shape[0])
#         wrapper_img.copy(yarp_img)
#         return img
#
#     def close(self):
#         if self._port:
#             self._port.close()
#
#     def __del__(self):
#         self.close()
#
#
# @Listeners.register("AudioChunk", "zeromq")
# class ZeroMQAudioChunkListener(ZeroMQImageListener):
#
#     def __init__(self, name, in_port, carrier="", channels=1, rate=44100, chunk=-1, **kwargs):
#         super().__init__(name, in_port, carrier=carrier, width=chunk, height=channels, rgb=False, fp=True, **kwargs)
#         self.channels = channels
#         self.rate = rate
#         self.chunk = chunk
#         self._dummy_sound = self._dummy_port = self._dummy_netconnect = None
#         if not self.should_wait:
#             ListenerWatchDog().add_listener(self)
#
#     def establish(self, repeats=None, **kwargs):
#         established = self.await_connection(port=self.in_port + "_SND", repeats=repeats)
#         if established:
#             # create a dummy sound object for transmitting the sound props. This could be cleaner but left for future impl.
#             rnd_id = str(np.random.randint(100000, size=1)[0])
#             self._dummy_port = yarp.Port()
#             self._dummy_port.open(self.in_port + "_SND:in" + rnd_id)
#             self._dummy_netconnect = yarp.Network.connect(self.in_port + "_SND", self.in_port + "_SND:in" + rnd_id, self.carrier)
#         established = self.check_establishment(established)
#         established_parent = super(YarpAudioChunkListener, self).establish(repeats=repeats)
#         if established_parent:
#             self._dummy_sound = yarp.Sound()
#             # self._dummy_port.read(self._dummy_sound)
#             # self.rate = self._dummy_sound.getFrequency()
#             # self.width = self.chunk = self._dummy_sound.getSamples()
#             # self.height = self.channels = self._dummy_sound.getChannels()
#         return established
#
#     def listen(self):
#         return super().listen(), self.rate
#
#     def close(self):
#         super().close()
#         if self._dummy_port:
#             self._dummy_port.close()
#
#
# @Listeners.register("Properties", "zeromq")
# class ZeroMQPropertiesListener(ZeroMQListener):
#     def __init__(self, name, in_port, **kwargs):
#         super().__init__(name, in_port, **kwargs)
#         raise NotImplementedError
