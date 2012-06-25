#!/usr/bin/env python

'''
A TCP ulitity server that allows for a constant output
serial device to be listened to over TCP without 
'''

import sys
import threading
import serial
import SocketServer
import signal
import socket
import time
from decimal import *

WANT_OTHER_MANGOS = 0
WANT_MOUNTAINS = 0
ON_BONE = 0
ON_PI = 0
VERBOSE = 0

if ON_BONE:
	SERPORT = '/dev/ttyO2'
	RX_MUX = 'spi0_sclk'
	TX_MUX = 'spi0_d0'
elif ON_PI:
	SERPORT = '/dev/ttyAMC0'
else:
	SERPORT = '/dev/ttyUSB0'
MUX_MODE = 1
BAUDRATE = 115200
TIMEOUT = 2 # serial port timeout is 2 seconds
RECEIVE_ENABLE = 32
ser = None 
serial_data = None

# Initialize hardware serial on beaglebone
def initializeSerial():
	global ser
	global ON_BONE
	global ON_PI

	if ON_BONE:
		# set the RX pin for Mode 0 with receive bit on
		# - use %X formatter, since value written must be in hex (e.g. write "21" for mode 1 with receive enabled = 33)
		open('/sys/kernel/debug/omap_mux/' + RX_MUX, 'wb').write("%X" % (RECEIVE_ENABLE + MUX_MODE))
		# set the TX pin for Mode 0
		open('/sys/kernel/debug/omap_mux/' + TX_MUX, 'wb').write("%X" % MUX_MODE)
	ser = serial.Serial(SERPORT, BAUDRATE, timeout=TIMEOUT)
	time.sleep(1)
	print ser.readline()
	print ser.readline()
	print ser.readline()
	print ser.readline()
	print ser.readline()
	if ON_BONE:
		open('/sys/devices/platform/leds-gpio/leds/beaglebone::usr2/brightness', 'wb').write("1") # echo 1 > /sys/devices/platform/leds-gpio/leds/beaglebone::usr2/brightness 

def returnIMUmessage():
	global WANT_MOUNTAINS
	global WANT_OTHER_MANGOS
	global VERBOSE

	line = ser.readline() # Get line of data
	try:	
		roll = line.split("!")[1].split(':')[1].split(',')[1]
	except IndexError:
		print "Problem with Serial Port"
		return "IndexError"
	pitch = line.split("!")[1].split(':')[1].split(',')[2]
	yaw = line.split("!")[1].split(':')[1].split(',')[3]
	accel_x = line.split("!")[1].split(':,')[2].split(',')[0]
	accel_y = line.split("!")[1].split(':,')[2].split(',')[1]
	accel_z = line.split("!")[1].split(':,')[2].split(',')[2]

	gyro_x = line.split("!")[1].split(':,')[2].split(',')[3]
	gyro_y = line.split("!")[1].split(':,')[2].split(',')[4]
	gyro_z = line.split("!")[1].split(':,')[2].split(',')[5]

	if want_other_mangos:
		magno_x = line.split("!")[1].split(':,')[2].split(',')[6]
		magno_y = line.split("!")[1].split(':,')[2].split(',')[7]
		magno_z = line.split("!")[1].split(':,')[2].split(',')[8]
	mango_h = line.split("!")[1].split(':,')[2].split(',')[9]

	if want_mountains:
		baro_t = (float(Decimal(line.split("!")[1].split(':,')[2].split(',')[10]))/10)
		baro_p = line.split("!")[1].split(':,')[2].split(',')[11]

	if not verbose:
		return 		"\n: " + roll + \
					"\n: " + pitch + \
					"\n: " + yaw + \
					"\n: " + accel_x + \
					"\n: " + accel_y + \
					"\n: " + accel_z + \
					"\n: " + gyro_x + \
					"\n: " + gyro_y + \
					"\n: " + gyro_z + \
					"\n: " + mango_h

	else:
		return		"\nRoll: " + roll + \
	   				"\nPitch: " + pitch + \
	   				"\nYaw: " + yaw + \
					"\nAccel x: " + accel_x + \
					"\nAccel y: " + accel_y + \
					"\nAccel z: " + accel_z + \
					"\nGyro x: " + gyro_x + \
					"\nGyro y: " + gyro_y + \
					"\nGyro z: " + gyro_z + \
					"\nMango heading: " + mango_h + \
					""
					#"\nMagno x: " + magno_x + \
					#"\nMagno y: " + magno_y + \
					#"\nMagno z: " + magno_z + \
					#"\nTemp C: " + str(baro_t) + \
					#"\nPressure: " + baro_p +\


class EchoRequestHandler(SocketServer.BaseRequestHandler ):
	'''
	Due to timing differences in serial communication and TCP,
	wait conditions occur, or other bugs due to TCP waiting for
	serial to finish communication, or as found, serial buffer
	problems that occur from not constantly emptying the serial
	buffer, leading to old data being sent, or TCP polling an
	empty buffer from exausting the buffer and waiting for 
	serial to finish. To fix this, a threaded TCP buffer that
	polls on client request was designed, which leads to new
	data consistanly being sent and no buffer race conditions
	from occuring.
	'''

	def setup(self): # Tells us when we have a client has connected
		print self.client_address, 'connected!'

	def handle(self): # Recieves data 
		global serial_data
		data = 'dummy'
		while data:
			if data:
				self.request.sendall(serial_data)
			data = self.request.recv(8)

	def finish(self): # Tells us when we have a client has disconnected
		print self.client_address, 'disconnected!'

def sig_handle(signal,frame): #So it responds to ^C
	print 'Exiting'
	sys.exit(0)

def main(*args):

	global serial_data
	initializeSerial()
	server = SocketServer.ThreadingTCPServer(('', 8881), EchoRequestHandler)
	signal.signal(signal.SIGINT, sig_handle)
	server_thread = threading.Thread(target=server.serve_forever)

	server_thread.daemon = True
	server_thread.start()

	while True:
		serial_data = returnIMUmessage()

if __name__ == '__main__':
	main(*sys.argv)
