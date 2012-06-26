# IMU and Camera Servers

**Authors:** Matthew Skolaut and Patrick Graniham

## About
IMU Server and Camera Server are two TCP data servers designed to run on a linux based co-processor for FIRST Robotics, but can easily be used in many other applications.

IMU server reads serial input from a boards UART device then sends a nicely formatted string over TCP which can be easily parsed. It is set to parse, re-order, and send off data from a Mongoose 9-DOF IMU.

Camera server is a OpenCV based square tracking program that sends off the corner point coordinates for a ranked square based off size and placement in view. The output can easily be processed if the size of the target is known beforehand to create rudimentary auto-targeting.

While this script is written in python, it was intended to work only on linux, so if any changes break support for windows or mac osx, fixes are less priority than others

## Install

Clone the git repository and move the scripts to /etc/init.d

    git clone git@github.com:Spectrum3847/Robot-Linux.git
    sudo mv Robot-Linux/*server* /etc/init.d/
    update-rc.d cam-server defaults # May stall boot if using network camera
    update-rc.d imu-server defaults # IMU server may not work on all platforms, ensure that proper switches in code are set

## Usage 

    python cam-server.py
    python imu-server.py

on another system do:

    nc <ip of server> 8882 # cam-server
    nc <ip of server> 8881 # imu-server


***Warning***
*Please bear in mind that this software is in continuous development, if you don't follow all instructions provided, it will not function