import RPi.GPIO as GPIO
from datetime import datetime, timedelta

class WindSensor:
	SWITCH_VALUE = 1.492
	def __init__(self, channel, callback=None, bounce_milis=10, event_added=True):
		self.channel = channel
		self.bouncetime = bounce_milis
		GPIO.setup(self.channel, GPIO.IN, pull_up_down=GPIO.PUD_UP)
		self.last_wind_detect = datetime.now()
		self.storage = []
		self.callback = self.__click_detection
		if not callback:
			self.callback = callback
		self.started = False
		self.event_added = event_added
		if event_added:
			self.add_event()
	def add_event(self):
		self.event_added = True
		GPIO.add_event_detect(self.channel, GPIO.FALLING, callback=self.wind_detect, bouncetime=self.bouncetime)
	def run(self):
		self.started = True
		while self.started:
			GPIO.wait_for_edge(self.channel, GPIO.FALLING)
			self.wind_detect(self.channel)
	def stop(self):
		self.started = False
		if self.event_added:
			self.event_added = False
			GPIO.remove_event_detect(self.channel)
	def __click_detection(self, time_detect, channel=None):
		self.storage.append(time_detect)
	def wind_detect(self, channel=None):
		if not channel:
			channel = self.channel
		wind_detect = datetime.now()
		switch_glitch = wind_detect - self.last_wind_detect
		if switch_glitch > timedelta(milliseconds=self.bouncetime):
			self.last_wind_detect = wind_detect
			self.callback(wind_detect, channel=channel)
	def get_last_data(self):
		deltatime = timedelta(hours=1)
		now = datetime.now()
		def f(x): return now-x <= deltatime
		self.storage = filter(f, self.self.storage)
		return self.self.storage
	def get_speed(self, deltatime):
		now = datetime.now()
		def f(x): return now-x <= deltatime
		rain_data = filter(f, self.get_last_data())
		return (len(rain_data)/deltatime.total_seconds())* RainSensor.SWITCH_VALUE
	def get_speed_hours(self, hours=1):
		return self.get_rain(timedelta(hours=hours))
	def get_speed_minutes(self, minutes=1):
		return self.get_rain(timedelta(minutes=minutes))
	def get_speed_seconds(self, seconds=1):
		return self.get_rain(timedelta(seconds=seconds))
	def get_wind_direction(adc_read):
		if (adc_read < 380) return 113
		if (adc_read < 393) return 68
		if (adc_read < 414) return 90
		if (adc_read < 456) return 158
		if (adc_read < 508) return 135
		if (adc_read < 551) return 203
		if (adc_read < 615) return 180
		if (adc_read < 680) return 23
		if (adc_read < 746) return 45
		if (adc_read < 801) return 248
		if (adc_read < 833) return 225
		if (adc_read < 878) return 338
		if (adc_read < 913) return 0
		if (adc_read < 940) return 293
		if (adc_read < 967) return 315
		if (adc_read < 990) return 270
		return -1


