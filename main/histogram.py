import cv2

# defintions for the histogram stuff

h_bins = 50
s_bins = 60
histSize = [h_bins, s_bins]
# hue varies from 0 to 179, saturation from 0 to 255
h_ranges = [0, 180]
s_ranges = [0, 256]
ranges = h_ranges + s_ranges  # concat lists
# Use the 0-th and 1-st channels
channels = [0, 1]

# set the histogram comparision method to BHATTACHARYYA (the lower the better)
HISTOGRAM_COMPARISION = cv2.HISTCMP_BHATTACHARYYA


def create_histogram(frame):
    print('we are creating a histogram')
    # turn the image into a hsv image
    hsv_images = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    # calculate the histogram
    histogram = cv2.calcHist([hsv_images], channels,
                             None, histSize, ranges, accumulate=False)
    cv2.normalize(histogram, histogram, alpha=0,
                  beta=1, norm_type=cv2.NORM_MINMAX)
    return histogram


def compare_histograms(histogram_1, histogram_2):
    # the lower the number this function returns the more similar the histograms are
    return cv2.compareHist(histogram_1, histogram_2, HISTOGRAM_COMPARISION)
