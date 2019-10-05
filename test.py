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

def get_pic_time(img):
    x_start, x_stop = 145, 213
    y_start, y_stop = 0, 14
    img_time = img[y_start:y_stop+1, x_start:x_stop+1, :]
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
    
    
svc, scaler, pca = load_model()

'''
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
'''

PATH_TEST = "test_images/"
PATH_NEW_POSITIVE = "training_images/new-yes/"
state = True
for image_file in os.listdir(PATH_TEST):
    image = cv2.imread(PATH_TEST+image_file)
    predictions = test_image(image)
    time = get_pic_time(image)
    with open("prediction.csv", "a") as f:
        f.write(";".join(predictions)+";"+time+"\n")
    if "1" in predictions:
        copyfile(os.path.join(PATH_TEST, image_file), os.path.join(PATH_NEW_POSITIVE, image_file))