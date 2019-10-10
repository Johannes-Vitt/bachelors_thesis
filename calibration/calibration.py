# based on blog https://albertarmea.com/post/opencv-stereo-camera/
# code from https://gist.github.com/aarmea/629e59ac7b640a60340145809b1c9013
import numpy as np
import cv2

path_output_file = "calibration_parameters.npz"
path_to_left_calibration = 'left/calibration_parameters.npz'
path_to_right_calibration = 'right/calibration_parameters.npz'

OPTIMIZE_ALPHA = 0.25

TERMINATION_CRITERIA = (cv2.TERM_CRITERIA_EPS +
                        cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

left_calibration_file = np.load(path_to_left_calibration)
right_calibration_file = np.load(path_to_right_calibration)

leftObjectPoints = left_calibration_file['objpoints']
rightObjectPoints = right_calibration_file['objpoints']

leftImagePoints = left_calibration_file['imgpoints']
rightImagePoints = right_calibration_file['imgpoints']

leftCameraMatrix = left_calibration_file['mtx']
rightCameraMatrix = right_calibration_file['mtx']

leftDistortionCoefficients = left_calibration_file['dist']
rightDistortionCoefficients = right_calibration_file['dist']

imageSize = left_calibration_file['img_size']
imageSize = tuple(imageSize)

objectPoints = leftObjectPoints

print("Calibrating cameras together...")
(_, _, _, _, _, rotationMatrix, translationVector, _, _) = cv2.stereoCalibrate(
    objectPoints, leftImagePoints, rightImagePoints,
    leftCameraMatrix, leftDistortionCoefficients,
    rightCameraMatrix, rightDistortionCoefficients,
    imageSize, None, None, None, None, cv2.CALIB_FIX_INTRINSIC, TERMINATION_CRITERIA)

print("Rectifying cameras...")
(leftRectification, rightRectification, leftProjection, rightProjection,
 dispartityToDepthMap, leftROI, rightROI) = cv2.stereoRectify(
    leftCameraMatrix, leftDistortionCoefficients,
    rightCameraMatrix, rightDistortionCoefficients,
    imageSize, rotationMatrix, translationVector,
    None, None, None, None, None,
    cv2.CALIB_ZERO_DISPARITY, OPTIMIZE_ALPHA)

print("Saving calibration...")
leftMapX, leftMapY = cv2.initUndistortRectifyMap(
    leftCameraMatrix, leftDistortionCoefficients, leftRectification,
    leftProjection, imageSize, cv2.CV_32FC1)
rightMapX, rightMapY = cv2.initUndistortRectifyMap(
    rightCameraMatrix, rightDistortionCoefficients, rightRectification,
    rightProjection, imageSize, cv2.CV_32FC1)

np.savez_compressed(path_output_file, imageSize=imageSize,
                    leftMapX=leftMapX, leftMapY=leftMapY, leftROI=leftROI,
                    rightMapX=rightMapX, rightMapY=rightMapY, rightROI=rightROI)
