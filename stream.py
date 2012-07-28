"""
Webcam Streamer

Uses Pygame and HTTPServer to stream USB Camera images via HTTP (Webcam)

HTTP Port, camera resolutions and framerate are hardcoded to keep it
simple but the program can be updated to take options.

Default HTTP Port 8080, 320x240 resolution and 6 frames per second.
Point your browser at http://localhost:8080/

http://www.madox.net/
"""
import pygame
import pygame.camera

import signal
import sys
import tempfile
import threading
import time

import BaseHTTPServer
import SocketServer
      
class CameraCapture():
  def __init__(self, device, resolution, fps):
    #Initialize the camera
    self.camera = pygame.camera.Camera(device, resolution)
    self.camera.start()

    #Set up a CameraSurface Buffer
    self.camera_surface = pygame.Surface(resolution)
    self.jpeg = ""
    self.jpeg_sema = threading.BoundedSemaphore()
    self.period = 1/float(fps)
    self.stop = True
    
    #Prepare conditions
    self.frame_count = 0
    self.frame_available = threading.Condition()
    
    #Kick it off
    self.start_capture()

  def get_image(self):
    self.jpeg_sema.acquire()
    jpeg_copy = self.jpeg
    self.jpeg_sema.release()
    return jpeg_copy
  
  def stop_capture(self):
    self.stop = True
  
  def start_capture(self):
    if self.stop == True:
      self.stop = False
      self.capture_image()
      
  def capture_image(self):
    #Time start
    time_start = time.time()
    
    #Capture the image [Blocking until image received]
    self.camera_surface = self.camera.get_image(self.camera_surface)
    
    #Using a tempfile here because pygame image save gets
    #filetype from extension.  Limiting module use so no PIL.
    temp_jpeg = tempfile.NamedTemporaryFile(suffix='.jpg')
    pygame.image.save(self.camera_surface, temp_jpeg.name)
    
    #Read back the JPEG from the tempfile and store it to self
    temp_jpeg.seek(0)
    self.jpeg_sema.acquire()
    self.jpeg = temp_jpeg.read()
    self.jpeg_sema.release()
    temp_jpeg.close()
    
    #Increment frame count and mark new frame condition
    self.frame_available.acquire()
    self.frame_count += 1
    self.frame_available.notifyAll()
    self.frame_available.release()
    
    #If not stopped, prepare for the next capture
    if self.stop == False:
      time_elapsed = time.time() - time_start
      if time_elapsed >= self.period:
        time_wait = 0
      else:
        time_wait = self.period - time_elapsed
      t = threading.Timer(time_wait, self.capture_image)
      t.start()

class HTTPServer(SocketServer.ThreadingMixIn,
                 BaseHTTPServer.HTTPServer):
  def __init__(self, server_address, cam_dev, cam_res, cam_fps):
    SocketServer.TCPServer.__init__(self, server_address, HTTPHandler)
    self.camera = CameraCapture(cam_dev, cam_res, cam_fps)
    
class HTTPHandler(BaseHTTPServer.BaseHTTPRequestHandler):
  """
  HTTP Request Handler
  """
  def do_GET(self): 
    if self.path == "/":
      response = """
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN"
"http://www.w3.org/TR/html4/strict.dtd">
<html>
<head>
<title>Webcam Streamer</title>
</head>
<body onload="get_new_image();">Select a streaming option below :<br>
<a href="/GetStream">Multipart:
Preferred for fast connections, supported by most browsers.</a><br>
<a href="/JSStream">Javascript:
Backup option, for some mobile browsers (Android) and good for slow
connections.</a>
</body>
</html>
"""   
      self.send_response(200)
      self.send_header("Content-Length", str(len(response)))
      self.send_header("Cache-Control", "no-store")
      self.end_headers()
      self.wfile.write(response)    


      self.send_response(200)
      self.send_header("Content-Length", str(len(response)))
      self.send_header("Cache-Control", "no-store")
      self.end_headers()
      self.wfile.write(response)    
      
    elif self.path[:10] == "/GetStream":     
      #Boundary is an arbitrary string that should not occur in the
      #data stream, using own website address here
      boundary = "www.madox.net" 
      self.send_response(200)
      self.send_header("Access-Control-Allow-Origin", "*")
      self.send_header("Content-type",
                       "multipart/x-mixed-replace;boundary=%s"
                       % boundary)
      self.end_headers()        
      
      frame_id = self.server.camera.frame_count
      
      while True:
        self.server.camera.frame_available.acquire()
        while frame_id == self.server.camera.frame_count:
          self.server.camera.frame_available.wait()      
        self.server.camera.frame_available.release()
        
        frame_id = self.server.camera.frame_count
        response = "Content-type: image/jpeg\n\n"
        response = response + self.server.camera.get_image()
        response = response + "\n--%s\n" % boundary
        self.wfile.write(response)    
        
    elif self.path[:9] == "/GetImage":
      response = self.server.camera.get_image()
      self.send_response(200)
      self.send_header("Content-Length", str(len(response)))
      self.send_header("Content-Type", "image/jpeg")
      self.send_header("Content-Disposition",
                       "attachment;filename=\"snapshot.jpg\"")
      self.send_header("Cache-Control", "no-store")
      self.end_headers()
      self.wfile.write(response)    

    else:
      self.send_error(404, "Banana Not Found.")
      self.end_headers()
    
  do_HEAD = do_POST = do_GET

if __name__ == '__main__':
  print "Started webcam streamer"

  def quit(signum, frame):
    print "Quitting..."
    http_server.camera.stop_capture()
    sys.exit(0)

  pygame.init()
  pygame.camera.init()
  
  signal.signal(signal.SIGINT, quit)
  signal.signal(signal.SIGTERM, quit)
  
  #Localhost, Port 8080, camres=320x240, fps=6
  http_server = HTTPServer(server_address=("",8080),
                            cam_dev="/dev/video0",
                            cam_res=(320,240),
                            cam_fps=6)
  
  http_server_thread = threading.Thread(target=
                                       http_server.serve_forever())
  http_server_thread.setDaemon(true)
  http_server_thread.start()
  
  try:
    while True:
      http_server_thread.join(60)
  except KeyboardInterrupt:
    quit()