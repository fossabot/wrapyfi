import json
import queue
import numpy as np
import rospy
import std_msgs.msg
import sensor_msgs.msg

from wrapify.connect.listeners import Listener, ListenerWatchDog, Listeners
from wrapify.middlewares.ros import ROSMiddleware
from wrapify.utils import JsonDecodeHook


class ROSListener(Listener):

    def __init__(self, name, in_port, carrier="", should_wait=True, queue_size=5):
        super().__init__(name, in_port, carrier=carrier, should_wait=should_wait)
        ROSMiddleware.activate()
        self.queue_size = queue_size


@Listeners.register("NativeObject", "ros")
class ROSNativeObjectListener(ROSListener):

    def __init__(self, name, in_port, carrier="", should_wait=True, queue_size=5, load_torch_device=None):
        super().__init__(name, in_port, carrier=carrier, should_wait=should_wait, queue_size=queue_size)
        self._json_object_hook = JsonDecodeHook(torch_device=load_torch_device).object_hook
        self._subscriber = self._queue = None
        ListenerWatchDog().add_listener(self)

    def establish(self):
        self._queue = queue.Queue(maxsize=0 if self.queue_size is None or self.queue_size <= 0 else self.queue_size)
        self._subscriber = rospy.Subscriber(self.in_port, std_msgs.msg.String, callback=self._message_callback)
        self.established = True

    def listen(self):
        if not self.established:
            self.establish()
        try:
            obj_str = self._queue.get(block=self.should_wait)
            return json.loads(obj_str, object_hook=self._json_object_hook)
        except queue.Empty:
            return None

    def _message_callback(self, data):
        try:
            self._queue.put(data.data, block=False)
        except queue.Full:
            print(f"Discarding data because listener queue is full: {self.in_port}")


@Listeners.register("Image", "ros")
class ROSImageListener(ROSListener):

    def __init__(self, name, in_port, carrier="", should_wait=True, width=-1, height=-1, rgb=True, fp=False):
        super().__init__(name, in_port, carrier=carrier, should_wait=should_wait)
        self.width = width
        self.height = height
        self.rgb = rgb
        self.fp = fp
        self._subscriber = self._type = self._queue = None
        if self.fp:
            self._encoding = '32FC3' if self.rgb else '32FC1'
        else:
            self._encoding = 'bgr8' if self.rgb else 'mono8'
        ListenerWatchDog().add_listener(self)

    def establish(self):
        self._queue = queue.Queue(maxsize=0 if self.queue_size is None or self.queue_size <= 0 else self.queue_size)
        self._subscriber = rospy.Subscriber(self.in_port, sensor_msgs.msg.Image, callback=self._message_callback)
        self._type = np.float32 if self.fp else np.uint8
        self.established = True

    def listen(self):
        if not self.established:
            self.establish()
        try:
            height, width, encoding, is_bigendian, data = self._queue.get(block=self.should_wait)
            # TODO: Check height width against expected
            # TODO: Check encoding against expected
            # TODO: Check data length against expected
            # TODO: Convert data to numpy array of required dtype/shape, respecting is_bigendian (required only for fp=true)
            # TODO: Return numpy image
            raise NotImplementedError
        except queue.Empty:
            return None

    def _message_callback(self, data):
        try:
            self._queue.put((data.height, data.width, data.encoding, data.is_bigendian, data.data), block=False)
        except queue.Full:
            print(f"Discarding data because listener queue is full: {self.in_port}")


@Listeners.register("AudioChunk", "ros")
class ROSAudioChunkListener(ROSListener):

    def __init__(self, name, in_port, carrier="", should_wait=True, channels=1, rate=44100, chunk=-1):
        super().__init__(name, in_port, carrier=carrier, should_wait=should_wait)
        self.channels = channels
        self.rate = rate
        self.chunk = chunk
        raise NotImplementedError  # TODO: Adapt ImageListener implementation for Audio chunk (chunk is expected length of array, channels is width)
        ListenerWatchDog().add_listener(self)


@Listeners.register("Properties", "ros")
class ROSPropertiesListener(ROSListener):

    def __init__(self, name, in_port, **kwargs):
        super().__init__(name, in_port, **kwargs)
        raise NotImplementedError
