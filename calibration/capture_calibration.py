# source: https://stackoverflow.com/questions/34588464/python-how-to-capture-image-from-webcam-on-click-using-opencv
import cv2
from threading import Thread
from imutils.video import WebcamVideoStream


def save_image(image, path):
    cv2.imwrite(path, image)


def start_thread(image, path):
    thread = Thread(target=save_image, args=(image, path))
    thread.start()


stream_left = WebcamVideoStream(src=0).start()
stream_right = WebcamVideoStream(src=2).start()

cv2.namedWindow("Left")
cv2.namedWindow("Right")

img_counter = 0

while True:
    frame_left = stream_left.read()
    frame_right = stream_right.read()

    cv2.imshow("Left", frame_left)
    cv2.imshow("Right", frame_left)
    k = cv2.waitKey(1)

    if k % 256 == 27:
        # ESC pressed
        print("Escape hit, closing...")
        break
    elif k % 256 == 32:
        # SPACE pressed
        left_path = "left/chessplate_calibration_{}.png".format(img_counter)
        right_path = "right/chessplate_calibration_{}.png".format(img_counter)
        start_thread(frame_left, left_path)
        start_thread(frame_right, right_path)
        print("{} and {} written!".format(left_path, right_path))
        img_counter += 1

stream_left.release()
stream_right.release()

cv2.destroyAllWindows()
