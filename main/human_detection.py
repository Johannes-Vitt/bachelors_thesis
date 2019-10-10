import cv2

import HOG_Descriptor
import CNN_detector
import ir_detection
import disparity

CERTAINITY_THRESHOLD = 0.7
IR_PUNISHMENT = 0.1
IR_OVERLAPPING_AREA = 0.2
calibration_path = '/home/jetson/2019-johannes-vitt-bsc-thesis/calibration/'

# returns the value (between 1.0 and 0.0) how much area of the first rectangle is covered by the second


def covered_area(rectangle_a, rectangle_b):
    x_a, y_a, w_a, h_a = rectangle_a
    x_b, y_b, w_b, h_b = rectangle_b

    if x_a + w_a < x_b or x_b + w_b < x_a or y_a + h_a < y_b or y_b + h_b < y_a:
        # the two rectangles do not overlap
        return 0.0
    else:
        area_a = w_a * h_a
        area_overlap = 0
        w_overlap = 0
        h_overlap = 0
        # calculate the width of the overlap
        if x_a < x_b:
            w_overlap = w_a - abs(x_b - x_a)
        else:
            w_overlap = w_b - abs(x_a - x_b)
        # calculte the height overlap
        if y_a < y_b:
            h_overlap = h_a - abs(y_b - y_a)
        else:
            h_overlap = h_b - abs(y_a - y_b)
        area_overlap = w_overlap * h_overlap
        return area_overlap/area_a


class Detector:
    def __init__(self, detectorType):
        self.last_disparity_frame = None
        self.current_disparity_frame = None
        self.next_disparity_frame = None
        self.detector_type = detectorType
        if detectorType == "CNN":
            self.cnn_detector = CNN_detector.CNNDetector()

    def disparity_detection(self, detections, left_frame, right_frame):
        print('doing the disparity detection')
        new_frame = disparity.disparity_image(left_frame, right_frame, calibration_path)

        self.last_disparity_frame = self.current_disparity_frame
        self.current_disparity_frame = self.next_disparity_frame
        self.next_disparity_frame = new_frame

        if self.last_disparity_frame is not None and self.current_disparity_frame is not None and self.next_disparity_frame is not None:
            disparity_blocks = disparity.human_detection_on_disparity(
                self.last_disparity_frame, self.current_disparity_frame, self.next_disparity_frame)
            for detection in detections:
                if list(filter(lambda x: covered_area(detection[0], x), disparity_blocks)):
                    detection = (detection[0], detection[1] + IR_PUNISHMENT)

    def ir_analysis(self, detections, frame, ir_frame):
        ir_blocks = ir_detection.detect_humans(ir_frame)
        #print('blocks where we detected a human in the ir image: {}'.format(ir_blocks))
        for detection in detections:

            if list(filter(lambda x: covered_area(detection[0], x), ir_blocks)):
                detection = (detection[0], detection[1] + IR_PUNISHMENT)

    # return all bounding boxes above the thresholds. Also uses the IR image to calculate the scores
    def detection(self, left_frame, right_frame, ir_frame, disparity_on):
        if self.detector_type == 'HOG':
            detections = HOG_Descriptor.hog_detection(left_frame)
            self.ir_analysis(detections, left_frame, ir_frame)
            if disparity_on:
                self.disparity_detection(detections, left_frame, right_frame)
            detections_above_threshold = list(
                filter(lambda x: x[1] > CERTAINITY_THRESHOLD, detections))
            return list(map(lambda x: x[0], detections_above_threshold))

        elif self.detector_type == 'CNN':
            detections = self.cnn_detector.detect_cnn(left_frame)
            self.ir_analysis(detections, left_frame, ir_frame)
            if disparity_on:
                self.disparity_detection(detections, left_frame, right_frame)
            detections_above_threshold = list(
                filter(lambda x: x[1] > CERTAINITY_THRESHOLD, detections))
            return list(map(lambda x: x[0], detections_above_threshold))
