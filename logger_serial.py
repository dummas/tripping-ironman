class LoggerSerial(threading.Thread):

	def __init__(self):
		#threading.Thread.__init__(self)
		super(LoggerSerial, self).__init__()
		self._stop = threading.Event()
		self.terminal = '/dev/ttyUSB0'
		self.speed = 921600
		self.timeout = 1
		self.serCom = False
		self.connected = False

	def connect(self):
		
		try:
			self.serCom = serial.Serial(self.terminal, self.speed, timeout=self.timeout)
			self.connected = True
		except:
			self.serCom = False
			self.connected = False
		
		#self.serCom = serial.Serial(self.terminal, self.speed, timeout=self.timeout)
			
		#print "From logger serial: " + self.serCom
			
	def status(self):
		return self.connected
		
	def run(self):
		try:
			while True:
				return self.readline()
		except:
			return False
			
	def stop(self):
		self._stop.set();
		
	def stopped(self):
		return self._stop.isSet()
		
	def readline(self):
		line = self.serCom.readline()
		return line
		
	def disconnect(self):
		if self.serCom is not False:
			self.connected = False
			self.serCom.close()
