import cv2
from datetime import datetime
import os
from threading import Thread
import time
import argparse

# set up all the arg parsing stuff
ap = argparse.ArgumentParser()

ap.add_argument("-wi", "--width", required=False,
                help="Specify the width of the image the should be captured e.g. 1920/640. Default: 1920", type=int, default=1920)

ap.add_argument("-he", "--height", required=False,
                help="Specify the height of the image the should be captured e.g. 1080/480. Default: 1080", type=int, default=1080)
ap.add_argument("-ir", "--infrared", required=False,
                help="Specify whether the script saves the ir images or not. Default: True",  type=bool, default=True)
ap.add_argument("-fps", "--framerate", required=False,
                help="Specify what framerate to use. Default: 5",  type=int, default=5)
ap.add_argument("-du", "--duration", required=False,
                help="Specify for how long (in seconds) the script captures images Default: 15",  type=int, default=15)

# left cam is dev 0
left_cam = '/dev/video0'
right_cam = '/dev/video2'

# turn the args into an array
args = vars(ap.parse_args())


def ir_capturing(path):
    # use the command seek_test to capture and write the ir image
    end = time.time() + args['duration']
    while time.time() < end:
        file_name = str(datetime.now()).replace(' ', '_')
        os.system('seek_test ' + path + file_name)


def capture_col_image(left_cam, right_cam, path_left, path_right):
    os.system('yes | ffmpeg -thread_queue_size 128 -f v4l2 -framerate {} -vcodec mjpeg -video_size {}x{} -i {} -t {}  -thread_queue_size 128 -f v4l2 -framerate {} -vcodec mjpeg -video_size {}x{} -i {} -t {} -map 0 {}video.avi -map 1 {}video.avi'.format(
        args['framerate'], args['width'], args['height'], left_cam, args['duration'], args['framerate'], args['width'], args['height'], right_cam, args['duration'], path_left, path_right))
    print('started to saved colored images')


data_path = '/home/jetson/2019-johannes-vitt-bsc-thesis/data/images/'

directory_name = str(datetime.now())
directory_name = directory_name.replace(' ', '_')
os.mkdir(data_path + directory_name)
os.mkdir(data_path + directory_name + '/col_cam_1/')
os.mkdir(data_path + directory_name + '/col_cam_2/')
os.mkdir(data_path + directory_name + '/ir_cam_1/')

# write the settings of the camera
f = open("{}/settings.txt".format(data_path + directory_name), "a")
# write the resolution
f.write('{},{}\n'.format(args['width'], args['height']))
# write the fps
f.write('{}'.format(args['framerate']))

file_name = str(datetime.now()).replace(' ', '_')
col_thread = Thread(target=capture_col_image, args=(left_cam, right_cam,
                                                    data_path + directory_name + '/col_cam_1/', data_path + directory_name + '/col_cam_2/'))
ir_capture_thread = Thread(target=ir_capturing, args=[
    data_path + directory_name + '/ir_cam_1/'])

col_thread.start()
if args['infrared']:
    ir_capture_thread.start()
