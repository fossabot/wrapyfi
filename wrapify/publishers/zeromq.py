import logging
import json
import time

import numpy as np
import zmq
import imagezmq

from wrapify.connect.publishers import Publisher, Publishers, PublisherWatchDog
from wrapify.middlewares.zeromq import ZeroMQMiddleware
from wrapify.encoders import JsonEncoder


class ZeroMQPublisher(Publisher):
    def __init__(self, name, out_port, carrier="tcp", out_port_connect=None,
                 socket_ip="127.0.0.1", socket_port=5555, socket_sub_port=5556,
                 start_proxy_broker=True, proxy_broker_spawn="process", proxy_broker_verbose=False, **kwargs):
        carrier = carrier if carrier else "tcp"
        super().__init__(name, out_port, carrier=carrier, out_port_connect=out_port_connect, **kwargs)
        # out_port is equivalent to topic in zeromq
        # TODO (fabawi): out_port_connect probably not needed, follow ROS approach
        self.socket_address = f"{carrier}://{socket_ip}:{socket_port}"
        self.socket_sub_address = f"{carrier}://{socket_ip}:{socket_sub_port}"
        if start_proxy_broker:
            ZeroMQMiddleware.activate(socket_address=self.socket_address, socket_sub_address=self.socket_sub_address,
                                      proxy_broker_spawn=proxy_broker_spawn, proxy_broker_verbose=proxy_broker_verbose)
        else:
            ZeroMQMiddleware.activate()

    def await_connection(self, port, out_port=None, repeats=None):
        connected = False
        if out_port is None:
            out_port = self.out_port
        logging.info(f"Waiting for output connection: {out_port}")
        if repeats is None:
            if self.should_wait:
                repeats = -1
            else:
                repeats = 1
            while repeats > 0 or repeats <= -1:
                repeats -= 1
                # TODO (fabawi): actually check connection
                connected = True
                # connected = port.getOutputCount() < 1
                if connected:
                    break
                time.sleep(0.02)
        logging.info(f"Output connection established: {out_port}")
        return connected


@Publishers.register("NativeObject", "zeromq")
class ZeroMQNativeObjectPublisher(ZeroMQPublisher):
    """
        The NativeObjectPublisher using the ZMQ message construct assuming a combination of python native objects
        and numpy arrays as input
        """
    def __init__(self, name, out_port, carrier="tcp", out_port_connect=None, **kwargs):
        """
        Initializing the NativeObjectPublisher
        :param name: Name of the publisher
        :param out_port: The published topic name preceded by "/"
        :param carrier: ZMQ currently only supports TCP for pub/sub pattern. Default is "tcp"
        :param out_port_connect: This is an optional port connection for listening devices (follows out_port format)
        """
        super().__init__(name, out_port, carrier=carrier, out_port_connect=out_port_connect, **kwargs)
        self._port = self._netconnect = None
        if not self.should_wait:
            PublisherWatchDog().add_publisher(self)

    def establish(self, repeats=None, **kwargs):
        self._port = zmq.Context.instance().socket(zmq.PUB)
        self._port.connect(self.socket_sub_address)
        self._topic = self.out_port.encode()
        established = self.await_connection(self._port, repeats=repeats)
        return self.check_establishment(established)

    def publish(self, obj):
        if not self.established:
            established = self.establish()
            if not established:
                return
            else:
                time.sleep(0.2)
        obj = json.dumps(obj, cls=JsonEncoder)
        self._port.send_multipart([self._topic, obj.encode()])


@Publishers.register("Image", "zeromq")
class ZeroMQImagePublisher(ZeroMQNativeObjectPublisher):

    def __init__(self, name, out_port, carrier="tcp", out_port_connect=None, width=-1, height=-1, rgb=True, fp=False, **kwargs):
        """
        Initializing the ImagePublisher
        :param name: Name of the publisher
        :param out_port: The published port name preceded by "/"
        :param carrier: ZMQ currently only supports TCP for pub/sub pattern. Default is "tcp"
        :param out_port_connect: This is an optional port connection for listening devices (follows out_port format)
        :param width: Image width
        :param height: Image height
        :param rgb: Transmits an RGB image when "True", or mono image when "False"
        :param fp: Transmits 32-bit floating point image when "True", or 8-bit integer image when "False"
        """
        super().__init__(name, out_port, carrier=carrier, out_port_connect=out_port_connect)
        self.width = width
        self.height = height
        self.rgb = rgb
        self.fp = fp
        self._type = np.float32 if self.fp else np.uint8

    def publish(self, img):
        if not self.established:
            established = self.establish()
            if not established:
                return
            else:
                time.sleep(0.2)
        if 0 < self.width != img.shape[1] or 0 < self.height != img.shape[0] or \
                not ((img.ndim == 2 and not self.rgb) or (img.ndim == 3 and self.rgb and img.shape[2] == 3)):
            raise ValueError("Incorrect image shape for publisher")
        if not img.flags['C_CONTIGUOUS']:
            img = np.ascontiguousarray(img)
        img = json.dumps(img, cls=JsonEncoder)
        self._port.send_multipart([self._topic, img.encode()])


@Publishers.register("AudioChunk", "zeromq")
class ZeroMQAudioChunkPublisher(ZeroMQPublisher):
    """
    Using the ImagePublisher to carry the sound signal. There are better alternatives (Sound) but
    don't seem to work with the python bindings at the moment
    """
    def __init__(self, name, out_port, carrier="tcp", out_port_connect=None, channels=1, rate=44100, chunk=-1, **kwargs):
        """
        Initializing the AudioPublisher
        :param name: Name of the publisher
        :param out_port: The published port name preceded by "/"
        :param carrier: ZMQ currently only supports TCP for pub/sub pattern. Default is "tcp"
        :param out_port_connect: This is an optional port connection for listening devices (follows out_port format)
        :param channels: Number of audio channels
        :param rate: Sampling rate of the audio signal
        :param chunk: Size of the chunk in samples. Transmits 1 second when chunk=rate
        """
        super().__init__(name, out_port, carrier=carrier, out_port_connect=out_port_connect, width=chunk, height=channels, rgb=False, fp=True)
        self.channels = channels
        self.rate = rate
        self.chunk = chunk

    def publish(self, aud):
        if not self.established:
            established = self.establish()
            if not established:
                return
            else:
                time.sleep(0.2)
        chunk, channels = aud.shape[0], aud.shape[1]
        if 0 < self.chunk != chunk or self.channels != channels or len(aud) != chunk * channels * 4:
            raise ValueError("Incorrect audio shape for publisher")
        if not aud.flags['C_CONTIGUOUS']:
            aud = np.ascontiguousarray(aud)
        aud = json.dumps(aud, cls=JsonEncoder)
        self._port.send_multipart([self._topic, aud.encode()])


@Publishers.register("Properties", "zeromq")
class ZeroMQPropertiesPublisher(ZeroMQPublisher):

    def __init__(self, name, out_port, **kwargs):
        super().__init__(name, out_port, **kwargs)
        raise NotImplementedError
