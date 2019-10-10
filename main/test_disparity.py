import display
import cv2
import disparity
import glob
import numpy as np

display.init_cams(1)

disparity_images = glob.glob('/home/jetson/Videos/disparity/*.png')

last_frame_path = ''
current_frame_path = ''
next_frame_path = ''


last_frame = None
current_frame = None
next_frame = None

frame_counter = 0
for new_image_path in disparity_images:
    last_frame_path = current_frame_path
    current_frame_path = next_frame_path
    next_frame_path = new_image_path

    if (last_frame_path != '') and (current_frame_path != '') and (next_frame_path != ''):
        last_frame = cv2.imread(last_frame_path)
        current_frame = cv2.imread(current_frame_path)
        next_frame = cv2.imread(new_image_path)
        cleaned_up_image = disparity.human_detection_on_disparity(
            last_frame, current_frame, next_frame)
        # manipulate the image a bit
        cleaned_up_image = cv2.cvtColor(cleaned_up_image, cv2.COLOR_RGB2GRAY)
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

        cv2.imwrite(
            '/home/jetson/Videos/disparity_result/disparity_improved{}.png'.format(frame_counter), binary_image)
        binary_image = cv2.cvtColor(binary_image, cv2.COLOR_GRAY2RGB)
        display.display_with_box([current_frame], [bounding_boxes])
        frame_counter += 1
