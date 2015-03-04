import RPi.GPIO as GPIO
from datetime import datetime, timedelta

class RainSensor:
	SWITCH_VALUE = 0.011
	def __init__(self, channel, callback=None, bounce_milis=10, event_added=True):
		self.channel = channel
		self.bouncetime = bounce_milis
		GPIO.setup(self.channel, GPIO.IN, pull_up_down=GPIO.PUD_UP)
		self.last_rain_detect = datetime.now()
		self.storage = []
		self.callback = self.__add_detection
		if not callback:
			self.callback = callback
		self.started = False
		self.event_added = event_added
		if event_added:
			self.add_event()
	def add_event(self):
		self.event_added = True
		GPIO.add_event_detect(self.channel, GPIO.FALLING, callback=self.rain_detect, bouncetime=self.bouncetime)
	def run(self):
		self.started = True
		while self.started:
			GPIO.wait_for_edge(self.channel, GPIO.FALLING)
			self.rain_detect(self.channel)
	def stop(self):
		self.started = False
		if self.event_added:
			self.event_added = False
			GPIO.remove_event_detect(self.channel)
	def get_last_data(self):
		deltatime = timedelta(days=1)
		now = datetime.now()
		def f(x): return now-x <= deltatime
		self.storage = filter(f, self.self.storage)
		return self.self.storage
	def rain_detect(self, channel=None):
		if not channel:
			channel = self.channel
		rain_detect = datetime.now()
		switch_glitch = rain_detect - self.last_rain_detect
		if switch_glitch > timedelta(milliseconds=self.bouncetime):
			self.last_rain_detect = rain_detect
			self.callback(rain_detect, channel=channel)
	def __add_detection(self, time_detect, channel=None):
		self.storage.append(time_detect)
	def get_rain(self, deltatime):
		now = datetime.now()
		def f(x): return now-x <= deltatime
		rain_data = filter(f, self.get_last_data())
		return len(rain_data) * RainSensor.SWITCH_VALUE
	def get_last_hours(self, hours=1):
		return self.get_rain(timedelta(hours=hours))
	def get_last_minutes(self, minutes=1):
		return self.get_rain(timedelta(minutes=minutes))
