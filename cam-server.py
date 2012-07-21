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

"""
SET UP / INSTANTIATION
"""
pixels = [(0,0), (0,0), (0,0), (0,0)]
pixel_data = ""

(CAM, NET, VID) = (0, 0, 1)
ON_BONE, ON_PI = (0, 0)

capture = None
writer = None

def returnCAMmessage():
		
	global pixels

	return		str(pixels[0][0]).zfill(3) + \
				str(pixels[0][1]).zfill(3) + \
				str(pixels[1][0]).zfill(3) + \
				str(pixels[1][1]).zfill(3) + \
				str(pixels[2][0]).zfill(3) + \
				str(pixels[2][1]).zfill(3) + \
				str(pixels[3][0]).zfill(3) + \
				str(pixels[3][1]).zfill(3)


class EchoRequestHandler(SocketServer.BaseRequestHandler):
	def setup(self):
		 print self.client_address, 'connected!'

	def handle(self):
		global pixel_data

		data = 'dummy'
		while data:
			if data:
				self.request.sendall(pixel_data)
			data = self.request.recv(1)
		print data

	def finish(self):
		 print self.client_address, 'disconnected!'


def sig_handle(signal,frame):
	global capture
	global writer
	print 'Exiting'
	del(capture)
	del(writer)
	sys.exit(0)


def main(*args):

	###### ORIGINAL SERVER MAIN FUNCTION START
	global pixels
	global pixel_data
	global ON_BONE
	global ON_PI
	global height
	global width
	global capture
	global writer
	#global redpill_or_bluepill

	server = SocketServer.ThreadingTCPServer(('', 8882), EchoRequestHandler)
	signal.signal(signal.SIGINT, sig_handle)
	server_thread = threading.Thread(target=server.serve_forever)

	server_thread.daemon = True
	server_thread.start()
	###### ORIGINAL SERVER MAIN FUNCTION NON-LOOP END
	
	print "caputure started"
	
	'''
	slow network video capture
	works, but delays code ~30-120sec on all platforms, depending on it's temperment
	this is due to the implementation in ffmpeg, and is not a part of OpenCV, just a
	lower level video library used by OpenCV
	possible workaround by using command line utilities to bind to file stream
	'''
	if NET:
		capture = cv.CaptureFromFile("http://10.38.47.11/mjpg/video.mjpg?resolution=640x480&.mjpg")
	elif CAM:
		print "Not Bone or Pi"
		capture = cv.CaptureFromCAM(1)
		cv.SetCaptureProperty(capture, cv.CV_CAP_PROP_FRAME_WIDTH, width)
		cv.SetCaptureProperty(capture, cv.CV_CAP_PROP_FRAME_HEIGHT, height)
	elif VID:
		capture = cv.CaptureFromFile("vision.mp4")
	print "capture done"

	if ON_BONE:
		# same as 'echo 1 > /sys/devices/platform/leds-gpio/leds/beaglebone::usr2/brightness'
		open('/sys/devices/platform/leds-gpio/leds/beaglebone::usr2/brightness', 'wb').write("1") 

	if capture is None:
		print "Capture Error"
		sys.exit()


	fourcc = cv.CV_FOURCC('M', 'J', 'P', 'G')
	fps = 10 
	writer = cv.CreateVideoWriter('compression4.avi', 0, fps, (width, height), 1)
	if writer is None:
		print 'Writer Error'

	##		easier to type (not necessarily required)
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

	upperhueval = 100
	lowerhueval = 10
	uppersatval = 255
	lowersatval = 140
	uppervalval = 255
	lowervalval = 140 
	dilateval = 5
	approxval = 35

	while True:

		rawImage = cv.QueryFrame(capture)
		if rawImage is None:
			break

		"""
		ACTUAL FILTERING BEGINS HERE
		"""

		##HSV provides much better initial filtering than RGB (at least for our color LEDs)
		cv.CvtColor(rawImage, hsvImage, cv.CV_BGR2HSV)

		##split the channels up so we can filter them individually
		cv.Split(hsvImage, hue, sat, val, None)

		##only keeps values in respective channels that are within ranges specified
		cv.InRangeS(hue, lowerhueval, upperhueval, hue) ## red 80-240 #hue 65-100
		cv.InRangeS(sat, lowersatval, uppersatval, sat)## green 200-255 #sat 30-200
		cv.InRangeS(val, lowervalval, uppervalval, val)## blue 200-255 #val 200-255

		##only keeps the values that fit all of the previous filters (i.e. the retroreflective tape (hopefully))
		cv.And(hue,sat, binImage)
		cv.And(val,binImage,binImage)


		'''
		This is a critical step:
		If the dilation/erosion or whatever ends up being implemented fails, then everything fails.
			
		Purpose:
		Serves to eliminate the noise caused by the rim in front of the retroreflective tape (on the 3rd tier basket)
		'''
		cv.Dilate(binImage, binImage, None, dilateval) 

		##Finds contours (like finding edges/sides)
		storage = cv.CreateMemStorage(0)
		contours = cv.FindContours(binImage, storage, cv.CV_RETR_CCOMP, cv.CV_CHAIN_APPROX_TC89_KCOS)
			

		##arrays which will hold the good/bad polygons
		squares = []
		badPolys = []

		while (contours != None) and (len(contours) > 0):
			hull = cv.ConvexHull2(contours, storage, cv.CV_CLOCKWISE, 1)

			##maybe try different filters?
			p = cv.ApproxPoly(hull, storage, cv.CV_POLY_APPROX_DP, approxval, 0)
		
			## A (good) square must: 1. Be convex, 2. Have four vertices, 3. Have a large area
			if (cv.CheckContourConvexity(p) != 0) and (len(p) == 4) and (cv.ContourArea(p) >= 5000):
				squares.append(p)
			else:
				badPolys.append(p)

			contours = contours.h_next()

			##TODO: possibly add a filter for polygons within other polygons, but I think findContours accounts for that

		for s in squares:
			if len(squares) > 0:
				pixels = s
				print "Tracking"
			else:
				pixels = [(0,0), (0,0), (0,0), (0,0)]

		pixel_data = returnCAMmessage()
		
		"""
		END FILTERING
		"""

	del(capture)
	del(writer)

	t = time.clock()
	print t - t0 ,'seconds ellapsed'
	
if __name__ == '__main__':
	main(*sys.argv)
