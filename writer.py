from cv2 import *
import math
import time
import sys
t0 = time.clock() ##initiate timer

height = 240
width = 320

capture=cv.CaptureFromCAM(1) ##run from camera
cv.SetCaptureProperty(capture, cv.CV_CAP_PROP_FRAME_WIDTH, width)
cv.SetCaptureProperty(capture, cv.CV_CAP_PROP_FRAME_HEIGHT, height)

#capture = cv.CaptureFromFile('http://10.38.47.133/GetStream') ##run from video
#capture=cv.CaptureFromFile('vision.mp4')
if capture is None:
    print 'No capture found!'
    exit


##Font, fourcc, fps, and writer are all used to save processed video
font = cv.InitFont(cv.CV_FONT_HERSHEY_PLAIN, 1.0, 1.0, 0, 1, cv.CV_AA);
fourcc = cv.CV_FOURCC('M', 'J', 'P', 'G')
fps = 30
writer = cv.CreateVideoWriter('calibrate1.avi', 0, fps, (width, height), 1)

t = time.clock()

while t-t0  <= 180:
    t = time.clock()
    rawImage = cv.QueryFrame(capture)
    cv.WriteFrame(writer, rawImage)
del(capture)
del(writer)

t = time.clock()
print t - t0 ,'seconds ellapsed'
