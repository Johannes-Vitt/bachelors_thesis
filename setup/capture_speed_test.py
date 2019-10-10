import cv2
from datetime import datetime
import time
import argparse

# set up all the arg parsing stuff
ap = argparse.ArgumentParser()

ap.add_argument("-w", "--width", required=False,
                help="Specify the width of the image the should be captured e.g. 1920/640. Default: 1920", type=int, default=1920)

ap.add_argument("-h", "--height", required=False,
                help="Specify the height of the image the should be captured e.g. 1080/480. Default: 1080", type=int, default=1080)

ap.add_argument("-s", "--save", required=False,
                help="Specify whether the captured iamges should be saved or not. Default: True",  type=bool, default=True)

# turn the args into an array
args = vars(ap.parse_args())


# Note: the numbering of the devices in /dev/ might be different every time, therefore one does not know which cam is 'left' or 'right'
cam_1 = cv2.VideoCapture(0)
# also initialize the second cam
cam_2 = cv2.VideoCapture(2)
time.wait(4)

# set the size of the frame and set the MJPEG mode for best frame rate
cam_1.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
cam_1.set(cv2.CAP_PROP_FRAME_WIDTH, args['width'])
cam_1.set(cv2.CAP_PROP_FRAME_HEIGHT, args['height'])

cam_2.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
cam_2.set(cv2.CAP_PROP_FRAME_WIDTH, args['width'])
cam_2.set(cv2.CAP_PROP_FRAME_HEIGHT, args['height'])


data_path = '/home/jetson/2019-johannes-vitt-bsc-thesis/data/images/'

directory_name = str(datetime.now())
directory_name = directory_name.replace(' ', '_')
os.mkdir(data_path + directory_name)
os.mkdir(data_path + directory_name + '/col_cam_1/')
os.mkdir(data_path + directory_name + '/col_cam_2/')
os.mkdir(data_path + directory_name + '/ir_cam_1/')

start_time = datetime.now()
frame_counter = 0
while True:

    _, frame_1 = cam_1.read()
    _, frame_2 = cam_2.read()
    current_time = datetime.now()

    frame_counter += 1
    time_difference = current_time - start_time

    datetime_start = datetime.datetime.combine(
        datetime.date.today(), start_time)
    datetime_current = datetime.datetime.combine(
        datetime.date.today(), current_time)

    time_difference = (datetime_start - datetime_current).totalSeconds()

    print('fps: {}'.format(frame_counter / time_difference))
