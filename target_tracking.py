from cv2 import *
import math
import time
import sys
t0 = time.clock() ##initiate timer
print "Please adjust values, then press ESC to begin, and ESC again to exit."

"""
Instantiate a bunch of variables
"""
height = 240
width = 320

capture=cv.CaptureFromCAM(1) ##run from camera
cv.SetCaptureProperty(capture, cv.CV_CAP_PROP_FRAME_WIDTH, width)
cv.SetCaptureProperty(capture, cv.CV_CAP_PROP_FRAME_HEIGHT, height)
cv.SetCaptureProperty(capture, cv.CV_CAP_PROP_SATURATION, 255)

#capture = cv.CaptureFromFile('http://10.38.47.133/GetStream') ##run from video
#capture=cv.CaptureFromFile('vision.mp4')
if capture is None:
    print 'No capture found!'
    exit


##Font, fourcc, fps, and writer are all used to save processed video
font = cv.InitFont(cv.CV_FONT_HERSHEY_PLAIN, 1.0, 1.0, 0, 1, cv.CV_AA);
fourcc = cv.CV_FOURCC('M', 'J', 'P', 'G')
fps = 60
writer = cv.CreateVideoWriter('compression4.avi', 0, fps, (width, height), 1)

##varying depths for the images: depth 3 means 3 channels, depth 1 means a binary image
depth1 = cv.CV_8UC1
depth3 = cv.CV_8UC3

##Images to be used during processing
hsvImage = cv.CreateMat(height,width, depth3)
filteredImage = cv.CreateMat(height,width, depth3)
binImage = cv.CreateMat(height,width, depth1)

##individual HSV channels
hue = cv.CreateMat(height, width, depth1)
sat = cv.CreateMat(height, width, depth1)
val = cv.CreateMat(height, width, depth1)

##just some global colors for ease of use
r =  (0, 0, 255, 0);
g =  (0, 255, 0, 0);
w = cv.RGB(255,255,255)
b = cv.RGB(0,0,0)

cv.NamedWindow('Filtered', cv.CV_WINDOW_AUTOSIZE)
cv.NamedWindow('Camera', cv.CV_WINDOW_AUTOSIZE)
cv.NamedWindow('HueSatVal', cv.CV_WINDOW_AUTOSIZE)

##cv.NamedWindow('Hue Filter', cv.CV_WINDOW_NORMAL)
##cv.NamedWindow('Sat Filter', cv.CV_WINDOW_NORMAL)
##cv.NamedWindow('Val Filter', cv.CV_WINDOW_NORMAL)

def changeUpperHueval(x):
    return
def changeUpperSatval(x):
    return
def changeUpperValval(x):
    return
def changeLowerHueval(x):
    return
def changeLowerSatval(x):
    return
def changeLowerValval(x):
    return
def delay(x):
    return
def dilate(x):
    return
def approx(x):
    return
def saturation(x):
    return
def contrast(x):
    return

cv.CreateTrackbar('UpperHue', 'HueSatVal', 0, 255, changeUpperHueval)
cv.CreateTrackbar('LowerHue', 'HueSatVal', 0, 255, changeLowerHueval)
cv.CreateTrackbar('UpperSat', 'HueSatVal', 0, 255, changeUpperSatval)
cv.CreateTrackbar('LowerSat', 'HueSatVal', 0, 255, changeLowerSatval)
cv.CreateTrackbar('UpperVal', 'HueSatVal', 0, 255, changeUpperValval)
cv.CreateTrackbar('LowerVal', 'HueSatVal', 0, 255, changeLowerValval)
cv.SetTrackbarPos('UpperHue', 'HueSatVal', 90)
cv.SetTrackbarPos('LowerHue', 'HueSatVal', 30)
cv.SetTrackbarPos('UpperSat', 'HueSatVal', 255)
cv.SetTrackbarPos('LowerSat', 'HueSatVal', 150)
cv.SetTrackbarPos('UpperVal', 'HueSatVal', 255)
cv.SetTrackbarPos('LowerVal', 'HueSatVal', 100)
##changeUpperHueval(0)

##if somevariable == 1:
##    ##red
##    huevals = (200,130)
##    satvals = (240,90)
##    valvals = (255,150)
##    dilateval = 4
##    approxval = 45
##elif somevariable == 2:
##    ##blue
##    huevals = (200,130)
##    satvals = (240,90)
##    valvals = (255,150)
##    dilateval = 4
##    approxval = 45

cv.CreateTrackbar('Delay', 'Camera', 1, 3000, delay)
cv.CreateTrackbar('Dilate', 'Filtered', 0, 10, dilate)
cv.CreateTrackbar('Approx', 'Filtered', 0, 100, approx)
cv.CreateTrackbar('Saturation', 'Camera', 0, 255, saturation)
cv.CreateTrackbar('Contrast', 'Camera', 0, 255, contrast)
cv.SetTrackbarPos('Saturation', 'Camera', 200)
cv.SetTrackbarPos('Contrast', 'Camera', 200)
cv.SetTrackbarPos('Delay', 'Camera', 200)
cv.SetTrackbarPos('Dilate', 'Filtered', 2)
cv.SetTrackbarPos('Approx', 'Filtered', 35)


'''
MAKE THREE SEPARATE WINDOWS; ONE FOR EACH CHANNEL
ADD UPPER AND LOWER TRACKBARS TO EACH

'''

total =0.0
possible =1.0
cv.WaitKey() ==27
while True:
    saturation = cv.GetTrackbarPos('Saturation', 'Camera')
    contrast = cv.GetTrackbarPos('Contrast', 'Camera')
    cv.SetCapturePropterty(capture, cv.CV_CAP_PROP_CONTRAST, contrast)
    cv.SetCapturePropterty(capture, cv.CV_CAP_PROP_SATURATION, saturation)
    
    rawImage = cv.QueryFrame(capture)
    if rawImage is None:
        print 'End of capture / no frame available'
##        break
        ##un-comment to enable infinite loop of video
        cv.SetCaptureProperty(capture, cv.CV_CAP_PROP_POS_AVI_RATIO, 0)
        rawImage =cv.QueryFrame(capture)

    
    """
    ACTUAL FILTERING BEGINS HERE
    """
    
    ##HSV provides much better initial filtering than RGB (at least for our color LEDs)
    cv.CvtColor(rawImage, hsvImage, cv.CV_BGR2HSV)

    ##split the channels up so we can filter them individually
    cv.Split(hsvImage, hue, sat, val, None)

    ##Color filtering based on sliders
    upperhueval = cv.GetTrackbarPos('UpperHue', 'HueSatVal')
    uppersatval = cv.GetTrackbarPos('UpperSat', 'HueSatVal')
    uppervalval = cv.GetTrackbarPos('UpperVal', 'HueSatVal')
    lowerhueval = cv.GetTrackbarPos('LowerHue', 'HueSatVal')
    lowersatval = cv.GetTrackbarPos('LowerSat', 'HueSatVal')
    lowervalval = cv.GetTrackbarPos('LowerVal', 'HueSatVal')
    cv.InRangeS(hue, lowerhueval, upperhueval, hue) ## red 80-240 #hue 65-100
    cv.InRangeS(sat, lowersatval, uppersatval, sat)## green 200-255 #sat 30-200
    cv.InRangeS(val, lowervalval, uppervalval, val)## blue 200-255 #val 200-255

    ##Only takes the matching matches
    cv.And(hue,sat, binImage)
    cv.And(val,binImage,binImage)

    cv.Merge(val,sat,hue,None,hsvImage)
    

    ##VERY IMPORTANT: Eliminates noise (such as the net/rim) 
    cv.Dilate(binImage, binImage, None, cv.GetTrackbarPos('Dilate', 'Filtered')) ##2,3,4 are magic numbers
    cv.ShowImage('Filtered', binImage)

    ##Finds contours (like finding edges/sides)
    storage = cv.CreateMemStorage(0)
    contours = cv.FindContours(binImage, storage, cv.CV_RETR_CCOMP, cv.CV_CHAIN_APPROX_TC89_KCOS)
    
    ##arrays which will hold the good/bad polygons
    squares = []
    badPolys = []
    corners = []

    while (contours != None) and (len(contours) > 0):
        hull = cv.ConvexHull2(contours, storage, cv.CV_COUNTER_CLOCKWISE, 1)
        p = cv.ApproxPoly(hull, storage, cv.CV_POLY_APPROX_DP, cv.GetTrackbarPos('Approx', 'Filtered'), 0) ##45 is a magic number: how accurate the rectangle should be
        area = cv.ContourArea(p)
        ##Ultimately determines what is a rectangle
        ## Must be convex, have 4 vertices, and have an area > 5000 and < 18000
        if (cv.CheckContourConvexity(p) != 0) and (len(p) == 4) and (cv.ContourArea(p) >= 500):
            squares.append(p)
        else:
            badPolys.append(p)
        contours = contours.h_next()

    ##draws bad polygons in red
##    cv.PolyLine(rawImage, badPolys, 1, r, 1, cv.CV_AA)
    ##draws targets in green
    cv.PolyLine(rawImage, squares, 1, g, 1, cv.CV_AA)
    while (contours != None) and (len(contours) > 0):
        hull = cv.ConvexHull2(contours, storage, cv.CV_COUNTER_CLOCKWISE, 1)
        p = cv.ApproxPoly(hull, storage, cv.CV_POLY_APPROX_DP, cv.GetTrackbarPos('Approx', 'Filtered'), 0) ##45 is a magic number: how accurate the rectangle should be

    for s in squares:        
        br = cv.BoundingRect(s,0) ##BoundingRectangles are just CvRectangles, so they store data as (x, y, width, height)
        ##Calculate and draw the center of the rectangle based on the BoundingRect
        x = br[0] + (br[2]/2)
        y = br[1] + (br[3]/2)
        cv.Line(rawImage, (x-5,y),(x+5,y),w, 1, cv.CV_AA)
        cv.Line(rawImage, (x,y-5),(x,y+5),w, 1, cv.CV_AA)
        ##Store the corners as tuples
        tl = (s[0][0],s[0][1])
        bl = (s[1][0],s[1][1])
        br = (s[2][0],s[2][1])
        tr = (s[3][0],s[3][1])
        ##Draw circles on the corners
        cv.Circle(rawImage,tl, 5, w, 1, cv.CV_AA)
        cv.Circle(rawImage,tr, 5, w, 1, cv.CV_AA)
        cv.Circle(rawImage,bl, 5, w, 1, cv.CV_AA)
        cv.Circle(rawImage,br, 5, w, 1, cv.CV_AA)
        cv.PutText(rawImage,str(cv.ContourArea(s)),(x-25,y-10),font, w)
        corners.append((y,tl,tr,br,bl))

    high = 100000
    for c in corners:
        if c[0] < high:
            high = c[0]

            
    ''''''''''''''''''##THESE ARE THE PIXELS YOU WANT DAVID/MATTHEW
    topleftcorner = toprightcorner = bottomrightcorner = bottomleftcorner = (0,0)
    for c in corners:
        if c[0] == high:
            topleftcorner = c[1]
            cv.Circle(rawImage,c[1], 7, r, 1, cv.CV_AA)
            toprightcorner = c[2]
            cv.Circle(rawImage,c[2], 7, r, 1, cv.CV_AA)
            bottomrightcorner = c[3]
            cv.Circle(rawImage,c[3], 7, r, 1, cv.CV_AA)
            bottomleftcorner = c[4]
            cv.Circle(rawImage,c[4], 7, r, 1, cv.CV_AA)
    ''''''''''''''''''
    
##    print topleftcorner
    """
    END FILTERING
    """

    """
    Display information on screen
    """
    cv.Line(rawImage,(0,height-20) ,(width,height-20) , b, 30, cv.CV_AA) ##The black line
    t_curr= time.clock()
    cv.PutText(rawImage, 'time(s): '+ str(round(t_curr-t0, 3)), (325, height-15), font, w) ##The time
    if len(squares) > 0:
        color = g;
        total = total +1.0
##        print "total" ,total
        possible = possible +1.0
##        print 'possible', possible
    else:
        color = r;
        possible = possible +1.0
##    print total/possible
    text =str(len(squares))
    cv.PutText(rawImage, 'targets:', (10,height-15), font, w)
    cv.PutText(rawImage, text, (80,height-15), font, color) ##Number of targets
    cv.PutText(rawImage, 'target in frame:', (110, height-15), font, w)
    cv.PutText(rawImage, str(round(total/possible,3)*100) + "%",(250,height-15),font,g)

    """
    DISPLAY RESULTS
    """
    ##    cv.WriteFrame(writer, rawImage)
##    cv.ShowImage('Filtered', hsvImage)
    cv.ShowImage('Camera', rawImage)
    cv.ShowImage('Hue Filter', hue)
    cv.ShowImage('Sat Filter', sat)
    cv.ShowImage('Val Filter', val)
    cv.ShowImage('HueSatVal', hsvImage)
    """
    DONE WITH WINDOWS
    """

    ## Press ESC to exit all windows and exit
    if cv.WaitKey(cv.GetTrackbarPos('Delay', 'Camera')+1)  ==27:
        break
cv.DestroyAllWindows()
del(capture)
del(writer)

t = time.clock()
print t - t0 ,'seconds ellapsed'
