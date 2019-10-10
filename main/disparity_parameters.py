import display
import disparity
import cv2
from matplotlib import pyplot as plt
import numpy as np

# possible parameters
window_size = [9, 11, 13, 15, 17]
#minDisparity = [16,32,48,64,80,96,112,128,144,160,176,192,208,224,240,256]
#maxDisparity = [16,32,48,64,80,96,112,128,144,160,176,192,208,224,240,256]
minDisparity = [0]
maxDisparity = [224, 240, 256]
blockSize = [12, 15, 17]
numDisparities = []

display.init_cams(1)

# path to calibration
path_to_calibration = '/home/jetson/2019-johannes-vitt-bsc-thesis/calibration/'

left_cam = cv2.VideoCapture(
    '/home/jetson/2019-johannes-vitt-bsc-thesis/data/images/2019-09-30_12:46:40.231939/col_cam_1/video.avi')
right_cam = cv2.VideoCapture(
    '/home/jetson/2019-johannes-vitt-bsc-thesis/data/images/2019-09-30_12:46:40.231939/col_cam_2/video.avi')


# frame 0 is the right image
right = cv2.imread(
    '/home/jetson/2019-johannes-vitt-bsc-thesis/data/images/2019-09-18_09:13:19.749703/col_cam_1/2019-09-18_09:13:22.773901.png')
left = cv2.imread(
    '/home/jetson/2019-johannes-vitt-bsc-thesis/data/images/2019-09-18_09:13:19.749703/col_cam_2/2019-09-18_09:13:19.759244.png')

#right = cv2.imread('/home/jetson/2019-johannes-vitt-bsc-thesis/opencv/opencv-4.0.0/samples/data/aloeR.jpg', 0)
#left = cv2.imread('/home/jetson/2019-johannes-vitt-bsc-thesis/opencv/opencv-4.0.0/samples/data/aloeL.jpg', 0)

# write the result to a video file
out = cv2.VideoWriter('output.avi', cv2.VideoWriter_fourcc(
    'M', 'J', 'P', 'G'), 5, (1799, 891))

counter = 0

while left_cam.isOpened() and right_cam.isOpened():
    if counter > 8:
        left_ret, left = left_cam.read()
        right_ret, right = right_cam.read()

        if not left_ret or not right_ret:
            break
        if counter > 30:

            left, right = disparity.calibrate_frame(
                left, right, path_to_calibration)

            height_left, width_left = left.shape[:2]
            height_right, width_right = right.shape[:2]

            new_height = min(height_left, height_right)
            new_width = min(width_left, width_right)

            left = left[20:new_height, 0: new_width]
            right = right[0:new_height - 20, 0: new_width]

            #left = np.uint8(left)
            #right = np.uint8(right)

            window_size = 3
            min_disp = 16
            num_disp = 112-min_disp
            stereo = cv2.StereoSGBM_create(minDisparity=min_disp,
                                           numDisparities=num_disp,
                                           blockSize=16,
                                           P1=8*3*window_size**2,
                                           P2=32*3*window_size**2,
                                           disp12MaxDiff=1,
                                           uniquenessRatio=10,
                                           speckleWindowSize=100,
                                           speckleRange=32
                                           )
            stereo = cv2.StereoBM(numDisparities=16, blockSize=15)

            print('computing disparity...')
            dis = stereo.compute(left, right).astype(np.float32) / 16.0
            #disparity_image = np.uint8(right)
            disparity_image = np.uint8(dis)
            print('frame {} computed'.format(counter))
            #display.display([left, disparity_image])
            #cv2.imwrite('/home/jetson/Videos/disparity/testimage{}.png'.format(counter), disparity_image)
            # out.write(disparity_image)
            # print(disparity)
            #plt.imshow(dis, 'gray')
            # plt.show()
    else:
        _, left = left_cam.read()
    counter += 1


out.release()
left_cam.release()
right_cam.release()
