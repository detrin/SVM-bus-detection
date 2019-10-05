import numpy as np
import cv2
import pickle
import time
import os
import sys
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
from sklearn.decomposition import PCA

def fd_hu_moments(image):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    feature = cv2.HuMoments(cv2.moments(image)).flatten()
    return feature

def fd_haralick(image):    # convert the image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # compute the haralick texture feature vector
    haralick = mahotas.features.haralick(gray).mean(axis=0)
    return haralick
 
def fd_histogram(image, mask=None, bins=(8, 8, 8)):
    # convert the image to HSV color-space
    image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    # compute the color histogram
    hist  = cv2.calcHist([image], [0, 1, 2], None, bins, [0, 256, 0, 256, 0, 256])
    # normalize the histogram
    cv2.normalize(hist, hist)
    return hist.flatten()

# Define a function to compute binned color features
def bin_spatial(img, size=(4, 8)):
	# Use cv2.resize().ravel() to create the feature vector
	features = cv2.resize(img, size).ravel()
	# Return the feature vector
	return features

def get_hog_features(img, orient, pix_per_cell, cell_per_block, feature_vec=True):
    features = hog(img, orientations=6, pixels_per_cell=(4, 4),
                cells_per_block=(5, 10), visualize=False, multichannel=False, block_norm='L2-Hys')
    return features

def create_features(images):
    print "Creating features ..."
    image = images[0]
    x_len, y_len = len(images), len(np.hstack([fd_histogram(image), fd_haralick(image), fd_hu_moments(image)]))
    for channel in range(image.shape[2]):
        hog_features = get_hog_features(image[:,:,channel],
                        orient, pix_per_cell, cell_per_block,
                        feature_vec=True)
        hog_features = np.ravel(hog_features)
        y_len += len(hog_features)
    global_features = np.zeros((x_len, y_len))
    for image_ind in tqdm(xrange(len(images))):
        image = images[image_ind]
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
        global_features[image_ind] = np.hstack([img_histogram, img_haralic, img_hu_moments, hog_features])
    print "Scaling features ..."
    scaler = MinMaxScaler(feature_range=(0, 1))
    # Normalize The feature vectors...
    rescaled_features = scaler.fit_transform(global_features)
    return rescaled_features, scaler

def save_model(svc, scaler, pca):
    with open('model.p', 'wb') as f:
        pickle.dump({'svc': svc, 'scaler': scaler, 'pca': pca}, f)

def train_model():
    DIR_YES = "training_img/201-yes/"
    DIR_NO = "training_img/no/"
    data = []
    print "Loading images from", DIR_YES
    for filename in tqdm(os.listdir(DIR_YES)):
        # image = mpimg.imread(os.path.join(DIR_YES, filename))
        image = cv2.imread(os.path.join(DIR_YES, filename))
        data.append([image, 1])

    print "Loading images from", DIR_NO
    for filename in tqdm(os.listdir(DIR_NO)[:1000]):
        # image = mpimg.imread(os.path.join(DIR_NO, filename))
        image = cv2.imread(os.path.join(DIR_NO, filename))
        data.append([image, 0])

    print "Shuffling data ..."
    random.shuffle(data)

    images, labels = [], []
    for row in data:
        images.append(row[0])
        labels.append(row[1])

    features, scaler = create_features(images)

    #Fitting the PCA algorithm with our Data
    pca = PCA().fit(features)#Plotting the Cumulative Summation of the Explained Variance
    plt.figure()
    plt.plot(np.cumsum(pca.explained_variance_ratio_))
    plt.xlabel('Number of Components')
    plt.ylabel('Variance (%)') #for each component
    plt.title('Pulsar Dataset Explained Variance')
    plt.show()
    
    print "Enter number of components for PCA: "
    comp_num = int(raw_input())

    pca = PCA(n_components=comp_num)
    features = pca.fit_transform(features)

    split = 0.8
    train_len = int(len(features)*split)
    train_data = features[:train_len]
    test_data = features[train_len:]

    train_labels= labels[:train_len]
    test_labels = labels[train_len:]

    print len(data)

    svc = LinearSVC(random_state=9)
    print "Training SVC ..."
    timeFlag = time.time()
    svc.fit(train_data, train_labels)
    print "SVC trained in", time.time() - timeFlag, "s"
    # Check the score of the SVC
    print 'Test Accuracy of SVC = ', round(svc.score(test_data, test_labels), 4)*100, "%"

    print "Saving model ..."
    save_model(svc, scaler, pca)

# train_model()