from cv2 import *
import math
import time
import sys
import threading
import SocketServer
import signal
import socket
from decimal import *
t0 = time.clock() ##timer
print "To exit, press ESC."
"""
SET UP / INSTANTIATION
"""
pixels = None
pixel_data = None


def returnCAMmessage():
    
	# These are placeholder values for what will be global variable when
	# this code is appended to the functioning vision code
	distance = None
	angle = None
	rpm = None

	global pixels

	return		"\nPixel 0 X: " + str(pixels[0][0]) + \
       			"\nPixel 0 Y: " + str(pixels[0][1]) + \
       			"\nPixel 1 X: " + str(pixels[1][0]) + \
			"\nPixel 1 Y: " + str(pixels[1][1]) + \
       			"\nPixel 2 X: " + str(pixels[2][0]) + \
       			"\nPixel 2 Y: " + str(pixels[2][1]) + \
       			"\nPixel 3 X: " + str(pixels[3][0]) + \
			"\nPixel 3 Y: " + str(pixels[3][1])


class EchoRequestHandler(SocketServer.BaseRequestHandler ):
    def setup(self):
        print self.client_address, 'connected!'

    def handle(self):
	global pixel_data

        data = 'dummy'
        while data:
		if data:
			self.request.sendall(pixel_data)
		data = self.request.recv(8)

    def finish(self):
        print self.client_address, 'disconnected!'


def sig_handle(signal,frame):
	print 'Exiting'
	sys.exit(0)


def main(*args):

	###### ORIGINAL SERVER MAIN FUNCTION START
	global pixels
	global pixel_data
	server = SocketServer.ThreadingTCPServer(('', 8882), EchoRequestHandler)
	signal.signal(signal.SIGINT, sig_handle)
	server_thread = threading.Thread(target=server.serve_forever)

	server_thread.daemon = True
	server_thread.start()
	###### ORIGINAL SERVER MAIN FUNCTION NON-LOOP END
	
	
	##capture=cv.CaptureFromFile("clear.asf")
	capture = cv.CaptureFromFile("http://10.38.47.11/mjpg/video.mjpg?resolution=640x480&.mjpg")
	 
	height = 480
	width = 640

	fourcc = cv.CV_FOURCC('M', 'J', 'P', 'G')
	fps = 10 
	writer = cv.CreateVideoWriter('compression4.avi', 0, fps, (width, height), 1)
	if writer is None:
	    print 'writer is wrong'

	##    easier to type (not necessarily required)
	depth1 = cv.CV_8UC1
	depth3 = cv.CV_8UC3

	##create some of the images which will be used during processing but which can ultimately be disposed
	hsvImage = cv.CreateMat(height,width, depth3)
	filteredImage = cv.CreateMat(height,width, depth3)
	binImage = cv.CreateMat(height,width, depth1)

	##individual HSV channels (all with a depth of 1)
	hue = cv.CreateMat(height, width, depth1)
	sat = cv.CreateMat(height, width, depth1)
	val = cv.CreateMat(height, width, depth1)

	##just some global colors for ease of use
	r =  (0, 0, 255, 0);
	g =  (0, 255, 0, 0);
	w = cv.RGB(255,255,255)
	b = cv.RGB(0,0,0)

	cv.NamedWindow('win2', cv.CV_WINDOW_AUTOSIZE)
	cv.NamedWindow('win', cv.CV_WINDOW_AUTOSIZE)
	while True:
	    rawImage = cv.QueryFrame(capture)
	    
	    if rawImage is None:
	##        print 'noFrame'
		break

	    """
	    ACTUAL FILTERING BEGINS HERE
	    """
	    ##HSV provides much better initial filtering than RGB (at least for our color LEDs)
	    cv.CvtColor(rawImage, hsvImage, cv.CV_BGR2HSV)

	    ##split the channels up so we can filter them individually
	    cv.Split(hsvImage, hue, sat, val, None)

	    ##only keeps values in respective channels that are within ranges specified
	    ##TODO: make tool that can generate these values on demand, for use at competition (i.e. rapid vision testing)
	    cv.InRangeS(hue, 80, 110, hue) ## red 80-240 #hue 65-100
	    cv.InRangeS(sat, 80, 255, sat)## green 200-255 #sat 30-200
	    cv.InRangeS(val, 220, 255, val)## blue 200-255 #val 200-255

	    ##only keeps the values that fit all of the previous filters (i.e. the retroreflective tape (hopefully))
	    cv.And(hue,sat, binImage)
	    cv.And(val,binImage,binImage)

	    '''
	    This is a critical step:
		If the dilation/erosion or whatever ends up being implemented fails, then everything fails.
	    
	    Purpose:
		Serves to eliminate the noise caused by the rim in front of the retroreflective tape (on the 3rd tier basket)
	    '''
	    cv.Dilate(binImage, binImage, None, 5) 

	    ##Finds contours (like finding edges/sides)
	    storage = cv.CreateMemStorage(0)
	    contours = cv.FindContours(binImage, storage, cv.CV_RETR_CCOMP, cv.CV_CHAIN_APPROX_TC89_KCOS)
	    

	    ##arrays which will hold the good/bad polygons
	    squares = []
	    badPolys = []

	    while (contours != None) and (len(contours) > 0):
		hull = cv.ConvexHull2(contours, storage, cv.CV_CLOCKWISE, 1)
		##maybe try different filters?
		p = cv.ApproxPoly(hull, storage, cv.CV_POLY_APPROX_DP, 45, 0)
		
		## A (good) square must: 1. Be convex, 2. Have four vertices, 3. Have a large area
		if (cv.CheckContourConvexity(p) != 0) and (len(p) == 4) and (cv.ContourArea(p) >= 5000):
		    squares.append(p)
		else:
		    badPolys.append(p)
		
		contours = contours.h_next()



	    ##draws bad polygons in red
	    cv.PolyLine(rawImage, badPolys, 1, r, 1, cv.CV_AA)
	    ##draws targets in green
	    cv.PolyLine(rawImage, squares, 1, g, 1, cv.CV_AA)
	    if len(squares) >0:
		color = g;
	    else:
		color = r;
	    text = '# targets: '+ str(len(squares))
	    font = cv.InitFont(cv.CV_FONT_HERSHEY_PLAIN, 1.0, 1.0, 0, 1, cv.CV_AA);
	    cv.PutText(rawImage, text, (10,height-10), font, color)
	    for s in squares:
		pixels
		pixels = s
		pixel_data = returnCAMmessage()
		
		br = cv.BoundingRect(s,0) ##BoundingRectangles are just CvRectangeles, so they store data as (x, y, width, height)
		##Calculate and draw the center of the rectangle based on the BoundingRect
		##  (could be calculated more accurately, but should be sufficient)
		x = br[0] + (br[2]/2)
		y = br[1] + (br[3]/2)
		cv.Circle(rawImage,(x,y), 2, g, 1, cv.CV_AA)
		cv.Circle(rawImage,(x,y), 5, g, 1, cv.CV_AA)
	    """
	    END FILTERING
	    """


	    """
	    DISPLAY RESULTS
	    """
	    cv.ShowImage('win', binImage)
	    cv.WriteFrame(writer, rawImage)
	    cv.ShowImage('win2', rawImage)
	    """
	    DONE WITH WINDOWS
	    """

	    ## Press ESC to exit all windows and exit
	    if cv.WaitKey(1)  ==27:
		break
	cv.DestroyAllWindows()
	del(capture)
	del(writer)

	t = time.clock()
	print t - t0 ,'seconds ellapsed'
	
if __name__ == '__main__':
	main(*sys.argv)
