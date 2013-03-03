#!/usr/bin/env python2

# Import Wx
import wx
# Import time
import time
# Import serial library
import serial
# Import threads
import threading
# DCT
#from scipy.fftpack import *
# PCA
#from pca import *

# Events ID's
ID_CONNECT = 1
ID_DISCONNECT = 2
ID_CLOSE = 3
ID_SAVEAS = 4

# Algorithm tuning
WINDOW_SIZE = 100
WINDOW_DELAY = 50

# TERMINAL
TERMINAL = '/dev/ttyUSB0'
SPEED = 921600
TIMEOUT = 1

# DATA:
# 01 - Dummy
# 02 - Dummy

# 03 - Maksim ( standing )
#		0301 - 2nd
#		0302 - 3rd
#   0303 - 4th
#		0304 - 5th
# 04 - Tomas ( standing )
#   0401 - 2nd
#   0402 - 3rd
#   0403 - 4th
#   0404 - 5th
# 05 - Justinas ( standing )
# 06 - Jadvyga ( standing )

# 07 - Maksim ( walking )
#		0701 - 2nd
#		0702 - 3rd
#		0703 - 4th
#		0704 - 5th
# 08 - Tomas ( walking )
#   0801 - 2nd
#   0802 - 3rd
#   0803 - 4th
#   0804 - 5th
# 09 - Justinas ( walking )
#   0901 - 2nd
#   0902 - 3rd
#   0903 - 4th
#   0904 - 5th
# 10 - Jadvyga ( walking )
#   1001 - 2nd
#   1002 - 3rd
#   1003 - 4th
#   1004 - 5th

# 11 - Maksim ( stairs up )
#		1101 - 2nd
# 12 - Tomas ( stairs up )
#   1201 - 2nd
# 13 - Justinas ( stairs up )
#		1301 - 2nd
# 14 - Jadvyga ( stairs up )
#   1401 - 2nd
#		1402 - 3rd

# 15 - Maksim ( stairs down )
#		1501 - 2nd
# 16 - Tomas ( stairs down )
#   1601 - 2nd
# 17 - Justinas ( stairs down )
#		1701 - 2nd
# 18 - Jadvyga ( stairs down )
#   1801 - 2nd
#		1802 - 3rd

# 19 - Maksim ( running )
# 20 - Tomas ( running )
# 21 - Justinas ( running )
# 22 - Jadvyga ( running )

# 23 - Maksim ( sitdown )
#		2301 - 2nd
# 24 - Jadvyga ( sitdown )
#		2401 - 2nd
# 25 - Muhamed ( sitdown )
#		2501 - 2nd
# 26 - Miguel ( sitdown )
#		2601 - 2nd

# 27 - Maksim ( standup )
#		2701 - 2nd
# 28 - Jadvyga ( standup )
#		2801 - 2nd
# 29 - Muhamed ( standup )
#		2901 - 2nd
# 30 - Miguel ( standup )
#		3001 - 2nd

# Logging 
GENERATION = '2901'

# FILE OUTPUT
FILE_OUTPUT_T 	= open('data/data' + str( GENERATION ) + '_t.dat', 	'w')
FILE_OUTPUT_N 	= open('data/data' + str( GENERATION ) + '_n.dat', 	'w')
FILE_OUTPUT_DCT = open('data/data' + str( GENERATION ) + '_dct.dat', 'w')
FILE_OUTPUT_PCA = open('data/data' + str( GENERATION ) + '_pca.dat', 'w')

SERIALRX = wx.NewEventType()
# bind to serial data receive events
EVT_SERIALRX = wx.PyEventBinder(SERIALRX, 0)

class SerialRxEvent(wx.PyCommandEvent):
	eventType = SERIALRX
	
	def __init__(self, windowID, data):
		wx.PyCommandEvent.__init__(self, self.eventType, windowID)
		self.data = data
		
	def Clone(self):
		self.__class__(self.GetID(), self.data)
		
class LoggerFrame(wx.Frame):

	def __init__(self, parent, id, title):
		self.serial = serial.Serial(TERMINAL, SPEED, timeout=TIMEOUT)
		self.thread = None
		self.alive = threading.Event()
		
		# Free of calibration
		#self.calibrated = False
		
		self.data_x = []
		self.data_y = []
		self.data_z = []
		
		self.counter = 6000
		
		#self.calibrate_x = []
		#self.calibrate_y = []
		#self.calibrate_z = []
		
		# Initialize Window
		wx.Frame.__init__(self, parent, id, title, size=(600,200))
		
		# Panel & Box
		self.panel = wx.Panel(self)
		self.vbox = wx.BoxSizer(wx.VERTICAL)
		
		# Menu bar
		menubar = wx.MenuBar()
		filem = wx.Menu()
		
		filem.Append(ID_CONNECT, '&Connect');
		filem.Append(ID_DISCONNECT, '&Disconnect');
		filem.AppendSeparator()
		filem.Append(ID_SAVEAS, '&Save Results');
		filem.AppendSeparator()
		filem.Append(ID_CLOSE, 'Cl&ose');
		
		menubar.Append(filem, '&File')
		self.SetMenuBar(menubar)
		
		# Event bindings
		self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)
		#self.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
		self.Bind(wx.EVT_KEY_DOWN, self.OnKeyUp)
		self.Bind(wx.EVT_KEY_UP, self.OnKeyUp)
		#self.Bind(wx.EVT_CHAR, self.OnKeyChar)
		self.Bind(wx.EVT_CHAR, self.OnKeyUp)
		self.Bind(wx.EVT_MENU, self.OnClose, id=ID_CLOSE)
		self.Bind(wx.EVT_MENU, self.OnConnect, id=ID_CONNECT)
		self.Bind(wx.EVT_MENU, self.OnDisConnect, id=ID_DISCONNECT)
		self.Bind(wx.EVT_MENU, self.OnSaveAs, id=ID_SAVEAS)
		self.Bind(EVT_SERIALRX, self.OnSerialRead)
		
		# Elements
		self.text_ctrl_output = wx.TextCtrl(self.panel,-1, "", style=wx.TE_MULTILINE|wx.TE_READONLY)
		
		self.vbox.Add(self.text_ctrl_output, 1, wx.EXPAND | wx.TOP, 20 )
		self.panel.SetSizer(self.vbox)
		self.panel.Fit()
		
	def OnSaveAs(self, event):
		filename = None
		dialog = wx.FileDialog(None, 'Save Logged Data As..', ".", "", "Text File|*.txt|All Files|*", wx.SAVE)
		if dialog.ShowModal() == wx.ID_OK:
			filename = dialog.GetPath()
		dialog.Destroy()
		
		if filename is not None:
			f = file(filename, 'w')
			text = self.text_ctrl_output.GetValue()
			if type(text) == unicode:
				text = text.encode('latin1') # good ?
			f.write(text)
			f.close()
		
	def StartCalibration(self, data):
		pass
		#print "Doing calibration.. X: " 
		#print len(self.calibrate_x)
		
#		if len(self.calibrate_x) < WINDOW_SIZE:
#			self.calibrate_x.append(data[7])
#			
#		if len(self.calibrate_y) < WINDOW_SIZE:
#			self.calibrate_y.append(data[8])
#			
#		if len(self.calibrate_z) < WINDOW_SIZE:
#			self.calibrate_z.append(data[9])		
#		
#		if len(self.calibrate_x) >= WINDOW_SIZE:
#			print "Accelerometer callibrated."
#			self.calibrated = True
		
	def StartThread(self):
		self.thread = threading.Thread(target=self.ComPortThread)
		self.thread.setDaemon(1)
		self.alive.set()
		self.thread.start()
		#print "Staring Calibration.."
		
	def StopThread(self):
		if self.thread is not None:
			self.alive.clear()	# Clear alive event for thread
			self.thread.join()	# Wait until thread has finished
			self.thread = None
			
	def OnSerialRead(self, event):
		"""Handle input from the serial port."""
		text = event.data
		data = text.split()
		
		print >>FILE_OUTPUT_N, data[7], data[8], data[9]
		print >>FILE_OUTPUT_T, data[1], data[2], data[3]
		
		self.text_ctrl_output.AppendText( str( self.counter ) + '\n' )
		
		if self.counter is 1:
			self.StopThread()
			print "Finised."
			print "Closing App..."
			self.CloseApp()
			print "Closed."
		
		#if ( len ( self.data_x ) > WINDOW_SIZE ):
		#	self.log_data()
		#else:
		#	self.data_x.append( float( data[7] ) )
		#	self.data_x.append( float( data[8] ) )
		#	self.data_x.append( float( data[9] ) )
			
			
		#print self.calibrated
#		if self.calibrated == True:
#			if ( len(self.data_x) > WINDOW_SIZE ):
#				self.log_data()
#			else:
#				self.data_x.append( float( data[7] ) )
#				self.data_y.append( float( data[8] ) )
#				self.data_z.append( float( data[9] ) )
#		else:
#			self.StartCalibration(text.split())
			
	def log_data(self):
		self.text_ctrl_output.AppendText( str( self.counter ) + '\n' )
		
		#index = 0
		
		axis_x = []
		axis_y = []
		axis_z = []
		
		#dct_x = []
		#dct_y = []
		#dct_z = []
		
		for vector in zip(self.data_x, self.data_y, self.data_z):
			#axis_x.append( float( vector[0] - float( self.calibrate_x[WINDOW_SIZE - 1 - index] ) ) )
			axis_x.append( float( vector[0] ) )
			#axis_y.append( float( vector[1] - float( self.calibrate_y[WINDOW_SIZE - 1 - index] ) ) )
			axis_y.append( float( vector[1] ) )
			#axis_z.append( float( vector[2] - float( self.calibrate_z[WINDOW_SIZE - 1 - index] ) ) )
			axis_z.append( float( vector[2] ) )
			
			#index = index + 1
			
		#for vector in zip(axis_x, axis_y, axis_z):
		#	string = str(vector[0]) + ' ' + str(vector[1]) + ' ' + str(vector[2]) + '\n'
		# self.text_ctrl_output.AppendText(string)
		#	print >>FILE_OUTPUT_T, string
		
		for vector in zip(axis_x, axis_y, axis_z ):
			string = str(vector[0]) + ' ' + str(vector[1]) + ' ' + str(vector[2]) + '\n'
			#self.text_ctrl_output.AppendText(string)
			print >>FILE_OUTPUT_N, string
			
		#for vector in zip(dct(axis_x), dct(axis_y), dct(axis_z)):
		#	dct_x.append(vector[0])
		#	dct_y.append(vector[1])
		#	dct_z.append(vector[2])
			
		#	print >>FILE_OUTPUT_DCT, vector[0], vector[1], vector[2]
			
		#center_dct_x = Center(dct_x)
		#center_dct_y = Center(dct_y)
		#center_dct_z = Center(dct_z)
		
		#pca_x = PCA([center_dct_x.A])
		#pca_y = PCA([center_dct_y.A])
		#pca_z = PCA([center_dct_z.A])
			
		#index = 0
		
		#for vector in zip(pca_x.Vt.T, pca_y.Vt.T, pca_z.Vt.T):
		#	print vector
		#	print >>FILE_OUTPUT_PCA, vector[0][0] * axis_x[index], vector[1][0] * axis_y[index], vector[2][0] * axis_z[index]
		#	index = index + 1;
			
		self.data_x = self.data_x[WINDOW_DELAY:]
		self.data_y = self.data_x[WINDOW_DELAY:]
		self.data_z = self.data_x[WINDOW_DELAY:]
		
	#def take_cate_of_plotting(self, data):
	
		#pass
	
		#print >>FILE_OUTPUT_T, time.time(), data[7], data[8], data[9]
		#print >>FILE_OUTPUT_N, data[7], data[8], data[9]
		
		#if len(self.plotting_data_x) + 1 < 100:
		#	self.plotting_data_x.append(data[7])
		#else:
		#	self.plotting_data_x = self.plotting_data_x[1:]
		#	self.plotting_data_x.append(data[7])
		#	
		#if len(self.plotting_data_y) + 1 < 100:
		#	self.plotting_data_y.append(data[8])
		#else:
		#	self.plotting_data_y = self.plotting_data_y[1:]
		#	self.plotting_data_y.append(data[8])
		#	
		#if len(self.plotting_data_z) + 1 < 100:
		#	self.plotting_data_z.append(data[9])
		#else:
		#	self.plotting_data_z = self.plotting_data_z[1:]
		#	self.plotting_data_z.append(data[9])
			
		#if len(self.plotting_data_x) + 1 == 100:
		#	d = Gnuplot.Data(self.plotting_data_x, with_ = 'lines' )
		#	if self.plotted:
		#		self.g.replot(d)
		#	else:
		#		self.g.plot(d)
		#		self.plotted = True
		#	#time.sleep(1.0)
		
	def ComPortThread(self):
		while self.alive.isSet(): # loop while alive event is true
			#text = self.serial.read(1) # readline
			#if text:
			#	n = self.serial.inWaiting() # look if there is more to read
			#	if n:
			#		text = text + self.serial.read(n) # get it
			text = self.serial.readline()
			if ( self.serial.inWaiting() == 0 ): # Rise event if only all bits have been read
				event = SerialRxEvent(self.GetId(), text )
				self.GetEventHandler().AddPendingEvent(event)
				self.counter = self.counter - 1;
		
	# Events
	def OnConnect(self, event):
		print "Connecting..."
		self.StartThread()
		print "Connected."
		
	def OnDisConnect(self, event):
		print "Disconnecting..."
		self.StopThread()
		print "Disconnected."
		
	def OnClose(self, event):
		print "Closing App.."
		self.CloseApp()
		print "App is closed"
		
	def OnCloseWindow(self, event):
		print "Closing application.."
		self.CloseApp()
		print "App is closed"
		
	def OnKeyUp(self, event):
		print "KeyUp Event"
		keycode = event.GetKeyCode()
		if keycode == wx.WXK_ESCAPE:
			self.CloseApp()
		elif keycode == wx.WXK_F2:
			if self.alive.isSet():
				self.StopThread()
			else:
				self.StartThread()
			
	def OnKeyDown(self, event):
		pass
		
	def OnKeyChar(self, event):
		pass
			
	# Functions
	def CloseApp(self):
		app.keepGoing = False
		self.Destroy()
		
class LoggerApp(wx.App):
	def MainLoop(self):
		evtloop = wx.EventLoop()
		old = wx.EventLoop.GetActive()
		wx.EventLoop.SetActive(evtloop)
		
		while self.keepGoing:
			
			while evtloop.Pending():
				evtloop.Dispatch()
			
			#time.sleep(0.05)
			self.ProcessIdle()
			
		wx.EventLoop.SetActive(old)
	
	def OnInit(self):
	
		frame = LoggerFrame(None, -1, "Logger Application")
		frame.Show(True)
		self.SetTopWindow(frame)
		
		self.keepGoing = True
		return True
		
if __name__ == '__main__':
	app = LoggerApp(False)
	app.MainLoop()
