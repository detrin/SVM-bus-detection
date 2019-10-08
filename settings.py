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
maximum_stop = 30

scheduled_arrivals_workdays = {
    4: [48],
    5: [16, 35, 47, 57],
    6: [7, 17, 27, 34, 40, 46, 52, 58,],
    7: [4, 11, 19, 26, 32, 38, 45, 51, 57],
    8: [3, 9, 15, 21, 27, 33, 39, 45, 51, 57],
    9: [4, 11, 20, 30, 40, 55],
    10: [4, 11, 20, 30, 40, 55],
    11: [10, 25, 40, 55],
    12: [10, 25, 40, 55],
    13: [10, 25, 40, 55],
    14: [0, 10, 19, 27, 35, 42, 50, 57],
    15: [5, 12, 19, 27, 35, 42, 50, 57],
    16: [5, 12, 19, 27, 35, 42, 50, 57],
    17: [5, 12, 19, 27, 35, 42, 50, 57],
    18: [5, 12, 19, 27, 35, 42, 48, 55],
    19: [3, 9, 17, 24, 32, 40, 48, 58],
    20: [8, 18, 30, 42, 55],
    21: [9, 24, 39, 54],
    22: [14, 34, 54],
    23: [14, 34, 54],
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