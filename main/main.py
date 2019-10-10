import cv2
from datetime import datetime
from datetime import timedelta
import argparse
import os
import glob
from imutils.video import FPS

import human_detection
import display
import tracking
import human
import histogram


# set up all the arg parsing stuff
ap = argparse.ArgumentParser()

ap.add_argument("-i", "--input", required=False,
                help="if the input images are not provided via the attached cams, the path must be provided here. Note: the path must end with a slash", type=str)

ap.add_argument("-vd", "--video", required=False,
                help="When the provided images from the files are stored as a video set this to true. Default: True", type=bool, default=True)

ap.add_argument("-r", "--right", required=False,
                help="provide which camera is the right camera (either \"0\" or \"2\")",  type=int, default=0)

ap.add_argument("-s", "--save_result", required=False,
                help="should the results of the detection be save in the directory? Default: \"False\"", type=bool, default=False)

ap.add_argument("-dt", "--detection", required=False,
                help="specify the detection method. \"HOG\" or \"CNN\" are valid here. Default is \"HOG\"", type=str, default="HOG")

ap.add_argument("-di", "--display", required=False,
                help="enter if the processed image should be displayed by opencv. Enter \"True\" or \"False\". Default: \"True\"", type=bool, default=True)
# for development purposes only
ap.add_argument("-dp", "--disparity", required=False,
                help="Enter if a disparity image should be computed and displayed. Enter \"True\" or \"False\". Default: \"False\"", type=bool, default=False)

# turn the args into an array
args = vars(ap.parse_args())

# if we need to display the result we need to init the output
if args['display']:
    display.init_cams(2)


# we need to setup our detector
human_detection = human_detection.Detector(args['detection'])

# we initialize our ids of human detection
human_id_counter = 0
detected_humans = []
# threshold for the deviation of the postion of the rectangle when detecting a new box
threshold_tracking_deviating = 400
# threshold for how many frames an "old" undetected human frame should be kept in "memory"
threshold_tracking_undetected_frames = 4

# we start the fps counting
fps = FPS().start()

# we check whether we need to save the results to the disk.
if args['save_result']:
    data_path = '/home/jetson/2019-johannes-vitt-bsc-thesis/data/images/'

    directory_name = str(datetime.now())
    directory_name = directory_name.replace(' ', '_')
    os.mkdir(data_path + '/col_cam_1/' + directory_name)
    os.mkdir(data_path + '/col_cam_2/' + directory_name)
    os.mkdir(data_path + '/ir_cam_1/' + directory_name)

# a function that handles the main processing of the frame


def process_frame(left_frame, right_frame, ir_frame):

    print('\n\n------------- New Frame -------------')
    global detected_humans
    global human_id_counter
    frame_1 = left_frame
    frame_2 = right_frame
    # detect humans in the frame
    boxes_1 = human_detection.detection(left_frame, right_frame, ir_frame, args['disparity'])

    print('positions where we have detected humans in the frame: {}'.format(boxes_1))

    # track the humans

    # for each entry in the detector compare the detected postion with the postition of the humans that are already in the list
    # if there is no human in the range, create a new human and add it to the list
    if detected_humans:
        new_occurances = tracking.detect_new_occurance_and_update_positions(
            frame_1, threshold_tracking_deviating, boxes_1, detected_humans)
        for new_block in new_occurances:
            # calculate the histogram for the newly detected human
            image_in_bounding_box = frame_1[int(new_block[1]): int(new_block[1]) +
                                            int(new_block[3]), int(new_block[0]): int(new_block[0]) + int(new_block[2])]
            hist = histogram.create_histogram(image_in_bounding_box)
            
            detected_humans.append(human.Human(
                human_id_counter, new_block, hist))
            human_id_counter = human_id_counter + 1
    else:
        for new_block in boxes_1:
            # calculate the histogram for the newly detected human
            image_in_bounding_box = frame_1[int(new_block[1]): int(new_block[1]) +
                                            int(new_block[3]), int(new_block[0]): int(new_block[0]) + int(new_block[2])]
            hist = histogram.create_histogram(image_in_bounding_box)

            detected_humans.append(human.Human(
                human_id_counter, new_block, hist))
            human_id_counter = human_id_counter + 1
    # remove all humans from the list that have a non_detected counter higher than the threshold
    detected_humans = list(filter(
        lambda x: x.get_untracked_frame_counter() < threshold_tracking_undetected_frames, detected_humans))
    print('our human list after filtering out all humans that were not detected for a few frames: {}'.format(
        detected_humans))

    # update fps
    fps.update()

    if args['display']:
        if ir_frame is not None:
            display.display_with_humans(
                [frame_1, ir_frame], [detected_humans, []])
        else:
            display.display_with_humans([frame_1], [detected_humans])


# check whether the input is from file or from attached cams
# for simplicity we assume that either all cameras are plugged in or all images are provided from file
if args['input'] is None:
    # Note: the numbering of the devices in /dev/ might be different every time, therefore one does not know which cam is 'left' or 'right'
    cam_1 = cv2.VideoCapture(0)
    # set the size of the frame
    cam_1.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cam_1.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    # also initialize the second cam
    cam_2 = cv2.VideoCapture(2)
    cam_2.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cam_2.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    # because the ir cam can't be connected to opencv directly yet we dont need to initialize it

    while True:
        frame_1_ret, frame_1 = cam_1.read()
        frame_2_ret, frame_2 = cam_2.read()

        # if one of the cameras is no longer reachable we stop the loop
        if not frame_1_ret or not frame_2_ret:
            break

        process_frame(frame_1, frame_2, None)

else:
    path_to_image_directory = args['input']
    path_ir_cam = path_to_image_directory + '/ir_cam_1/*.png'

    images_ir = sorted(glob.glob(path_ir_cam))
    ir_counter = 0
    # the input file can either be passed as a video or as images in a directory
    if args['video']:
        left_cam = cv2.VideoCapture(
            '{}/col_cam_1/video.avi'.format(path_to_image_directory))
        right_cam = cv2.VideoCapture(
            '{}/col_cam_2/video.avi'.format(path_to_image_directory))
        framecounter = 0
        # the time the video was started
        time_as_string = path_to_image_directory.split('/')[-1]
        video_start_time = datetime.strptime(
            time_as_string, "%Y-%m-%d_%H:%M:%S.%f")
        # get the framerate of the video
        # TODO: read from the file
        framerate_video = 4
        while left_cam.isOpened() and right_cam.isOpened():
            ret_left, left_frame = left_cam.read()
            ret_right, right_frame = right_cam.read()

            video_time = video_start_time + \
                timedelta(seconds=int((1/framerate_video) * framecounter))
            # this need to be adopted to the timing of the video
            ir_time = images_ir[ir_counter].split('/')[-1]
            if (ir_counter + 1) < len(images_ir) and images_ir[ir_counter + 1].split('/')[-1] < str(video_time).replace(' ', '_'):
                ir_counter += 1

            # if no frame could be capture it means we are out of frames
            if not ret_left or not ret_right:
                break

            print('before loading the ir image')
            # add the right IR image again
            ir_frame = cv2.imread(images_ir[ir_counter])
            print('after loading the ir image')

            #print('current ir image: {}'.format(images_ir[ir_counter]))
            process_frame(left_frame, right_frame, ir_frame)
            framecounter += 1

    # if the images are not passed as a video the are images in a directory
    else:
        for image_index in range(len(images_cam_1)):
            path_img_cam_1 = path_to_image_directory + '/col_cam_1/*.png'
            path_img_cam_2 = path_to_image_directory + '/col_cam_2/*.png'
            images_cam_1 = sorted(glob.glob(path_img_cam_1))
            images_cam_2 = sorted(glob.glob(path_img_cam_2))

            # there is no ir image for every frame. So we need to check what the last ir frame is. Since the date is saved as the file name we can just compare them alphanumerically
            if (ir_counter + 1) < len(images_ir) and images_ir[ir_counter + 1] < images_cam_1[image_index]:
                ir_counter += 1

            # get the input images
            frame_1 = cv2.imread(images_cam_1[image_index])
            frame_2 = cv2.imread(images_cam_2[image_index])
            ir_frame = cv2.imread(images_ir[ir_counter])
            print('current ir image: {}'.format(images_ir[ir_counter]))
            # we call the main processing function
            process_frame(frame_1, frame_2, ir_frame)

fps.stop()
print('Currently we run at {} fps'.format(fps.fps()))
exit()
