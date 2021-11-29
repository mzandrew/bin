# from https://learn.adafruit.com/adafruit-ultimate-gps-featherwing/circuitpython-library
# written 2021-11-28 by mza
# last updated 2021-11-28 by mza

import time
import board
import busio
import adafruit_gps
import boxcar
from DebugInfoWarningError24 import debug, info, warning, error, debug2, debug3, set_verbosity, create_new_logfile_with_string_embedded, flush

shmepsilon = 1.5

def setup_internal(N, delay_in_ms=1000):
	gps.send_command(b"PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0")
	gps.send_command(b'PMTK220,' + str(delay_in_ms))
	global myboxcar
	myboxcar = boxcar.boxcar(6, N, "gps")

def setup_uart(uart, N, delay_in_ms=1000):
	global gps
	gps = adafruit_gps.GPS(uart, debug=False)
	setup_internal(N, delay_in_ms)

def setup_i2c(i2c, N, delay_in_ms=1000):
	global gps
	gps = adafruit_gps.GPS_GtopI2C(i2c)
	setup_internal(N, delay_in_ms)

def get_values():
	try:
		gps.update()
	except:
		pass
	values = [ 0., 0., 0., 0., 0., 0 ]
	if gps.has_fix:
		hd = gps.horizontal_dilution
		if hd is not None and hd<shmepsilon:
			values = [ gps.latitude, gps.longitude, gps.altitude_m, gps.height_geoid, gps.horizontal_dilution, gps.satellites ]
			myboxcar.accumulate(values)
	return values

def header_string():
	return ", lat-deg, long-deg, alt/elev-m, #sat, HDOP-m"

def measure_string():
	string = ""
	if gps.has_fix:
		values = get_values()
		string += ", %.6f" % values[0]
		string += ", %.6f" % values[1]
		#string += ", %d" % gps.fix_quality
		if values[2] is not None:
			if values[3] is not None:
				string += ", %.1f" % (values[2] - values[3])
			else:
				string += ", %.1f" % values[2]
	#	if gps.speed_knots is not None:
	#		string += ", %.1f" % gps.speed_knots
	#	if gps.track_angle_deg is not None:
	#		string += ", %.1f" % gps.track_angle_deg
		if values[5] is not None:
			string += ", %02d" % values[5]
		if values[4] is not None:
			string += ", %.2f" % values[4]
	else:
		pass
		#info("Waiting for fix...")
	return string

def average_location():
	try:
		location = myboxcar.get_average_values()[0:4]
		# this is a bit sketch, since if the height_geoid is not reported in a given sentence, a zero will be averaged in...
		# so we could just subtract the latest one or something
		#info(str(location))
		#location[3] = myboxcar.get_previous_values()[3]
		#info(str(location))
		location = [ location[0], location[1], location[2] - location[3] ]
		#info(str(location))
		return location
	except:
		raise

def instantaneous_location():
	try:
		gps.update()
	except:
		pass
	if gps.has_fix:
		location = [ gps.latitude, gps.longitude ]
		if gps.altitude_m is not None:
			if gps.height_geoid is not None:
				location.append(gps.altitude_m-gps.height_geoid)
			else:
				location.append(gps.altitude_m)
		else:
			location.append(0.)
	else:
		location = [ 0., 0., 0. ]
	info(str(location))
	return location

def show_location():
	info(measure_string())

def time():
	try:
		gps.update()
	except:
		pass
	if gps.has_fix:
		return "{:04}-{:02}-{:02}+{:02}:{:02}:{:02}UTC".format(
			gps.timestamp_utc.tm_year,
			gps.timestamp_utc.tm_mon,
			gps.timestamp_utc.tm_mday,
			gps.timestamp_utc.tm_hour,
			gps.timestamp_utc.tm_min,
			gps.timestamp_utc.tm_sec)
	else:
		return ""

if __name__ == "__main__":
	N = 8
	if 1:
		uart = busio.UART(board.TX, board.RX, baudrate=9600, timeout=10)
		setup_uart(uart, N)
	else:
		i2c = busio.I2C(board.SCL, board.SDA)
		setup_i2c(i2c, N)
	while True:
		show_location()
		time.sleep(1)

