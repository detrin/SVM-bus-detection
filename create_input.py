import numpy as np
import cv2
import pickle
import time
import os
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from sklearn.model_selection import train_test_split
from sklearn.svm import LinearSVC
from sklearn.preprocessing import StandardScaler
from skimage.feature import hog
from scipy.ndimage.measurements import label
from settings import *
from tqdm import tqdm


def slide_window(img, pt_start, pt_stop,
					window_size=(40, 20), N=10):
    dx, dy = pt_stop[0]-pt_start[0], pt_stop[1]-pt_start[1]
    ratio = dy/float(dx)
    x_step = dx/N
    windows = []
    for dx_pos in xrange(0, dx, x_step):
        x_pos = pt_start[0]+dx_pos
        y_pos = int(pt_start[1]+dx_pos*ratio)
        windows.append(img[y_pos:y_pos+window_size[1], x_pos:x_pos+window_size[0]])
    return windows

def create_input_from_dirs():
    train_img_ID = 0
    PATH_LOAD = 'input_img/'
    PATH_SAVE = 'training_img/no/'
    image_file = os.listdir(PATH_LOAD)[0]
    for time_stamp in tqdm(os.listdir(PATH_LOAD)):
        for image_file in os.listdir(PATH_LOAD+time_stamp):
            image = mpimg.imread(os.path.join(PATH_LOAD, time_stamp, image_file))
            img_windows = slide_window(image, (317, 295), (399, 283))
            for ind in xrange(len(img_windows)):
                filename = os.path.join(PATH_SAVE, time_stamp.replace("/", "")+"_"+image_file[:-4]+"_"+str(ind)+".png")
                img_window = img_windows[ind]
                mpimg.imsave(filename, img_window)
            
# create_input_from_dirs()