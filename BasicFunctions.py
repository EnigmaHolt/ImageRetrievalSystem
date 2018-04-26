

import PIL
import numpy as np
import cv2
import sys
from matplotlib import pyplot as plt
from PIL import Image


def readImage(path):
    photo = open(path).read()
    source = bytearray()
    source.extend(photo)
    w, h = 352, 288;

    rMatrix = [[0 for x in range(w)] for y in range(h)]
    gMatrix = [[0 for x in range(w)] for y in range(h)]
    bMatrix = [[0 for x in range(w)] for y in range(h)]

    #Extract the R,G,B values from the file.
    index = 0
    for i in range(0, 288):
        for j in range(0, 352):
            rMatrix[i][j] = source[index]
            gMatrix[i][j] = source[index + 288 * 352]
            bMatrix[i][j] = source[index + 288 * 352 * 2]
            index = index + 1
        
    #Convert arrays into numpy array in byte format.
    b = np.array(bMatrix, dtype=np.uint8)
    r = np.array(rMatrix, dtype=np.uint8)
    g = np.array(gMatrix, dtype=np.uint8)

    #Merge three channels and display!
    im = cv2.merge((b, g, r))       
    return im;

# If user wants to display a specific image, use this method.
def displayImage(image, time, message):
    cv2.imshow(message, image)
    cv2.waitKey(time)        
    return;

# Range of similarity is 0-1. 1 means two are the same pictures.
def colorSimilarity(image1, image2):
    hist1 = cv2.calcHist([image1], [0], None, [256], [0, 256])
    hist2 = cv2.calcHist([image2], [0], None, [256], [0, 256])
    result = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)
    return result;

# Given a list of images in OpenCV format, convert them into a 30 fps video into a specified path.
def convertToVideo(imageList, path):
    out = cv2.VideoWriter(path, -1, 30.0, (352, 288))
    for image in imageList:
        out.write(image)
    out.release()
    return;

# Given a path, read all images in that path. Mode-0 means Database Videos including 600 frames, Mode-1 means 150-frame Query Video. 
def readAllImages(path, mode):
    imageList = []
    fileName = path
    if mode == 0:
        for index in range(1, 601):
            if index > 99:
                fileName = path + str(index) + ".rgb"
            elif index > 9:
                fileName = path + "0" + str(index) + ".rgb"
            elif index > 0:
                fileName = path + "00" + str(index) + ".rgb"
            image = readImage(fileName)
            imageList.append(image)
                    
    elif mode == 1:
        for index in range(1, 151):
            if index > 99:
                fileName = path + str(index) + ".rgb"
            elif index > 9:
                fileName = path + "0" + str(index) + ".rgb"
            elif index > 0:
                fileName = path + "00" + str(index) + ".rgb"
            image = readImage(fileName)
            imageList.append(image)
            
    return imageList;

# Test Code(Passed on Apr,19th)
imL = readAllImages("/Users/leichen/Desktop/sports/sports", 0)
convertToVideo(imL, "output.mov")