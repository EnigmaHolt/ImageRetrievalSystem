import PIL
import numpy as np
import cv2
import sys
from PIL import Image

# Fill the RGB file into the open method. That's it.
photo = open("Image1.rgb").read()
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
cv2.imshow('hello', im)
cv2.waitKey(3000)        
