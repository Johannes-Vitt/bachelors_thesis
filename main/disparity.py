import numpy as np
#from sklearn.preprocessing import normalize
import cv2
import display

REMAP_INTERPOLATION = cv2.INTER_LINEAR

DEPTH_VISUALIZATION_SCALE = 2048


path_to_calibration = '/home/jetson/2019-johannes-vitt-bsc-thesis/calibration/near_angle/calibration_parameters.npz'


def human_detection_on_disparity(disparity_last, disparity_current, disparity_next):
    # we compare the disparity frame to the next and the last frame
    # if the pixel value is different from the next and the last frame there has to be a human

    last_and_current = np.absolute(
        np.subtract(disparity_last, disparity_current))
    current_and_next = np.absolute(
        np.subtract(disparity_current, disparity_next))
    cleaned_up_image = np.minimum(last_and_current, current_and_next)

    # manipulate the image a bit
    #cleaned_up_image = cv2.cvtColor(cleaned_up_image, cv2.COLOR_RGB2GRAY)
    cleaned_up_image = cv2.erode(cleaned_up_image, None, iterations=1)
    cleaned_up_image = cleaned_up_image = cv2.dilate(
        cleaned_up_image, None, iterations=6)
    ret, binary_image = cv2.threshold(
        cleaned_up_image, 40, 255, cv2.THRESH_BINARY)

    #binary_image = cv2.bitwise_not(binary_image)
    contours, hier = cv2.findContours(
        binary_image, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    bounding_boxes = []
    for cnt in contours:
        if 50000 < cv2.contourArea(cnt) and cv2.contourArea(cnt) < 300000:
            bounding_boxes.append(cv2.boundingRect(cnt))
    return bounding_boxes


def calibrate_frame(left, right, path_to_calibration):
    path_to_left_calibration = path_to_calibration + 'left/calibration_parameters.npz'
    path_to_right_calibration = path_to_calibration + \
        'right/calibration_parameters.npz'

    left_calibration_file = np.load(path_to_left_calibration)
    right_calibration_file = np.load(path_to_right_calibration)

    leftCameraMatrix = left_calibration_file['mtx']
    rightCameraMatrix = right_calibration_file['mtx']

    leftDistortionCoefficients = left_calibration_file['dist']
    rightDistortionCoefficients = right_calibration_file['dist']

    h_left, w_left = left.shape[:2]
    h_right, w_right = right.shape[:2]

    # do the cropping and stuff on the left frame
    newcameramtx_left, roi_left = cv2.getOptimalNewCameraMatrix(
        leftCameraMatrix, leftDistortionCoefficients, (w_left, h_left), 1, (w_left, h_left))
    dst_left = cv2.undistort(
        left, leftCameraMatrix, leftDistortionCoefficients, None, newcameramtx_left)

    # crop the image
    x_left, y_left, w_left, h_left = roi_left
    dst_left = dst_left[y_left:y_left+h_left, x_left:x_left+w_left]

    # do it also on the right frame
    newcameramtx_right, roi_right = cv2.getOptimalNewCameraMatrix(
        rightCameraMatrix, rightDistortionCoefficients, (w_right, h_right), 1, (w_right, h_right))
    dst_right = cv2.undistort(
        right, rightCameraMatrix, rightDistortionCoefficients, None, newcameramtx_right)

    # crop the image
    x_right, y_right, w_right, h_right = roi_right
    dst_right = dst_right[y_right:y_right+h_right, x_right:x_right+w_right]

    return (dst_left, dst_right)


def calibrate_frame_hard_way(left, right, path_to_calibration):
    path_to_calibration = path_to_calibration + 'calibration_parameters.npz'

    calibration_file = np.load(path_to_calibration)

    leftMapX = calibration_file['leftMapX']
    leftMapY = calibration_file['leftMapY']

    rightMapX = calibration_file['rightMapX']
    rightMapY = calibration_file['rightMapY']

    dst_left = cv2.remap(
        left, leftMapX, leftMapY, cv2.INTER_NEAREST)

    dst_right = cv2.remap(
        right, rightMapX, rightMapY, cv2.INTER_NEAREST)

    return (dst_left, dst_right)


def disparity_image(left, right, path_to_calibration):
    left, right = calibrate_frame(left, right, path_to_calibration)

    height_left, width_left = left.shape[:2]
    height_right, width_right = right.shape[:2]
    new_height = min(height_left, height_right)
    new_width = min(width_left, width_right)
    left = left[20:new_height, 0: new_width]
    right = right[0:new_height - 20, 0: new_width]
    #left = np.uint8(left)
    # right = np.uint8(right
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
    #stereo = cv2.StereoBM(numDisparities=16, blockSize=15)
    print('computing disparity...')
    dis = stereo.compute(left, right).astype(np.float32) / 16.0
    #disparity_image = np.uint8(right)
    disparity_image = np.uint8(dis)
    return disparity_image


def disparity_parameters(frame_1, frame_2, path_to_calibration, window_size, minDisparity, maxDisparity, blockSize):

    fixedLeft, fixedRight = calibrate_frame(
        frame_1, frame_2,  path_to_calibration)

    # SGBM Parameters -----------------
    # wsize default 3; 5; 7 for SGBM reduced size image; 15 for SGBM full size image (1300px and above); 5 Works nicely
    window_size = window_size

    left_matcher = cv2.StereoSGBM_create(
        minDisparity=minDisparity,
        # max_disp has to be dividable by 16 f. E. HH 192, 256
        numDisparities=maxDisparity,
        blockSize=blockSize,
        # wsize default 3; 5; 7 for SGBM reduced size image; 15 for SGBM full size image (1300px and above); 5 Works nicely
        P1=8 * 3 * window_size ** 2,
        P2=32 * 3 * window_size ** 2,
        disp12MaxDiff=1,
        uniquenessRatio=15,
        speckleWindowSize=0,
        speckleRange=2,
        preFilterCap=63,
        mode=cv2.STEREO_SGBM_MODE_SGBM_3WAY
    )

    right_matcher = cv2.ximgproc.createRightMatcher(left_matcher)

    # FILTER Parameters
    lmbda = 80000
    sigma = 1.2
    visual_multiplier = 1.0

    wls_filter = cv2.ximgproc.createDisparityWLSFilter(
        matcher_left=left_matcher)
    wls_filter.setLambda(lmbda)
    wls_filter.setSigmaColor(sigma)

    displ = left_matcher.compute(frame_1, frame_2)  # .astype(np.float32)/16
    dispr = right_matcher.compute(frame_2, frame_1)  # .astype(np.float32)/16
    displ = np.int16(displ)
    dispr = np.int16(dispr)
    filteredImg = wls_filter.filter(displ, frame_1, None, dispr)

    filteredImg = cv2.normalize(
        src=filteredImg, dst=filteredImg, beta=0, alpha=255, norm_type=cv2.NORM_MINMAX)
    filteredImg = np.uint8(filteredImg)
    return filteredImg


def disparity_image_SGBM(frame_1, frame_2, path_to_calibration):

    frame_1 = calibrate_frame(frame_1, path_to_calibration)
    frame_2 = calibrate_frame(frame_2, path_to_calibration)

    # SGBM Parameters -----------------
    # was 5 wsize default 3; 5; 7 for SGBM reduced size image; 15 for SGBM full size image (1300px and above); 5 Works nicely
    window_size = 15

    left_matcher = cv2.StereoSGBM_create(
        minDisparity=0,
        # was 256 was 160 max_disp has to be dividable by 16 f. E. HH 192, 256
        numDisparities=256,
        blockSize=15,
        # wsize default 3; 5; 7 for SGBM reduced size image; 15 for SGBM full size image (1300px and above); 5 Works nicely
        P1=8 * 3 * window_size ** 2,
        P2=32 * 3 * window_size ** 2,
        disp12MaxDiff=1,
        uniquenessRatio=15,
        speckleWindowSize=0,
        speckleRange=2,
        preFilterCap=63,
        mode=cv2.STEREO_SGBM_MODE_SGBM_3WAY
    )

    right_matcher = cv2.ximgproc.createRightMatcher(left_matcher)

    # FILTER Parameters
    lmbda = 80000
    sigma = 1.2
    visual_multiplier = 1.0

    wls_filter = cv2.ximgproc.createDisparityWLSFilter(
        matcher_left=left_matcher)
    wls_filter.setLambda(lmbda)
    wls_filter.setSigmaColor(sigma)

    print('computing disparity...')
    displ = left_matcher.compute(frame_1, frame_2)  # .astype(np.float32)/16
    dispr = right_matcher.compute(frame_2, frame_1)  # .astype(np.float32)/16
    displ = np.int16(displ)
    dispr = np.int16(dispr)
    filteredImg = wls_filter.filter(displ, frame_1, None, dispr)

    filteredImg = cv2.normalize(
        src=filteredImg, dst=filteredImg, beta=0, alpha=255, norm_type=cv2.NORM_MINMAX)
    filteredImg = np.uint8(filteredImg)
    return filteredImg
