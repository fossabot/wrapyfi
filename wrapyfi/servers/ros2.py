import logging
import sys
import json
import time
import threading
import os
import importlib.util
import queue
from typing import Optional

import numpy as np
import cv2
import rclpy
from rclpy.node import Node
import std_msgs.msg
import sensor_msgs.msg

from wrapyfi.connect.servers import Server, Servers
from wrapyfi.middlewares.ros2 import ROS2Middleware
from wrapyfi.encoders import JsonEncoder, JsonDecodeHook


class ROS2Server(Server, Node):

    def __init__(self, name: str, out_topic: str, ros2_kwargs: Optional[dict] = None, **kwargs):
        """
        Initialize the server

        :param name: str: Name of the server
        :param out_topic: str: Name of the input topic preceded by '/' (e.g. '/topic')
        :param ros2_kwargs: dict: Additional kwargs for the ROS2 middleware
        :param kwargs: dict: Additional kwargs for the server
        """
        carrier = "tcp"
        if "carrier" in kwargs and kwargs["carrier"] not in ["", None]:
            logging.warning(
                "[ROS2] ROS2 currently does not support explicit carrier setting for REQ/REP pattern. Using TCP.")
        if "carrier" in kwargs:
            del kwargs["carrier"]

        ROS2Middleware.activate(**ros2_kwargs or {})
        Server.__init__(self, name, out_topic, carrier=carrier, **kwargs)
        Node.__init__(self, name + str(hex(id(self))))

    def close(self):
        """
        Close the server
        """
        if hasattr(self, "_server") and self._server:
            if self._server is not None:
                self.destroy_node()
        if hasattr(self, "_background_callback") and self._background_callback:
            if self._background_callback is not None:
                self._background_callback.join()

    def __del__(self):
        self.close()


@Servers.register("NativeObject", "ros2")
class ROS2NativeObjectServer(ROS2Server):
    SEND_QUEUE = queue.Queue(maxsize=1)
    RECEIVE_QUEUE = queue.Queue(maxsize=1)

    def __init__(self, name: str, out_topic: str,
                 serializer_kwargs: Optional[dict] = None, deserializer_kwargs: Optional[dict] = None, **kwargs):
        """
        Specific server handling native Python objects, serializing them to JSON strings for transmission

        :param name: str: Name of the server
        :param out_topic: str: Name of the input topic preceded by '/' (e.g. '/topic')
        :param serializer_kwargs: dict: Additional kwargs for the serializer
        :param deserializer_kwargs: dict: Additional kwargs for the deserializer
        :param kwargs: Additional kwargs for the server
        """
        super().__init__(name, out_topic, **kwargs)
        self._plugin_encoder = JsonEncoder
        self._plugin_kwargs = kwargs
        self._serializer_kwargs = serializer_kwargs or {}
        self._plugin_decoder_hook = JsonDecodeHook(**kwargs).object_hook
        self._deserializer_kwargs = deserializer_kwargs or {}

        self._server = None

    def establish(self):
        """
        Establish the connection to the server
        """
        try:
            from wrapyfi_ros2_interfaces.srv import ROS2NativeObjectService
        except ImportError:
            import wrapyfi
            logging.error("[ROS2] Could not import ROS2NativeObjectService. "
                          "Make sure the ROS2 services in wrapyfi_extensions/wrapyfi_ros2_interfaces are compiled. "
                          "Refer to the documentation for more information: \n" +
                          wrapyfi.__url__ + "wrapyfi_extensions/wrapyfi_ros2_interfaces/README.md")
            sys.exit(1)

        self._server = self.create_service(ROS2NativeObjectService, self.out_topic, self._service_callback)

        self._req_msg = ROS2NativeObjectService.Request()
        self._rep_msg = ROS2NativeObjectService.Response()
        self.established = True

    def await_request(self, *args, **kwargs):
        """
        Await and deserialize the client's request, returning the extracted arguments and keyword arguments.
        The method blocks until a message is received, then attempts to deserialize it using the configured JSON decoder
        hook, returning the extracted arguments and keyword arguments

        :return: Tuple[list, dict]: A tuple containing two items:
                 - A list of arguments extracted from the received message
                 - A dictionary of keyword arguments extracted from the received message
        """
        if not self.established:
            self.establish()
        try:
            self._background_callback = threading.Thread(name='ros2_server', target=rclpy.spin_once,
                                                         args=(self,), kwargs={})
            self._background_callback.setDaemon(True)
            self._background_callback.start()

            request = ROS2NativeObjectServer.RECEIVE_QUEUE.get(block=True)
            [args, kwargs] = json.loads(request.request, object_hook=self._plugin_decoder_hook, **self._deserializer_kwargs)
            return args, kwargs
        except Exception as e:
            logging.error("[ROS2] Service call failed %s" % e)
            return [], {}

    @staticmethod
    def _service_callback(request, _response):
        """
        Callback for the ROS2 service

        :param request: ROS2NativeObjectService.Request: The request message
        :param _response: ROS2NativeObjectService.Response: The response message
        """
        ROS2NativeObjectServer.RECEIVE_QUEUE.put(request)
        return ROS2NativeObjectServer.SEND_QUEUE.get(block=True)

    def reply(self, obj):
        """
        Serialize the provided Python object to a JSON string and send it as a reply to the client.
        The method uses the configured JSON encoder for serialization before sending the resultant string to the client

        :param obj: Any: The Python object to be serialized and sent
        """
        try:
            obj_str = json.dumps(obj, cls=self._plugin_encoder, **self._plugin_kwargs,
                                 serializer_kwrags=self._serializer_kwargs)
            self._rep_msg.response = obj_str
            ROS2NativeObjectServer.SEND_QUEUE.put(self._rep_msg, block=False)
        except queue.Full:
            logging.warning(f"[ROS2] Discarding data because queue is full. "
                            f"This happened due to bad synchronization in {self.__name__}")


@Servers.register("Image", "ros2")
class ROS2ImageServer(ROS2Server):
    SEND_QUEUE = queue.Queue(maxsize=1)
    RECEIVE_QUEUE = queue.Queue(maxsize=1)

    def __init__(self, name: str, out_topic: str,
                 deserializer_kwargs: Optional[dict] = None,
                 width: int = -1, height: int = -1, rgb: bool = True, fp: bool = False, jpg: bool = False, **kwargs):
        """
        Specific server handling native Python objects, serializing them to JSON strings for transmission

        :param name: str: Name of the server
        :param out_topic: str: Name of the input topic preceded by '/' (e.g. '/topic')
        :param deserializer_kwargs: dict: Additional kwargs for the deserializer
        :param width: int: Width of the image. Default is -1 (use the width of the received image)
        :param height: int: Height of the image. Default is -1 (use the height of the received image)
        :param rgb: bool: True if the image is RGB, False if it is grayscale. Default is True
        :param fp: bool: True if the image is floating point, False if it is integer. Default is False
        :param jpg: bool: True if the image should be decompressed from JPG. Default is False
        :param kwargs: Additional kwargs for the server
        """
        super().__init__(name, out_topic, **kwargs)
        self._plugin_encoder = JsonEncoder
        self._plugin_kwargs = kwargs
        self._plugin_decoder_hook = JsonDecodeHook(**kwargs).object_hook
        self._deserializer_kwargs = deserializer_kwargs or {}

        self.width = width
        self.height = height
        self.rgb = rgb
        self.fp = fp
        self.jpg = jpg

        if self.fp:
            self._encoding = '32FC3' if self.rgb else '32FC1'
            self._type = np.float32
        else:
            self._encoding = 'bgr8' if self.rgb else 'mono8'
            self._type = np.uint8
        if self.jpg:
            self._encoding = 'jpeg'
            self._type = np.uint8

        self._server = None

    def establish(self):
        """
        Establish the connection to the server
        """
        try:
            from wrapyfi_ros2_interfaces.srv import ROS2ImageService, ROS2CompressedImageService
        except ImportError:
            import wrapyfi
            logging.error("[ROS2] Could not import ROS2NativeObjectService. "
                          "Make sure the ROS2 services in wrapyfi_extensions/wrapyfi_ros2_interfaces are compiled. "
                          "Refer to the documentation for more information: \n" +
                          wrapyfi.__url__ + "wrapyfi_extensions/wrapyfi_ros2_interfaces/README.md")
            sys.exit(1)
        if self.jpg:
            self._server = self.create_service(ROS2CompressedImageService, self.out_topic, self._service_callback)
            self._req_msg = ROS2CompressedImageService.Request()
            self._rep_msg = ROS2CompressedImageService.Response()
        else:
            self._server = self.create_service(ROS2ImageService, self.out_topic, self._service_callback)
            self._req_msg = ROS2ImageService.Request()
            self._rep_msg = ROS2ImageService.Response()
        self.established = True

    def await_request(self, *args, **kwargs):
        """
        Await and deserialize the client's request, returning the extracted arguments and keyword arguments.
        The method blocks until a message is received, then attempts to deserialize it using the configured JSON decoder
        hook, returning the extracted arguments and keyword arguments

        :return: Tuple[list, dict]: A tuple containing two items:
                 - A list of arguments extracted from the received message
                 - A dictionary of keyword arguments extracted from the received message
        """
        if not self.established:
            self.establish()
        try:
            self._background_callback = threading.Thread(name='ros2_server', target=rclpy.spin_once,
                                                         args=(self,), kwargs={})
            self._background_callback.setDaemon(True)
            self._background_callback.start()

            request = ROS2ImageServer.RECEIVE_QUEUE.get(block=True)
            [args, kwargs] = json.loads(request.request, object_hook=self._plugin_decoder_hook, **self._deserializer_kwargs)
            return args, kwargs
        except Exception as e:
            logging.error("[ROS2] Service call failed %s" % e)
            return [], {}

    @staticmethod
    def _service_callback(request, _response):
        """
        Callback for the ROS2 service

        :param request: ROS2NativeObjectService.Request: The request message
        :param _response: ROS2NativeObjectService.Response: The response message
        """
        ROS2ImageServer.RECEIVE_QUEUE.put(request)
        return ROS2ImageServer.SEND_QUEUE.get(block=True)

    def reply(self, img: np.ndarray):
        """
        Serialize the provided image data and send it as a reply to the client.

        :param img: np.ndarray: Image to send formatted as a cv2 image - np.ndarray[img_height, img_width, channels]

        """
        try:
            if 0 < self.width != img.shape[1] or 0 < self.height != img.shape[0] or \
                    not ((img.ndim == 2 and not self.rgb) or (img.ndim == 3 and self.rgb and img.shape[2] == 3)):
                raise ValueError("Incorrect image shape for publisher")
            img = np.require(img, dtype=self._type, requirements='C')
            img_msg = self._rep_msg.response
            if self.jpg:
                img_msg.header.stamp = rclpy.clock.Clock().now().to_msg()
                img_msg.format = "jpeg"
                img_msg.data = np.array(cv2.imencode('.jpg', img)[1]).tobytes()
            else:
                img_msg.header.stamp = rclpy.clock.Clock().now().to_msg()
                img_msg.height = img.shape[0]
                img_msg.width = img.shape[1]
                img_msg.encoding = self._encoding
                img_msg.is_bigendian = img.dtype.byteorder == '>' or (img.dtype.byteorder == '=' and sys.byteorder == 'big')
                img_msg.step = img.strides[0]
                img_msg.data = img.tobytes()
            self._rep_msg.response = img_msg
            ROS2ImageServer.SEND_QUEUE.put(self._rep_msg, block=False)
        except queue.Full:
            logging.warning(f"[ROS2] Discarding data because queue is full. "
                            f"This happened due to bad synchronization in {self.__name__}")
