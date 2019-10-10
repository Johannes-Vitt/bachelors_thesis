import cv2
import human

# set the font and font size for this


def init_cams(number_of_cams):
    for index in range(number_of_cams):
        cv2.namedWindow("Window " + str(index))


# displays all frames (provided as a list) in the different images that were set up in the initialization
def display(frames):
    for index in range(len(frames)):
        cv2.imshow("Window " + str(index), frames[index])
    k = cv2.waitKey(25)

# displayes all frames with the corresponding box. boxes is a list of list of boxes (each frame can have multiple boxes)


def display_with_box(frames, boxes):
    # for each frame there is a list of boxes (each box is a list)
    for index in range(len(frames)):
        if len(boxes) == len(frames):
            for box_in_frame in boxes[index]:
                (x, y, w, h) = box_in_frame
                print('x: {}, y:{}, w:{}, h:{}'.format(x, y, w, h))
                cv2.rectangle(frames[index], (int(x), int(y)),
                              (int(x + w), int(y + h)), (0, 255, 0), 2)
        cv2.imshow("Window " + str(index), frames[index])
        k = cv2.waitKey(10000)
        
def overlay(image1, image2):
    overlay_image = cv2.addWeighted(image1, 0.5, image2, 0.5,0)
    cv2.imshow('Window 0', overlay_image)
    if cv2.waitKey(25) & 0xFF == ord('s'):
        cv2.imwrite('overlay.png', overlay_image)
        cv2.imwrite('left.png', image1)
        cv2.imwrite('right.png', image2)

def display_with_humans(frames, humans):
    # for each frame there is a list of humans
    for index in range(len(frames)):
        if len(humans) == len(frames):
            if humans[index] is not None:
                for human in humans[index]:
                    last_position = human.get_current_position()
                    if last_position is not None:
                        # draw the bounding box
                        (x, y, w, h) = last_position
                        cv2.rectangle(frames[index], (int(x), int(y)),
                                      (int(x + w), int(y + h)), (0, 255, 0), 2)
                        # draw the id of the human on the frame
                        cv2.putText(frames[index], 'ID: {}'.format(
                            human.get_id()), (int(x), int(y)), cv2.FONT_HERSHEY_SIMPLEX, 2, 255)
        cv2.imshow("Window " + str(index), frames[index])
        k = cv2.waitKey(1)
