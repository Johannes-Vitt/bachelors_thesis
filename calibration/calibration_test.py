import sys
import numpy as np
import cv2
import glob

cv2.namedWindow('Disparity')


REMAP_INTERPOLATION = cv2.INTER_LINEAR

DEPTH_VISUALIZATION_SCALE = 2048

# set input images
path_to_image_directory = '/home/jetson/2019-johannes-vitt-bsc-thesis/data/images/2019-09-07_02:10:20.451385'
path_img_cam_1 = path_to_image_directory + '/col_cam_1/*.png'
path_img_cam_2 = path_to_image_directory + '/col_cam_2/*.png'
images_cam_1 = sorted(glob.glob(path_img_cam_1))
images_cam_2 = sorted(glob.glob(path_img_cam_2))

calibration = np.load('calibration_parameters.npz', allow_pickle=False)
imageSize = tuple(calibration["imageSize"])
leftMapX = calibration["leftMapX"]
leftMapY = calibration["leftMapY"]
leftROI = tuple(calibration["leftROI"])
rightMapX = calibration["rightMapX"]
rightMapY = calibration["rightMapY"]
rightROI = tuple(calibration["rightROI"])


# TODO: Why these values in particular?
# TODO: Try applying brightness/contrast/gamma adjustments to the images
stereoMatcher = cv2.StereoBM_create()
stereoMatcher.setMinDisparity(4)
stereoMatcher.setNumDisparities(128)
stereoMatcher.setBlockSize(21)
stereoMatcher.setROI1(leftROI)
stereoMatcher.setROI2(rightROI)
stereoMatcher.setSpeckleRange(16)
stereoMatcher.setSpeckleWindowSize(45)

# Grab both frames first, then retrieve to minimize latency between cameras
for image_index in range(len(images_cam_1)):
    leftFrame = cv2.imread(images_cam_1[image_index])
    rightFrame = cv2.imread(images_cam_2[image_index])

    fixedLeft = cv2.remap(leftFrame, leftMapX, leftMapY, REMAP_INTERPOLATION)
    fixedRight = cv2.remap(rightFrame, rightMapX,
                           rightMapY, REMAP_INTERPOLATION)

    grayLeft = cv2.cvtColor(fixedLeft, cv2.COLOR_BGR2GRAY)
    grayRight = cv2.cvtColor(fixedRight, cv2.COLOR_BGR2GRAY)
    depth = stereoMatcher.compute(grayLeft, grayRight)


    cv2.imshow('Disparity',depth.astype('uint8')*255)
    k = cv2.waitKey()
