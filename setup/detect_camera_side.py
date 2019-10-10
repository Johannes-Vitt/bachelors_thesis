import cv2
import numpy as np

THRESHOLD = 5

print('Please cover the lense of the right camera (from the perspective of the camera) with your hand')

cam_1 = cv2.VideoCapture(0)
cam_2 = cv2.VideoCapture(2)
while True:
    # check the average brightness for both cameras, if one is brighter, the other one is covered and therefore must be the right camera
    _, frame_1 = cv2.cvtColor(cam_1.read(), cv2.COLOR_RGB2GRAY)
    _, frame_2 = cv2.cvtColor(cam_2.read(), cv2.COLOR_RGB2GRAY)

    if np.average(frame_1) > np.average(frame_2) + THRESHOLD:
        print('The right camera is dev 2')
        break
    elif np.average(frame_2) > np.average(frame_1) + THRESHOLD:
        print('The right camera is dev 0')
        break
    print('no darker side detected yet...')
