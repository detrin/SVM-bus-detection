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
from sklearn.preprocessing import MinMaxScaler
from skimage.feature import hog
from scipy.ndimage.measurements import label
from settings import *
from tqdm import tqdm
import mahotas
import random
from sklearn.svm import SVC
from train import fd_hu_moments, fd_haralick, fd_histogram, get_hog_features
from shutil import copyfile
from create_input import slide_window
import pytesseract
import datetime
from database_manipulation import *
import sqlite3

def create_features_single(image, scaler, pca):
    img_histogram = fd_histogram(image)
    img_haralic = fd_haralick(image)
    img_hu_moments = fd_hu_moments(image)
    hog_features = []
    for channel in range(image.shape[2]):
        hog_features.append(get_hog_features(image[:,:,channel],
                            orient, pix_per_cell, cell_per_block,
                            feature_vec=True))
    # hog_features = np.array(hog_features)
    hog_features = np.ravel(hog_features)
    # print len(img_histogram), len(img_haralic), len(img_hu_moments), len(hog_features)
    global_features = np.hstack([img_histogram, img_haralic, img_hu_moments, hog_features])
    # Normalize The feature vectors...
    rescaled_features = scaler.transform([global_features])
    reduced_features = pca.transform(rescaled_features)
    return reduced_features[0]

def load_model():
    with open('model.p', 'rb') as f:
        save_dict = pickle.load(f)
    svc = save_dict['svc']
    scaler = save_dict['scaler']
    pca = save_dict['pca']
    return svc, scaler, pca

def edge_detection(img):
    # Apply gray scale
    gray_img = np.round(0.299 * img[:, :, 0] +
                        0.587 * img[:, :, 1] +
                        0.114 * img[:, :, 2]).astype(np.uint8)

    # Sobel Operator
    h, w = gray_img.shape
    # define filters
    horizontal = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]])  # s2
    vertical = np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]])  # s1

    # define images with 0s
    newhorizontalImage = np.zeros((h, w))
    newverticalImage = np.zeros((h, w))
    newgradientImage = np.zeros((h, w))

    # offset by 1
    for i in range(1, h - 1):
        for j in range(1, w - 1):
            horizontalGrad = (horizontal[0, 0] * gray_img[i - 1, j - 1]) + \
                            (horizontal[0, 1] * gray_img[i - 1, j]) + \
                            (horizontal[0, 2] * gray_img[i - 1, j + 1]) + \
                            (horizontal[1, 0] * gray_img[i, j - 1]) + \
                            (horizontal[1, 1] * gray_img[i, j]) + \
                            (horizontal[1, 2] * gray_img[i, j + 1]) + \
                            (horizontal[2, 0] * gray_img[i + 1, j - 1]) + \
                            (horizontal[2, 1] * gray_img[i + 1, j]) + \
                            (horizontal[2, 2] * gray_img[i + 1, j + 1])

            newhorizontalImage[i - 1, j - 1] = abs(horizontalGrad)

            verticalGrad = (vertical[0, 0] * gray_img[i - 1, j - 1]) + \
                        (vertical[0, 1] * gray_img[i - 1, j]) + \
                        (vertical[0, 2] * gray_img[i - 1, j + 1]) + \
                        (vertical[1, 0] * gray_img[i, j - 1]) + \
                        (vertical[1, 1] * gray_img[i, j]) + \
                        (vertical[1, 2] * gray_img[i, j + 1]) + \
                        (vertical[2, 0] * gray_img[i + 1, j - 1]) + \
                        (vertical[2, 1] * gray_img[i + 1, j]) + \
                        (vertical[2, 2] * gray_img[i + 1, j + 1])

            newverticalImage[i - 1, j - 1] = abs(verticalGrad)

            # Edge Magnitude
            mag = np.sqrt(pow(horizontalGrad, 2.0) + pow(verticalGrad, 2.0))
            newgradientImage[i - 1, j - 1] = mag
    return newgradientImage

def get_pic_time(img):
    x_start, x_stop = 145, 213
    y_start, y_stop = 0, 14
    img_time = img[y_start:y_stop+1, x_start:x_stop+1, :]
    # mpimg.imsave("text.jpg", img_time)
    # img_time = edge_detection(img_time)
    # mpimg.imsave("text.jpg", img_edges)
    text = pytesseract.image_to_string(img_time)
    return text

def test_image(img):
    predictions = []
    img_windows = slide_window(image, (317, 295), (399, 283))
    for ind in xrange(len(img_windows)):
        img_window = img_windows[ind]
        features = create_features_single(img_window, scaler, pca)
        predictions.append(str(svc.predict([features])[0]))
    return predictions
    

def sort_images():
    PATH_SORT = "training_img/sort/"
    PATH_YES = "training_img/sort-yes/"
    PATH_NO = "training_img/sort-no/"
    data = []
    print "Sorting images from", PATH_SORT
    for filename in tqdm(os.listdir(PATH_SORT)):
        # image = mpimg.imread(os.path.join(DIR_YES, filename))
        image = cv2.imread(os.path.join(PATH_SORT, filename))
        features = create_features_single(image, scaler, pca)
        prediction = svc.predict([features])
        # print prediction[0]
        if prediction[0] == 0:
            copyfile(os.path.join(PATH_SORT, filename), os.path.join(PATH_NO, filename))
        else:
            copyfile(os.path.join(PATH_SORT, filename), os.path.join(PATH_YES, filename))

conn = sqlite3.connect('db/db01.sqlite')
cursor = conn.cursor()

svc, scaler, pca = load_model()

PATH_TEST = "test_images/"
PATH_NEW_POSITIVE = "training_images/new-yes/"
state = True
for image_file in os.listdir(PATH_TEST):
    image = cv2.imread(PATH_TEST+image_file)
    predictions = test_image(image)
    time_text = get_pic_time(image)
    time_str = datetime.datetime.now()
    time_str = time_str.strftime('%H:%M:%S')
    if ":" not in time_text or time_text.count(":") != 2:
        hours = int(time_str.split(':')[0])
        seconds = 3600*hours + int(time_str.split(':')[1])*60 + int(time_str.split(':')[2])

        time_diff = get_timediff(conn)

        result = seconds - time_diff
        time_text = time_str.split(':')[0]+":"
        result %= 3600
        time_text += str(result/60)+":"
        result %= 60
        time_text += str(result)
    else:
        seconds = int(time_text.split(':')[1])*60 + int(time_text.split(':')[2])
        time_now = datetime.datetime.now()
        time_now = time_now.strftime('%H:%M:%S')
        seconds_now = int(time_now.split(':')[1])*60 + int(time_now.split(':')[2])
        result = seconds_now - seconds
        if result < 0:
            result = 3600 - result
        result = str(result)

        update_flag(conn, "StreamDelay", str(result))
        if int(time_str.split(':')[0]) - int(time_text.split(':')[0]) not in [0, 1]:
            time_text = time_str.split(':')[0]+":"+time_text.split(':')[1]+":"+time_text.split(':')[2]

    if "1" in predictions:
        insert_new_arrival(conn, time_text)
        copyfile(os.path.join(PATH_TEST, image_file), os.path.join(PATH_NEW_POSITIVE, time_text+"_"+image_file))
    else:
        check_arrival(conn, time_text)