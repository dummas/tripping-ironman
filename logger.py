#!/usr/bin/env python2

# Import serial library
import serial

# Interface
import pygtk
pygtk.require('2.0')
import gtk

# Create a new window
window = gtk.Window()

# Connect delete event
window.connect("delete-event", gtk.main_quit)

window.set_border_width(10)

# Buttons
button = gtk.Button("");

#ser = serial.Serial('/dev/ttyUSB0', 921600, timeout=1) 	# Open USB port, '921600,8,n,1'
#line = ser.readline()																		# Read Line, till '\n'
#print line
#ser.close()

