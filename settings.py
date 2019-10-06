color_space = 'RGB' # Can be RGB, HSV, LUV, HLS, YUV, YCrCb, GRAY
orient = 30  # HOG orientations
pix_per_cell = 16 # HOG pixels per cell
cell_per_block = 2 # HOG cells per block
hog_channel = 'ALL' # Can be 0, 1, 2, or ALL
spatial_size = (16, 16) # Spatial binning dimensions
hist_bins = 16	# Number of histogram bins
spatial_feat = False # Spatial features on or off
hist_feat = False # Histogram features on or off
hog_feat = True # HOG features on or off
y_start_stop = [400, 720] # Min and max in y to search in slide_window()
x_start_stop = [0, 1280] # ditto for x
pct_overlap = 0.7 # sliding window overlap percentage
heatmap_thresh = 33
num_frames = 30 # number of video frames over which to accumulate heatmap
min_ar, max_ar = 0.7, 3.0 # bounding box acceptable aspect ratio range
small_bbox_area, close_y_thresh = 80*80, 500
min_bbox_area = 40*40
use_pretrained = True # load pre-trained SVM model from disk?
maximum_stop = 60

scheduled_arrivals_workdays = {
    5: [8, 28, 45, 57],
    6: [9, 21, 33, 39, 45, 51, 57],
    7: [3, 9, 15, 21, 27, 33, 39, 45, 51, 57],
    8: [3, 10, 18, 28, 38, 48],
    9: [3, 18, 33, 48],
    10: [3, 18, 33, 48],
    11: [3, 18, 33, 48],
    12: [3, 18, 33, 48],
    13: [0, 12, 24, 36, 48, 58],
    14: [8, 18, 27, 35, 43, 50, 58],
    15: [5, 13, 20, 28, 35, 43, 50, 58],
    16: [5, 13, 20, 28, 35, 43, 50, 58],
    17: [5, 13, 20, 28, 35, 43, 50, 58],
    18: [5, 13, 20, 28, 35, 43, 51, 59],
    19: [9, 19, 29, 41, 53],
    20: [6, 21, 36, 52],
    21: [8, 28, 48],
    22: [8, 28, 48],
    23: [8, 38],
}

scheduled_arrivals_saturday = {
    5: [8, 48],
    6: [8, 28, 48],
    7: [8, 28, 48],
    8: [8, 28, 47],
    9: [2, 17, 32, 47],
    10: [2, 17, 32, 47],
    11: [2, 17, 32, 47],
    12: [2, 17, 32, 47],
    13: [2, 17, 32, 47],
    14: [2, 17, 32, 47],
    15: [2, 17, 32, 47],
    16: [2, 17, 32, 47],
    17: [2, 17, 32, 47],
    18: [2, 17, 32, 47],
    19: [2, 17, 32, 47],
    20: [2, 17, 35, 50],
    21: [8, 28, 48],
    22: [8, 28, 48],
    23: [8, 38],
}

scheduled_arrivals_sundays = {
    5: [8, 48],
    6: [8, 28, 48],
    7: [8, 28, 48],
    8: [8, 28, 48],
    9: [8, 28, 48],
    10: [8, 28, 47],
    11: [2, 17, 32, 47],
    12: [2, 17, 32, 47],
    13: [2, 17, 32, 47],
    14: [2, 17, 32, 47],
    15: [2, 17, 32, 47],
    16: [2, 17, 32, 47],
    17: [2, 17, 32, 47],
    18: [2, 17, 32, 47],
    19: [2, 17, 32, 47],
    20: [2, 17, 35, 50],
    21: [8, 28, 48],
    22: [8, 28, 48],
    23: [8, 38],
}