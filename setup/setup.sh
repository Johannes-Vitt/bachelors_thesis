#!/bin/bash
#
# script installs OpenCV 4.0.0 and newest tensorflow on a fresh Jetson Nano
#
# OpenCV parts from: https://github.com/AastaNV/JEP/blob/master/script/install_opencv4.0.0_Nano.sh
# Tensorflow parts from: https://docs.nvidia.com/deeplearning/frameworks/install-tf-jetson-platform/index.html

if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <Install Folder> <Password>. \nNote: you have to be in the root of the git repo for this script to work!"
    exit
fi
folder="$1"
user="jetson"
passwd="$2"

#install dependencies for tensorflow
sudo apt-get install libhdf5-serial-dev hdf5-tools libhdf5-dev zlib1g-dev zip libjpeg8-dev
sudo apt-get install python3-pip
sudo pip3 install -U pip
sudo pip3 install -U numpy grpcio absl-py py-cpuinfo psutil portpicker six mock requests gast h5py astor termcolor protobuf keras-applications keras-preprocessing wrapt google-pasta setuptools testresources

#install the latest version of tensorflow 
sudo pip3 install --pre --extra-index-url https://developer.download.nvidia.com/compute/redist/jp/v42 tensorflow-gpu

#install OpenCV ans all dependencies

echo "** Remove OpenCV3.3 first"
sudo sudo apt-get purge *libopencv*

echo "** Install requirement"
sudo apt-get update
sudo apt-get install -y build-essential cmake git libgtk2.0-dev pkg-config libavcodec-dev libavformat-dev libswscale-dev
sudo apt-get install -y libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev
sudo apt-get install -y python2.7-dev python3.6-dev python-dev python-numpy python3-numpy
sudo apt-get install -y libtbb2 libtbb-dev libjpeg-dev libpng-dev libtiff-dev libjasper-dev libdc1394-22-dev
sudo apt-get install -y libv4l-dev v4l-utils qv4l2 v4l2ucp
sudo apt-get install -y curl
sudo apt-get update

echo "** Download opencv-4.0.0"
cd $folder
curl -L https://github.com/opencv/opencv/archive/4.0.0.zip -o opencv-4.0.0.zip
curl -L https://github.com/opencv/opencv_contrib/archive/4.0.0.zip -o opencv_contrib-4.0.0.zip
unzip opencv-4.0.0.zip 
unzip opencv_contrib-4.0.0.zip 
cd opencv-4.0.0/

echo "** Building..."
mkdir release
cd release/
cmake -D WITH_CUDA=ON -D CUDA_ARCH_BIN="5.3" -D CUDA_ARCH_PTX="" -D OPENCV_EXTRA_MODULES_PATH=../../opencv_contrib-4.0.0/modules -D WITH_GSTREAMER=ON -D WITH_LIBV4L=ON -D BUILD_opencv_python2=ON -D BUILD_opencv_python3=ON -D BUILD_TESTS=OFF -D BUILD_PERF_TESTS=OFF -D BUILD_EXAMPLES=OFF -D CMAKE_BUILD_TYPE=RELEASE -D CMAKE_INSTALL_PREFIX=/usr/local ..
make -j3
sudo make install

echo "** Install opencv-4.0.0 (hopefully) successfully"

# set PYTHONPATH correctly to make opencv work with python
echo "export PYTHONPATH=\"${PYTHONPATH}:/usr/local/python\"" >> ~/.bashrc

# install idle 
sudo apt-get install idle3

#befor intalling libseek we need to download libboost
sudo apt-get install libboost-program-options-dev

# also install libseek (the library for running the ir cam)
cd libseek-thermal/libseek-thermal-master
mkdir build
cd build
cmake ../
make
sudo make install
sudo ldconfig
# add a udev rule for the ir cam
# the bash -c option is necessary because sudo echo does not work, e.g. echo rejects writing to a protected enviroment evenbefore sudoing
sudo bash -c 'echo "SUBSYSTEM==\"usb\", ATTRS{idVendor}==\"289d\", ATTRS{idProduct}==\"0010\", MODE=\"0666\", GROUP=\"users\"" >> /etc/udev/rules.d/99-seek-thermal-ir-cam.rules'

# we also need to add the canberra gtk module
sudo apt install libcanberra-gtk-module libcanberra-gtk3-module

# install imutils
sudo pip install imutils

echo "** Bye :)"