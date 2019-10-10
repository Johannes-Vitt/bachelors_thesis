# based on https://www.pyimagesearch.com/2018/07/30/opencv-object-tracking/
import cv2
import math
import histogram


class Tracker:
    def __init__(self, frame, bounding_box):
        self.initBoundingBox = bounding_box
        # init the object tracker
        self.tracker = cv2.TrackerKCF_create()
        self.tracker.init(frame, tuple(bounding_box))

    # update the tracker with the new frame and return the new bounding box if the object was also detected in the new frame
    def track(self, frame):
        (success, newBoundingBox) = self.tracker.update(frame)
        if success:
            return newBoundingBox
        else:
            return None

# remove all the entries from the detected_bounding_boxes list where the position is close to the tracked position


def euclidian_distance(point_1, point_2):
    (x_1, y_1) = point_1
    (x_2, y_2) = point_2
    return math.sqrt(pow((x_1 - x_2), 2) + pow((y_1 - y_2), 2))


def detect_new_occurance_and_update_positions(frame, max_deviation, detected_bounding_boxes, detected_humans):
    # for each bounding box that was detected we calculate the euclidian distance of its center to the center of the bounding boxes that are available
    result_list = detected_bounding_boxes.copy()
    # we initialize the list of the previous humans that were not detected in this frame with all previous humans. If the humans is discovered in this frame its reference will be removed from the list
    non_detected_humans = detected_humans.copy()
    unmatched_previous_humans = detected_humans.copy()
    if unmatched_previous_humans:
        for detected_bounding_box in detected_bounding_boxes:
            detected_centroid = (detected_bounding_box[0] + detected_bounding_box[2] / 2,
                                 detected_bounding_box[1] + detected_bounding_box[3] / 2)

            detected_histogram = histogram.create_histogram(frame[detected_bounding_box[1]: detected_bounding_box[1] +
                                                                  detected_bounding_box[3], detected_bounding_box[0]: detected_bounding_box[0] + detected_bounding_box[2]])

            for human in unmatched_previous_humans:
                new_centroid = human.get_current_position()[
                    0] + human.get_current_position()[2] / 2, human.get_current_position()[1] + human.get_current_position()[3] / 2

            # for each bounding box we sort the previous human occurances by their proximity. If the closest previous_human is lower (e.g. closer) than the threshold, it is considered to be the same
            unmatched_previous_humans.sort(key=lambda human: euclidian_distance(
                (human.get_current_position()[0] + human.get_current_position()[2] / 2, human.get_current_position()[1] + human.get_current_position()[3] / 2), detected_centroid))

            # filter out all humans that are not in the range anyway
            unmatched_previous_humans_within_range = list(filter(lambda human: euclidian_distance((human.get_current_position()[0] + human.get_current_position()[2] / 2, human.get_current_position()[1] + human.get_current_position()[3] / 2), detected_centroid) < max_deviation, unmatched_previous_humans))

            
            # sort the humans that are left by the similarity of their histogram
            unmatched_previous_humans_within_range.sort(
                key=lambda human: histogram.compare_histograms(detected_histogram, human.get_histogram()))

            if unmatched_previous_humans_within_range:
                centroid_of_closest_unmatched_human = unmatched_previous_humans_within_range[0].get_current_position()[
                    0] + unmatched_previous_humans_within_range[0].get_current_position()[2] / 2, unmatched_previous_humans_within_range[0].get_current_position()[1] + unmatched_previous_humans_within_range[0].get_current_position()[3] / 2
                print(
                    'we have a match between a newly detected human and an entry in our previous list!')
                # if the position is close enough we know that we dont need to add a new human
                result_list.remove(detected_bounding_box)
                # update the position of the human. Note since we used a shallow copy for the creation of the sorted_humans the following code updates the elements in the original detected_humans list
                unmatched_previous_humans[0].update_position(
                    detected_bounding_box)
                # we found an occurance of that human so we can remove if from the 'not found' list
                non_detected_humans.remove(unmatched_previous_humans[0])
                unmatched_previous_humans.remove(unmatched_previous_humans[0])


    for human in non_detected_humans:
        human.increase_untracked_frame_counter()
    return result_list
