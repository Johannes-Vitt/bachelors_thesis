import cv2
import argparse
import ir_detection
import display

ap = argparse.ArgumentParser()

ap.add_argument("-ir", "--infrared", required=True,
                help="input the path to the ir image", type=str)
ap.add_argument("-col", "--color", required=True,
                help="input the path to the colored image", type=str)

display.init_cams(2)

# turn the args into an array
args = vars(ap.parse_args())

ir_frame = cv2.imread(args['infrared'])
col_frame = cv2.imread(args['color'])

ir_detections = ir_detection.detect_humans(ir_frame)
ir_detections = list(map(list, ir_detections))
print(ir_detections)
print(len(ir_detections))
display.display_with_box([col_frame, ir_frame], [ir_detections, []])
