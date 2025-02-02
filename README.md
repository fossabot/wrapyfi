<p align="center">
  <img width="460" height="300" src="https://raw.githubusercontent.com/fabawi/wrapyfi/main/assets/wrapyfi.png">
</p>


<hl/>


[![webpage](https://custom-icon-badges.demolab.com/badge/Page-blue.svg?logo=globe&logoColor=white)](https://www.inf.uni-hamburg.de/en/inst/ab/wtm/research/software.html#wrapyfi "webpage link")
[![paper](https://custom-icon-badges.demolab.com/badge/Paper-blue.svg?logo=paper_sheet&logoColor=white)](https://www2.informatik.uni-hamburg.de/wtm/publications/2024/AAFW24/Abawi_HRI24.pdf "paper link")
[![arXiv](https://custom-icon-badges.demolab.com/badge/arXiv:2302.09648-lightyellow.svg?logo=arxiv-logomark-small)](https://arxiv.org/abs/2302.09648 "arXiv link")
[![doi](https://custom-icon-badges.demolab.com/badge/10.1145/3610977.3637471-lightyellow.svg?logo=doi_logo)](https://doi.org/10.1145/3610977.3637471 "doi link")
[![FOSSA Status](https://app.fossa.com/api/projects/git%2Bgithub.com%2Fmodular-ml%2Fwrapyfi.svg?type=shield)](https://app.fossa.com/projects/git%2Bgithub.com%2Fmodular-ml%2Fwrapyfi?ref=badge_shield)

[![researchgate](https://custom-icon-badges.demolab.com/badge/ResearchGate-white.svg?logo=researchgate)](https://www.researchgate.net/publication/376582189_Wrapyfi_A_Python_Wrapper_for_Integrating_Robots_Sensors_and_Applications_across_Multiple_Middleware "researchgate link")
[![paperswithcode](https://custom-icon-badges.demolab.com/badge/Papers%20With%20Code-white.svg?logo=paperwithcode)](https://cs.paperswithcode.com/paper/wrapyfi-a-wrapper-for-message-oriented-and "paperswithcode link")
[![modularml](https://custom-icon-badges.demolab.com/badge/Modular%20ML-white.svg?logo=modularml)](https://modular.ml/#wrap "modularml link")

[![License](https://custom-icon-badges.demolab.com/github/license/denvercoder1/custom-icon-badges?logo=law&logoColor=white)](https://github.com/fabawi/wrapyfi/blob/main/LICENSE "license MIT")
[![Documentation Status](https://readthedocs.org/projects/wrapyfi/badge/?version=latest)](https://wrapyfi.readthedocs.io/en/latest/?badge=latest)
[![PyPI version](https://badge.fury.io/py/wrapyfi.svg)](https://badge.fury.io/py/wrapyfi)

Wrapyfi is a middleware communication wrapper for transmitting data across nodes, without 
altering the operation pipeline of your Python scripts. Wrapyfi introduces
a number of helper functions to make middleware integration possible without the need to learn an entire framework, just to parallelize your processes on 
multiple machines. 
Wrapyfi supports [YARP](https://www.yarp.it/yarp_swig.html), [ROS](http://wiki.ros.org/rospy), [ROS 2](https://docs.ros2.org/foxy/api/rclpy/index.html), and [ZeroMQ](http://zeromq.org/).

To integrate Wrapyfi with your scripts, add the decorators describing the transmitting and listening method parameters.

# Attribution

Please refer to the following [paper](https://www2.informatik.uni-hamburg.de/wtm/publications/2024/AAFW24/Abawi_HRI24.pdf) when citing Wrapyfi in academic work:

```
@inproceedings{abawi2024wrapyfi,
  title = {Wrapyfi: A Python Wrapper for Integrating Robots, Sensors, and Applications across Multiple Middleware},
  author = {Abawi, Fares and Allgeuer, Philipp and Fu, Di and Wermter, Stefan},
  booktitle = {Proceedings of the ACM/IEEE Conference on Human-Robot Interaction (HRI '24)},
  year = {2024},
  organization = {ACM},
  isbn = {79-8-4007-0322-5},
  doi = {10.1145/3610977.3637471},
  url = {https://github.com/fabawi/wrapyfi}
}
```

# Getting Started

Before using Wrapyfi, YARP, ROS, or ZeroMQ must be installed.

* Follow the [YARP installation guide](https://github.com/fabawi/wrapyfi/tree/main/wrapyfi_extensions/yarp/README.md?rank=0).<!-- [YARP installation guide](docs/yarp_install_lnk.md). -->
Note that the iCub package is not needed for Wrapyfi to work and does not have to be installed if you do not intend on using the iCub robot.

* For installing ROS, follow the [ROS installation guide](http://wiki.ros.org/noetic/Installation/Ubuntu). 
We recommend installing ROS on Conda using the [RoboStack](https://github.com/RoboStack/ros-noetic) environment. Additionally, the 
Wrapyfi [ROS interfaces](https://github.com/modular-ml/wrapyfi_ros_interfaces/blob/master/README.md?rank=0) must be
built to support messages needed for audio transmission.

* For installing ROS 2, follow the [ROS 2 installation guide](https://docs.ros.org/en/humble/Installation/Ubuntu-Install-Debians.html). 
We recommend installing ROS 2 on Conda using the [RoboStack](https://github.com/RoboStack/ros-humble) environment. Additionally, the 
Wrapyfi [ROS 2 interfaces](https://github.com/modular-ml/wrapyfi_ros2_interfaces/blob/master/README.md?rank=0) must be
built to support messages and services needed for audio transmission and the REQ/REP pattern support.

* ZeroMQ can be installed using pip: `pip install pyzmq`. 
The xpub-xsub pattern followed in our ZeroMQ implementation requires a proxy broker. A broker is spawned by default as a daemon process.
To avoid automatic spawning, pass the argument `start_proxy_broker=False` to the method register decorator. 
A standalone broker can be found [here](https://github.com/fabawi/wrapyfi/tree/main/wrapyfi/standalone/zeromq_proxy_broker.py)


#### Compatibility
* Ubuntu >= 18.04 (Not tested with earlier versions of Ubuntu or other OS)
* Python >= 3.6
* OpenCV >= 4.2
* Numpy >= 1.19


* YARP >= v3.3.2 
* ROS Noetic Ninjemys
* ROS 2 Humble Hawksbill **|** Galactic Geochelone **|** Foxy Fitzroy 
* PyZMQ 16.0, 17.1 and 19.0


## Installation

You can install Wrapyfi with **pip** or from source.

### Pip

To install all the necessary components for the majority of common uses of Wrapyfi (e.g., NativeObject, Image, Audio, etc.) using **pip**, this process installs both Wrapyfi and its dependencies, like NumPy and OpenCV (`opencv-contrib-python`, `opencv-headless`, and `opencv-python` are supported), that are essential for various workloads, along with ZeroMQ being the default middleware. This option is the best for users running Wrapyfi out of the box in a newly created environment (without any middleware installed beforehand), installing `numpy`, `opencv-contrib-python` and `pyzmq`:

```
pip install wrapyfi[all]
```

*Note that most plugins require additional dependencies and should be installed separately.*

Other middleware such as ROS are environment-specific and require dependencies that cannot be installed using pip. 
Wrapyfi **could** and should be used within such environments with minimal requirements to avoid conflicts with existing NumPy and OpenCV packages:

```
pip install wrapyfi
```

### Source (Pip)

Clone this repository:

```
git clone --recursive https://github.com/fabawi/wrapyfi.git
cd wrapyfi
```

You can choose to install minimal dependencies, for running a basic Wrapyfi script:

```
pip install .[all]
```

or install wrapyfi *without* NumPy, OpenCV, and ZeroMQ:

```
pip install .
```

## Usage

Wrapyfi supports two patterns of communication: 
* **Publisher-Subscriber** (PUB/SUB): A publisher sends data to a subscriber accepting arguments and executing methods on the publisher's end.
e.g., with YARP


<table>
<tr>
<th> Without Wrapyfi </th>
<th> With Wrapyfi </th>
</tr>
<tr>
<td>
<sub style="white-space: pre-wrap;">

```python
# Just your usual Python class


class HelloWorld(object):
    
    
    
    
    def send_message(self):
        msg = input("Type your message: ")
        obj = {"message": msg}
        return obj,


hello_world = HelloWorld()



    

while True:
    my_message, = hello_world.send_message()
    print(my_message)
```
    
</sub>
</td>
<td>
<sub style="white-space: pre-wrap;">

```python
from wrapyfi.connect.wrapper import MiddlewareCommunicator


class HelloWorld(MiddlewareCommunicator):
    @MiddlewareCommunicator.register("NativeObject", "yarp",
                                     "HelloWorld", 
                                     "/hello/my_message", 
                                     carrier="", should_wait=True)
    def send_message(self):
        msg = input("Type your message: ")
        obj = {"message": msg}
        return obj,


hello_world = HelloWorld()

LISTEN = True
mode = "listen" if LISTEN else "publish"
hello_world.activate_communication(hello_world.send_message, mode=mode)

while True:
    my_message, = hello_world.send_message()
    print(my_message)
```
    
</sub>
</td>
</tr>
</table>

Run `yarpserver` from the command line. Now execute the Python script above (with Wrapyfi) twice setting `LISTEN = False` and `LISTEN = True`. You can now type with the publisher's command line and preview the message within the listener's


* **Request-Reply** (REQ/REP): A requester sends a request to a responder, which responds to the request in a synchronous manner.
e.g., with ROS

<table>
<tr>
<th> Without Wrapyfi </th>
<th> With Wrapyfi </th>
</tr>
<tr>
<td>
<sub style="white-space: pre-wrap;">

```python
# Just your usual Python class


class HelloWorld(object):
    
    
    
    
    def send_message(self, a, b):
        msg = input("Type your message: ")
        obj = {"message": msg, 
               "a": a, "b": b, "sum": a + b}
        return obj,


hello_world = HelloWorld()



    

while True:
    my_message, = hello_world.send_message(a=1, 
                                           b=2)
    print(my_message)
```
    
</sub>
</td>
<td>
<sub style="white-space: pre-wrap;">

```python
from wrapyfi.connect.wrapper import MiddlewareCommunicator


class HelloWorld(MiddlewareCommunicator):
    @MiddlewareCommunicator.register("NativeObject", "ros",
                                     "HelloWorld", 
                                     "/hello/my_message", 
                                     carrier="", should_wait=True)
    def send_message(self, a, b):
        msg = input("Type your message: ")
        obj = {"message": msg, 
               "a": a, "b": b, "sum": a + b}
        return obj,


hello_world = HelloWorld()

LISTEN = True
mode = "request" if LISTEN else "reply"
hello_world.activate_communication(hello_world.send_message, mode=mode)

while True:
    my_message, = hello_world.send_message(a=1 if LISTEN else None, 
                                           b=2 if LISTEN else None)
    print(my_message)
```
    
</sub>
</td>
</tr>
</table>




Run `roscore` from the command line. Now execute the Python script above (with Wrapyfi) twice setting `LISTEN = False` and `LISTEN = True`. You can now type within the server's command line and preview the message within the client's. 
Note that the server's command line will not show the message until the client's command line has been used to send a request. The arguments are passed from the client to the server and the server's response is passed back to the client.

For more examples of usage, refer to the [user guide](docs/usage.md). Run scripts in the [examples directory](https://github.com/fabawi/wrapyfi/tree/main/examples) for trying out Wrapyfi. 

# Supported Formats

## Middleware
* [x] **YARP**
* [x] **ROS**
* [x] **ROS 2**
* [x] **ZeroMQ** (beta feature: `should_wait` trigger introduced with event monitoring)


## Serializers
* [x] **JSON**
* [ ] **msgpack**
* [ ] **protobuf**

## Data Structures

Supported Objects by the `NativeObject` type include:

* [x] [**Numpy Array|Generic**](https://numpy.org/doc/1.23/)
* [x] [**Pytorch Tensor**](https://pytorch.org/docs/stable/index.html)
* [x] [**Tensorflow 2 Tensor**](https://www.tensorflow.org/api_docs/python/tf)
* [x] [**JAX Tensor**](https://jax.readthedocs.io/en/latest/)
* [x] [**MXNet Tensor**](https://mxnet.apache.org/versions/1.9.1/api/python.html)
* [x] [**Paddlepaddle Tensor**](https://www.paddlepaddle.org.cn/documentation/docs/en/guides/index_en.html)
* [x] [**pandas DataFrame|Series**](https://pandas.pydata.org/docs/)
* [x] [**Pillow Image**](https://pillow.readthedocs.io/en/stable/reference/Image.html)
* [x] [**PyArrow Array**](https://arrow.apache.org/docs/python/index.html)
* [x] [**Xarray DataArray|Dataset**](http://xarray.pydata.org/en/stable/)
* [x] [**Dask Array|DataFrame**](https://www.dask.org/get-started)
* [x] [**Zarr Array|Group**](https://zarr.readthedocs.io/en/stable/)
* [x] [**Pint Quantity**](https://pint.readthedocs.io/en/stable/)
* [ ] [**pandas 2.0 DataFrame|Series**](https://pandas.pydata.org/docs/)
* [ ] [**Gmpy 2 MPZ**](https://gmpy2.readthedocs.io/en/latest/) 

## Image

Supported Objects by the `Image` type include:

* [x] **Numpy Array** (supports many libraries including [scikit-image](https://scikit-image.org/), [imageio](https://imageio.readthedocs.io/en/stable/), [Open CV](https://opencv.org/), [imutils](https://github.com/PyImageSearch/imutils), [matplotlib.image](https://matplotlib.org/stable/api/image_api.html), and [Mahotas](https://mahotas.readthedocs.io/en/latest/))

## Sound 

Supported Objects by the `AudioChunk` type include:

* [x] **Numpy Array**,int (supports the [sounddevice](https://python-sounddevice.readthedocs.io/en/0.4.5/) format)




## License
[![FOSSA Status](https://app.fossa.com/api/projects/git%2Bgithub.com%2Fmodular-ml%2Fwrapyfi.svg?type=large)](https://app.fossa.com/projects/git%2Bgithub.com%2Fmodular-ml%2Fwrapyfi?ref=badge_large)