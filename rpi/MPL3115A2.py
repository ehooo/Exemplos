#!/usr/bin/python

from Adafruit_GPIO.I2C import get_i2c_device
import time

# ===========================================================================
# MPL3115A2 Altitude/Barometric Pressure Sensor Class
#
# Based on MPL3115A2 Breakout (https://github.com/sparkfun/MPL3115A2_Breakout)
# RPi and BBIO compatibility by (https://github.com/adafruit/Adafruit_Python_GPIO)
# ===========================================================================

class MPL3115A2:
	ADDRESS     = 0x60
	STATUS      = 0x00
	OUT_P_MSB   = 0x01
	OUT_T_MSB   = 0x04
	PT_DATA_CFG = 0x13
	CTRL_REG1   = 0x26

	def __init__(self, address=MPL3115A2.ADDRESS):
		self.i2c = get_i2c_device(address)
		self.last_data = None

	'''
		Clears then sets the OST bit which causes the sensor to immediately take another reading
		Needed to sample faster than 1Hz
	'''
	def __toggleOneShot(self):
		tempSetting = self.i2c.readU8(MPL3115A2.CTRL_REG1)
		tempSetting &= ~(1<<1)
		tempSetting = self.i2c.readU8(MPL3115A2.CTRL_REG1, 1)
		self.i2c.write8(MPL3115A2.CTRL_REG1, tempSetting)

		tempSetting = self.i2c.readU8(MPL3115A2.CTRL_REG1, 1)
		tempSetting |= (1<<1); //Set OST bit
		self.i2c.write8(MPL3115A2.CTRL_REG1, tempSetting)
	def __prepare(self, size):
		#Check PDR bit, if it's not set then toggle OST
		if(self.i2c.write8(MPL3115A2.STATUS) & (1<<2) == 0):
			self.__toggleOneShot()# Toggle the OST bit causing the sensor to immediately take another reading

		# Wait for PDR bit, indicates we have new pressure data
		counter = 0
		while(self.i2c.readU8(MPL3115A2.STATUS) & (1<<2) == 0):
			if ++counter > 600:
				raise IOError("Error out after max of 512ms for a read")
			time.sleep(0.001)

		# Read pressure registers
		self.last_data = self.i2c.readList(MPL3115A2.OUT_P_MSB, size)
		if len(self.last_data) != size:
			self.last_data = None

		self.__toggleOneShot()# Toggle the OST bit causing the sensor to immediately take another reading

	# Returns float with meters above sealevel. Ex: 1638.94
	def readAltitude(self):
		try:
			self.__prepare(3)
		except IOError:
			return -999
		if self.last_data is None:
			return -999
		'''
			The least significant bytes l_altitude and l_temp are 4-bit,
			fractional values, so you must cast the calulation in (float),
			shift the value over 4 spots to the right and divide by 16 (since  there are 16 values in 4-bits).
		#'''
		tempcsb = float((self.last_data[2]>>4)/16.0)
		return float( ( (self.last_data[0]<<8) | self.last_data[1] ) + tempcsb )
	# Returns float with feet above sealevel. Ex: 5376.68
	def readAltitudeFt(self):
		return self.readAltitude() * 3.28084
	# Returns float with barometric pressure in Pa. Ex: 83351.25
	def readPressure(self):
		try:
			self.__prepare(3)
		except IOError:
			return -999
		if self.last_data is None:
			return -999

		# Pressure comes back as a left shifted 20 bit number
		pressure_whole = self.last_data[0]<<16 | self.last_data[1]<<8 | self.last_data[2];
		pressure_whole >>= 6 #Pressure is an 18 bit number with 2 bits of decimal. Get rid of decimal portion.

		self.last_data[2] &= 0x30 # Bits 5/4 represent the fractional component
		self.last_data[2] >>= 4 # Get it right aligned
		pressure_decimal = float(self.last_data[2]/4.0)# Turn it into fraction
		pressure = float(pressure_whole) + pressure_decimal
		return pressure 
	# Returns float with current temperature in Celsius. Ex: 23.37
	def readTemp(self):
		try:
			self.__prepare(2)
		except IOError:
			return -999
		if self.last_data is None:
			return -999

		foo = 0x0
		negSign = False

		#Check for 2s compliment
		if(self.last_data[0] > 0x7F):
			foo = ~((self.last_data[0] << 8) + self.last_data[1]) + 1 # 2’s complement
			self.last_data[0] = foo >> 8
			self.last_data[1] = foo & 0x00F0
			negSign = True

		'''
			The least significant bytes l_altitude and l_temp are 4-bit,
			fractional values, so you must cast the calulation in (float),
			shift the value over 4 spots to the right and divide by 16 (since there are 16 values in 4-bits).
		'''
		templsb = float((self.last_data[1]>>4)/16.0) # temp, fraction of a degree
		temperature = float(self.last_data[0] + templsb)

		if negSign:
			temperature = 0 - temperature
		return temperature
	# Returns float with current temperature in Fahrenheit. Ex: 73.96
	def readTempF(self):
		return((self.readTemp() * 9.0)/ 5.0 + 32.0) # Convert celsius to fahrenheit

	# Puts the sensor into Pascal measurement mode.
	def setModeBarometer(self):
		tempSetting = self.i2c.readU8(MPL3115A2.CTRL_REG1); #Read current settings
		tempSetting &= ~(1<<7) # Clear ALT bit
		self.i2c.write8(MPL3115A2.CTRL_REG1, tempSetting)
	# Puts the sensor into altimetery mode.
	def setModeAltimeter(self):
		tempSetting = self.i2c.readU8(MPL3115A2.CTRL_REG1); #Read current settings
		tempSetting |= (1<<7) # Clear ALT bit
		self.i2c.write8(MPL3115A2.CTRL_REG1, tempSetting)
	# Puts the sensor into Standby mode. Required when changing CTRL1 register.
	def setModeStandby(self):
		tempSetting = self.i2c.readU8(MPL3115A2.CTRL_REG1); #Read current settings
		tempSetting &= ~(1<<0) # Clear SBYB bit for Standby mode
		self.i2c.write8(MPL3115A2.CTRL_REG1, tempSetting)
	# Start taking measurements!
	def setModeActive(self):
		tempSetting = self.i2c.readU8(MPL3115A2.CTRL_REG1); #Read current settings
		tempSetting |= (1<<0) # Set SBYB bit for Active mode
		self.i2c.write8(MPL3115A2.CTRL_REG1, tempSetting)
	'''
		Call with a rate from 0 to 7. See page 33 for table of ratios.
		Sets the over sample rate. Datasheet calls for 128 but you can set it from 1 to 128 samples. The higher the oversample rate the greater the time between data samples.
		Sets the # of samples from 1 to 128. See datasheet.
	'''
	def setOversampleRate(self, sampleRate):
		if sampleRate > 7:
			sampleRate = 7 # OS cannot be larger than 0b.0111
		sampleRate <<= 3 #Align it for the CTRL_REG1 register
		tempSetting = self.i2c.readU8(MPL3115A2.CTRL_REG1) # Read current settings
		tempSetting &= 0xC7 # Clear out old OS bits
		tempSetting |= sampleRate # Mask in new OS bits
		self.i2c.write8(MPL3115A2.CTRL_REG1, tempSetting)
	# Sets the fundamental event flags. Required during setup.
	def enableEventFlags(self):
		self.i2c.write8(MPL3115A2.PT_DATA_CFG, 0x07)

