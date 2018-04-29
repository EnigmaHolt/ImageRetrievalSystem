import PIL
import numpy as np
import cv2
import json
import math
import sys
from matplotlib import pyplot as plt
from PIL import Image
from decimal import Decimal

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

# Calculate the overall color similarity in a group of frames.
def calGroupColorSimilarty(queryList, dataList, startQ, startD, sub):
    resultArray = []
    result = 0.0
    sampleCount = 0
    while startQ < len(queryList) and startD < len(dataList):
        result = result + colorSimilarity(queryList[startQ], dataList[startD])
        startQ = startQ + sub
        startD = startD + sub
        sampleCount = sampleCount + 1
    if sampleCount != 0 and result >= 0:
        result = result / sampleCount
    else:
        result = 0.0
    return result;

# Range of similarity is 0-1. 1 means two are the same pictures.
def colorSimilarity(image1, image2):
    hist1 = cv2.calcHist([image1], [0], None, [256], [0, 256])
    hist2 = cv2.calcHist([image2], [0], None, [256], [0, 256])
    hist3 = cv2.calcHist([image1], [1], None, [256], [0, 256])
    hist4 = cv2.calcHist([image2], [1], None, [256], [0, 256])
    hist5 = cv2.calcHist([image1], [2], None, [256], [0, 256])
    hist6 = cv2.calcHist([image2], [2], None, [256], [0, 256])
    result = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL) + cv2.compareHist(hist3, hist4, cv2.HISTCMP_CORREL) +cv2.compareHist(hist5, hist6, cv2.HISTCMP_CORREL)
    result = result / 3.0
    return result;

# Given a list of images in OpenCV format, convert them into a 30 fps video into a specified path.
def convertToVideo(imageList, path):
    out = cv2.VideoWriter(path, -1, 30.0, (352, 288))
    for image in imageList:
        out.write(image)
    out.release()
    return;

# Given a path, read all images in that path. Mode-0 means Database Videos including 600 frames, Mode-1 means 150-frame Query Video. 
def readAllImages(path, mode, sub):
    imageList = []
    fileName = path
    index = 1
    if mode == 0:
        while index < 601:
            #print(index)
            if index > 99:
                fileName = path + str(index) + ".rgb"
            elif index > 9:
                fileName = path + "0" + str(index) + ".rgb"
            elif index > 0:
                fileName = path + "00" + str(index) + ".rgb"
            image = readImage(fileName)
            imageList.append(image)
            index = index + sub
                    
    elif mode == 1:
        while index < 151:
            if index > 99:
                fileName = path + str(index) + ".rgb"
            elif index > 9:
                fileName = path + "0" + str(index) + ".rgb"
            elif index > 0:
                fileName = path + "00" + str(index) + ".rgb"
            image = readImage(fileName)
            imageList.append(image)
            index = index + sub
            
    return imageList;

# Return the matching tuples for 2 images.
def featureMatch(img1, img2):
    # Initiate SIFT detector
    orb = cv2.ORB_create()

    # find the keypoints and descriptors with SIFT
    kp1, des1 = orb.detectAndCompute(img1,None)
    kp2, des2 = orb.detectAndCompute(img2,None)

    # create BFMatcher object
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

    # Match descriptors.
    matches = bf.match(des1,des2)

    # Sort them in the order of their distance.
    matches = sorted(matches, key = lambda x:x.distance)
    
    return matches;

def generateMotion(path, size):
    cap = cv2.VideoCapture(path)
    feature_params = dict(maxCorners = 1000,
                           qualityLevel = 0.000001,
                           minDistance = 3,
                           blockSize = 2)

    lk_params = dict(winSize = (8, 8),
                     maxLevel = 4,
                     criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))

    color = np.random.randint(0, 255, (200,3))

    ret, old_frame = cap.read()
    old_gray = cv2.cvtColor(old_frame, cv2.COLOR_BGR2GRAY)
    p0 = cv2.goodFeaturesToTrack(old_gray, mask = None, **feature_params)

    mask = np.zeros_like(old_frame)
    test = [0, 0, 0, 0, 0, 0, 0, 0, 0]
    number = 1
    while(1):
        ret,frame = cap.read()
        frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # calculate optical flow
        p1, st, err = cv2.calcOpticalFlowPyrLK(old_gray, frame_gray, p0, None, **lk_params)
        if number == size - 1:
            break;
        # Select good points
        good_new = p1[st==1]
        good_old = p0[st==1]
        #print(number)
        number = number + 1
        # draw the tracks
        test[len(test) - 1] = test[len(test) - 1] + len(good_old)
        for i,(new,old) in enumerate(zip(good_new,good_old)):
            a,b = new.ravel()
            c,d = old.ravel()
            raw = round(calculateAngle(c, d, a, b) / 45)
            angle = raw * 45
            if calculateAngle(c, d, a, b) >= 0 :
                #print(round(calculateAngle(c, d, a, b)/ 45))
                test[int(raw)] = test[int(raw)] + 1
            #mask = cv2.line(mask, (a,b),(c,d), color[i].tolist(), 2)
            #frame = cv2.circle(frame,(a,b),5,color[i].tolist(),-1)
        #img = cv2.add(frame,mask)
        
        #cv2.imshow('frame',frame)
        k = cv2.waitKey(30) & 0xff
        #if k == 30:
            #break
        # Now update the previous frame and previous points
        old_gray = frame_gray.copy()
        p0 = good_new.reshape(-1,1,2)
        if len(p0) < 10:
            break;
    cv2.destroyAllWindows()
    #plt.plot(test)
    #plt.show()
    cap.release()
    return test;


def calculateAngle(a, b, x, y):
    if round(a, 2) == round(x, 2) and round(b, 2) == round(y, 2):
        return -1.0;
    if round(y,2) == round(b,2):
        if round(a, 2) < round(x, 2) :
            return 0.0;
        elif round(a, 2) > round(x, 2):
            return 180.0;
    short = y - b
    #print(str(y) + ",," + str(b))
    long = math.sqrt((y - b) * (y - b) + (x - a) * (x - a))
    if long < 1:
        return -2;
    if round(short,2) == round(long, 2):
        return 90;
    elif round(short,2) == -round(long, 2):
        return 270;
    #print(str(short) + "," + str(long))
    result = math.degrees(math.asin(abs(short) / long))
    if y - b >= 0 and x - a <= 0:
        result = result + 90
    elif y - b <= 0 and x - a <= 0:
        result = result + 180
    elif y - b <= 0 and x - a >= 0:
        result = result + 270
    return result;

def convertSegmentsAndAnalysis(segments, imL, name):
    number = 0
    results = []
    for index in range(0, len(segments)):
        convertToVideo(imL[segments[index][0]: segments[index][1]], name + str(number) + ".mov")
        result = generateMotion(name + str(number) + ".mov", segments[index][1] - segments[index][0])
        number = number + 1
        result.append(segments[index][0])
        result.append(segments[index][1])
        results.append(result)
    return results;

def detectKeyFrame(imageList):
    keyIndex = 0
    result = []
    for i in range(0, 150):
        if i == keyIndex:
            continue;
        img = imageList[i]
        similar = colorSimilarity(imageList[i], imageList[keyIndex])
        if similar >= 0.6:
            continue;
        elif similar < 0.6:
            if i - keyIndex >=10:
                result.append([keyIndex, i - 1])
            keyIndex = i
    if 150 - keyIndex >= 10:
                result.append([keyIndex, 150])
    print(result)
    return result;    

def getMotionSimilarity(path):
    result = {}
    imL = readAllImages(path, 1, 1)
    clipResult = convertSegmentsAndAnalysis(detectKeyFrame(imL), imL, path)
    result["musicvideo"] = compareSingleClip(clipResult, json.load(open('dataVideo.json'))["musicvideo"])
    result["starCraft"] = compareSingleClip(clipResult, json.load(open('dataVideo.json'))["starCraft"])
    result["movie"] = compareSingleClip(clipResult, json.load(open('dataVideo.json'))["movie"])
    result["interview"] = compareSingleClip(clipResult, json.load(open('dataVideo.json'))["interview"])
    result["flowers"] = compareSingleClip(clipResult, json.load(open('dataVideo.json'))["flowers"])
    result["sports"] = compareSingleClip(clipResult, json.load(open('dataVideo.json'))["sports"])
    result["traffic"] = compareSingleClip(clipResult, json.load(open('dataVideo.json'))["traffic"])
    #print(sum(result["musicvideo"]))
    #print(sum(result["starCraft"]))
    #print(sum(result["movie"]))
    #print(sum(result["interview"]))
    #print(sum(result["flowers"]))
    #print(sum(result["sports"]))
    #print(sum(result["traffic"]))
    return result;
    
def compareSingleClip(queryData, dataInfo):
    result = []
    for i in range(0, 600):
        result.append(0) 
    for index in range(0, len(queryData)):
        for dataClip in range(0, len(dataInfo)):
            querySize = queryData[index][10] - queryData[index][9]
            dataSize = dataInfo[dataClip]["end"] - dataInfo[dataClip]["start"]
            similar = 0.0
            for angle in range(0, 8):
                queryAngle = queryData[index][angle] * 1.0 / queryData[index][8]
                dataAngle = dataInfo[dataClip]["directions"][angle]* 1.0 / dataInfo[dataClip]["directions"][8]
                if queryAngle == 0.0:
                    if dataAngle == 0.0:
                        similar = similar + 1
                error = abs(queryAngle - dataAngle) * 1.0 / queryAngle
                if error > 1:
                    continue;
                similar = 1 - error + similar
            similar = similar / 8.0
            for add in range(dataInfo[dataClip]["start"], dataInfo[dataClip]["end"] + 1):
                result[add] = result[add] + similar
        
        
        for i in range(0, 600):
            result[i] = result[i] / len(queryData)
        return result;

def compareSingleColor(queryList, dataList):
    result = []
    finalResult = []
    for i in range(0, 75):
        result.append(calGroupColorSimilarty(queryList, dataList, 0, i, 1))
    index = 1
    while index <= 593:
        if (index - 1) % 8 == 0:
            finalResult.append(result[(index - 1) / 8])
        elif (index - 1) % 8 != 0:
            finalResult.append((8 - (index - 1) % 8) / 8.0 * result[(index - 1) / 8] + ((index - 1) % 8) / 8.0 * result[(index - 1) / 8 + 1])
        index = index + 1
    while len(finalResult) < 600:
        finalResult.append((finalResult[len(finalResult) - 1] + finalResult[len(finalResult) - 2]) / 2.0)
        if finalResult[len(finalResult) - 1] >= 1:
            finalResult[len(finalResult) - 1] = 1
    return finalResult;
    
    
def getColorSimilarity(dataVideoFolder, queryPath):
    result = {}
    imR = readAllImages(queryPath, 1, 8)
    imL = readAllImages(dataVideoFolder + "/flowers/flowers", 0, 8)
    result["flowers"] = compareSingleColor(imR, imL)
    #print(sum(result["flowers"]))
    imL = readAllImages(dataVideoFolder + "/musicvideo/musicvideo", 0, 8)
    #result["musicvideo"] = compareSingleColor(imR, imL)
    print(sum(result["musicvideo"]))
    imL = readAllImages(dataVideoFolder + "/starcraft/starCraft", 0, 8)
    result["starCraft"] = compareSingleColor(imR, imL)
    #print(sum(result["starCraft"]))
    imL = readAllImages(dataVideoFolder + "/movie/movie", 0, 8)
    result["movie"] = compareSingleColor(imR, imL)
    #print(sum(result["movie"]))
    imL = readAllImages(dataVideoFolder + "/traffic/traffic", 0, 8)
    result["traffic"] = compareSingleColor(imR, imL)
    #print(sum(result["traffic"]))
    imL = readAllImages(dataVideoFolder + "/sports/sports", 0, 8)
    result["sports"] = compareSingleColor(imR, imL)
    #print(sum(result["sports"]))
    imL = readAllImages(dataVideoFolder + "/interview/interview", 0, 8)
    result["interview"] = compareSingleColor(imR, imL)
    #print(sum(result["interview"]))
    return result;

# The parameter is the path of query video! WATCH the _ after Q4!!!
getMotionSimilarity("/Users/leichen/Desktop/Q4/Q4_")

# The first param is the FOLDER you store ALL database videos! 
# The second is the path of query video, WATCH the _ after HQ1!!!
getColorSimilarity("/Users/leichen/Desktop", "/Users/leichen/Desktop/HQ2/HQ2_")

