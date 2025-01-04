#!/usr/bin/env python
# coding: utf-8

# In[1]:


####Tianrui Lai####
#####Feb 2023#####


# In[2]:


# -*- coding: UTF-8 -*-
import sys
import os
import cv2
import shutil
import math
import time
import numpy as np
import fitz


# In[3]:



# In[4]:



# Transform PDFs to Images
def pdfToImage(pdfFile, imagesDir, pageIndex=0): 
    doc=fitz.open(pdfFile)
    imgcount = 0
    for pg in range(doc.pageCount):
        imgcount += 1
        if pageIndex > 0 and (pg+1) != pageIndex:
            continue
        page = doc[pg]
        rotate = int(0)
        # Increase the resolution by 4 times
        zoom_x = 4.0
        zoom_y = 4.0
        trans = fitz.Matrix(zoom_x, zoom_y).preRotate(rotate)
        pm = page.getPixmap(matrix=trans, alpha=False)
        #generate the path to store image: imagesDir/picname
        pic_name = "pic{}.jpg".format("%03d"%imgcount)
        pic_pwd = os.path.join(imagesDir, pic_name)
        if not os.path.exists(pic_pwd):
            pm.writeImage(pic_pwd)
            #pm.writePNG(pic_pwd)
            
## imdecode read into rgb，need to transfer to grey picture for processing in opencv
##cv_img=cv2.cvtColor(cv_img,cv2.COLOR_RGB2BGR)            
def cv_imread(filePath):
    cv_img=cv2.imdecode(np.fromfile(filePath,dtype=np.uint8),-1)
    return cv_img

# Crop all images into family and address
def processAllImages(imageFile):
        srcMat = cv_imread(imageFile)
        img_h, img_w, img_c = srcMat.shape
        '''
        #Crop the edges of the image
        h, w, c = srcMat.shape
        cropMat = srcMat[10:h - 10, 10:w - 10]
        cv2.namedWindow("Original Image", cv2.WINDOW_NORMAL)
        cv2.imshow("Original Image", srcMat)
        cv2.waitKey(0)
        cv2.namedWindow("Cropped Image", cv2.WINDOW_NORMAL)
        cv2.imshow("Cropped Image", cropMat)
        cv2.waitKey(0)
        '''
        #Transfer to grey mat
        grayMat = cv2.cvtColor(srcMat, cv2.COLOR_BGR2GRAY)
        #Transfer to binary mat(black and white, and inverse)
        _, thresholdMat = cv2.threshold(grayMat, 130, 255, cv2.THRESH_BINARY_INV)
        
        #cv2.namedWindow("thresholdMat", cv2.WINDOW_NORMAL)
        #cv2.imshow("thresholdMat", thresholdMat)
        #cv2.waitKey(0)

        #Repair the broken lines
        dilateKernelSize = 4
        erodeKernelSize = 4
        thresholdMat = cv2.dilate(thresholdMat, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, [dilateKernelSize, dilateKernelSize]))
        thresholdMat = cv2.erode(thresholdMat, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, [erodeKernelSize, erodeKernelSize]))

        #cv2.namedWindow("thresholdMat", cv2.WINDOW_NORMAL)
        #cv2.imshow("thresholdMat", thresholdMat)
        #cv2.waitKey(0)

        #Identify the vertical lines
        contours, hierarchy = cv2.findContours(thresholdMat, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        validRects = []
        validContours = []
        if hierarchy is not None:
            #Iterate all the contours
            for i in range(len(hierarchy[0])):
                if hierarchy[0][i][3] == -1:
                    rect = cv2.minAreaRect(contours[i])
                    center, size, angle = rect[0], rect[1], rect[2]
                    #Coordination of the minimal bounding rectangles
                    pts_contour = cv2.boxPoints(rect).astype(np.int32)  
                    x, y, w, h= cv2.boundingRect(pts_contour)
                    #Identify the vertical lines
                    if h/w > 5:
                        validRects.append([x, y, x+w, y+h])
                        validContours.append(contours[i])

        validRects.sort(key=lambda x: x[1])
        #Concacte the broken edges
        i = 0
        while i < len(validRects) -1:
            # print(i)
            j = i + 1
            #print(j)
            # Calculate the distance between the contours
            x1i = validRects[i][0]
            y1i = validRects[i][1]
            x2i = validRects[i][2]
            y2i = validRects[i][3]
            x1j = validRects[j][0]
            y1j = validRects[j][1]
            x2j = validRects[j][2]
            y2j = validRects[j][3]
            xi = (validRects[i][0] + validRects[i][2]) / 2
            yi = validRects[i][3]
            xj = (validRects[j][0] + validRects[j][2]) / 2
            yj = validRects[j][1]
            #cv2.circle(srcMat, (int(xi), int(yi)), 5, (0, 0, 255), -1)
            #cv2.circle(srcMat, (int(xj), int(yj)), 5, (0, 0, 255), -1)
            #cv2.namedWindow("Points", cv2.WINDOW_NORMAL)
            #cv2.imshow("Points", srcMat)
            #cv2.waitKey(0)
            dist = cv2.norm((xi, yi), (xj, yj))
            #print(dist)
            # Calculate the nearest distance between two contours
            # dist_transform_i = cv2.distanceTransform(
            #    np.uint8(cv2.drawContours(np.zeros_like(thresholdMat), [validRects[j]], 0, 255, -1)), cv2.DIST_L2, 3)
            # dist_transform_j = cv2.distanceTransform(
            #    np.uint8(cv2.drawContours(np.zeros_like(thresholdMat), [validRects[j]], 0, 255, -1)), cv2.DIST_L2, 3)
            # dist = np.min(dist_transform_i[dist_transform_j > 0])

            ###Key variable: The distance of linking two vertical lines into one
            if dist < 10:
                validRects[i] = [min(x1i, x1j), min(y1i, y1j), max(x2i, x2j), max(y2i, y2j)]
                validRects.pop(j)
                validContours.pop(j)
            else:
                i += 1

            #printingcontours = []
            #for rect in validRects:
                #x1, y1, x2, y2 = rect
                #printingcontour = np.array([[(x1, y1)], [(x2, y1)], [(x2, y2)], [(x1, y2)]])
                #printingcontours.append(printingcontour)
            #cv2.drawContours(srcMat, printingcontours, -1, (255, 0, 0), 3)
            #cv2.namedWindow("Contours", cv2.WINDOW_NORMAL)
            #cv2.imshow("Contours", srcMat)
            #cv2.waitKey(0)

        validRects.sort(key=lambda x: x[1])
        i = 1
        finalRects = []
        #print(validRects)
        for everyRect in validRects:

            ###Key Variable: Set the ratio of height and width to identify the vertical lines
            if len(everyRect) != 0 and 10 < (everyRect[3]-everyRect[1])/(everyRect[2]-everyRect[0]) < 200\
                    and 120 < everyRect[0] < img_w -50:
                finalRects.append(everyRect)
                try:
                    #Crop out the left and right side of the vertical line, then cover it with blanks
                    left = srcMat[everyRect[1]-4:everyRect[3],0:everyRect[0]]
                    leftname = os.path.join(picDir,"L"+imageFile[-7:-4]+str(i).zfill(2)+".png")
                    cv2.imencode('.png', left)[1].tofile(leftname)
                    #cv2.imwrite(leftname,left)
                    cv2.rectangle(srcMat, (0, everyRect[1]-4), (everyRect[0], everyRect[3]), (255, 255, 255), thickness=-1)
                    right = srcMat[everyRect[1]-4:everyRect[3], everyRect[0]:srcMat.shape[1]]
                    rightname = os.path.join(picDir,"R"+imageFile[-7:-4]+str(i).zfill(2)+".png")
                    cv2.imencode('.png', right)[1].tofile(rightname)
                    #cv2.imwrite(rightname,right)
                    cv2.rectangle(srcMat, (everyRect[0], everyRect[1]-4), (srcMat.shape[1], everyRect[3]), (255, 255, 255), thickness=-1)
                    i += 1
                    ### Old method: cover the right with new letters
                    #srcMat =cv2.putText(srcMat, startSymbol, (everyRect[2], everyRect[1]+34), cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0, 0, 0), 4)
                    #srcMat =cv2.putText(srcMat, endSymbol, (everyRect[2], everyRect[3]-10), cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0, 0, 0), 4)
                except:
                    pass

        printingcontours = []
        for rect in finalRects:
            x1, y1, x2, y2 = rect
            printingcontour = np.array([[(x1, y1)], [(x2, y1)], [(x2, y2)], [(x1, y2)]])
            printingcontours.append(printingcontour)

        #Save the transformed images
        cv2.imencode('.png', srcMat)[1].tofile(imageFile)
        #cv2.drawContours(srcMat, printingcontours, -1, (0, 0, 255), 3)
        #boundary = np.array([[(120, 0), (121, 0), (120, img_h), (121, img_h)],
        #                    [(img_w - 50, 0), (img_w - 49, 0), (img_w - 50, img_h), (img_w - 49, img_h)]])
        #cv2.drawContours(srcMat, boundary, -1, (0, 0, 255), 3)
        #cv2.namedWindow("OriginMat", cv2.WINDOW_NORMAL)
        #cv2.imshow("OriginMat", srcMat)
        #cv2.waitKey(0)

        ### Show the image if there is an error
        #cv2.drawContours(thresholdMat, validContours, -1, (0, 0, 255), 1)
        #cv2.namedWindow("thresholdMat", cv2.WINDOW_NORMAL)
        #cv2.imshow("thresholdMat", thresholdMat)
        #cv2.waitKey(0)
        

        
            
                    


# In[5]:


### Need to specify your path
# Transform the pdf into images
for filepath,filedirs,files in os.walk("C:\\Users\\87208\\Documents\\Documents\\RA\\Social register\\pdf_ny"):
    for file in files:
        inputPdfFile = os.path.join(filepath,file)
        imagesDir = os.path.join("C:\\Users\\87208\\Documents\\Documents\\RA\\Social register\\images_single_new",file[:-4])
        if os.path.exists(imagesDir):
            shutil.rmtree(imagesDir)
        os.makedirs(imagesDir)
        pdfToImage(inputPdfFile, imagesDir, 0)
'''
# Crop the images into small pieces
        picDir = os.path.join( "C:\\Users\\87208\\Documents\\Documents\\RA\\Social register\\images_household_new",file[:-4])
        #Delete the path if it preexist
        if os.path.exists(picDir):
            shutil.rmtree(picDir)
        os.makedirs(picDir)
        for imagepath,imagedirs,images in os.walk(imagesDir):
            for image in images:
                imageFile = os.path.join(imagepath,image)
                processAllImages(imageFile)

'''
# In[ ]:




