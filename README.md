# Bachelor's Thesis
This is the code for an person counting system that was implemented as my bachelor's thesis. 

## Requirements
The system runs on a [NVIDIA Jetson Nano](https://www.nvidia.com/en-us/autonomous-machines/embedded-systems/jetson-nano/), Raspberry Pi clone with an additional GPU. In order to install all the required software you can run the shell script `/setup/setup.sh`. It is advised to add 4 GB of swap memomry before the process as the installation of OpenCV will often fail otherwise.

## Setup
In order to use the system with convolution neural networks, a TensorFlow model is required. It can be optained from the [TensorFlow Object Model Zoo](https://github.com/tensorflow/models/blob/master/research/object_detection/g3doc/detection_model_zoo.md). Then it needs to placed inside a `/tensorflow/` directory. 

## Usage
```
usage: main.py [-h] [-i INPUT] [-vd VIDEO] [-r RIGHT] [-s SAVE_RESULT]
               [-dt DETECTION] [-di DISPLAY] [-dp DISPARITY]

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        if the input images are not provided via the attached
                        cams, the path must be provided here. Note: the path
                        must end with a slash
  -vd VIDEO, --video VIDEO
                        When the provided images from the files are stored as
                        a video set this to true. Default: True
  -r RIGHT, --right RIGHT
                        provide which camera is the right camera (either "0"
                        or "2")
  -s SAVE_RESULT, --save_result SAVE_RESULT
                        should the results of the detection be saved in the
                        directory? Default: "False"
  -dt DETECTION, --detection DETECTION
                        specify the detection method. "HOG" or "CNN" are valid
                        here. Default is "HOG"
  -di DISPLAY, --display DISPLAY
                        enter if the processed image should be displayed by
                        opencv. Enter "True" or "False". Default: "True"
  -dp DISPARITY, --disparity DISPARITY
                        Enter if a disparity image should be computed and
                        displayed. Enter "True" or "False". Default: "False"
```