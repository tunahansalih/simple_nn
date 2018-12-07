import matplotlib
matplotlib.use('Agg')

import tensorflow as tf
from tensorflow import keras
from sklearn.preprocessing import LabelBinarizer
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import imutils
import matplotlib.pyplot as plt
import numpy as np
import argparse
import random
import pickle
import cv2
import os

ap = argparse.ArgumentParser()
ap.add_argument('-d', '--dataset', required=True, help='path to input dataset of images')
ap.add_argument('-m', '--model', required=True, help='path to output trained model')
ap.add_argument('-l', '--label-bin', required=True, help='path to output label binarizer')
ap.add_argument('-p', '--plot', required=True, help='path to output accuracy/loss plot')
args = vars(ap.parse_args())

dataset_file = args['dataset']
model_file = args['model']
label_binary_file = args['label_bin']
plot_file = args['plot']

print('[INFO] Loading images...')
data = []
labels = []

# Grab image paths
image_paths = sorted(list(imutils.paths.list_images(dataset_file)))
random.seed(53)
random.shuffle(image_paths)

# Read each image and resize it
for image_path in image_paths:
    image = cv2.imread(image_path)
    image = cv2.resize(image, (32,32)).flatten()
    data.append(image)

    # Push label data derived from path
    label = image_path.split(os.path.sep)[-2]
    labels.append(label)

data = np.array(data, dtype=float) / 255.0
labels = np.array(labels)

# One Hot encode the labels
binarizer = LabelBinarizer()
binarizer.fit_transform(labels)
