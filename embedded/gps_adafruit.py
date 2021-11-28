# from https://learn.adafruit.com/adafruit-ultimate-gps-featherwing/circuitpython-library
# written 2021-11-28 by mza
# last updated 2021-11-28 by mza

import time
import board
import busio
import adafruit_gps
from DebugInfoWarningError24 import debug, info, warning, error, debug2, debug3, set_verbosity, create_new_logfile_with_string_embedded, flush

def setup_internal(delay_in_ms=1000):
	gps.send_command(b"PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0")
	gps.send_command(b'PMTK220,' + str(delay_in_ms))

def setup_uart(uart, delay_in_ms=1000):
	global gps
	gps = adafruit_gps.GPS(uart, debug=False)
	setup_internal(delay_in_ms)

def setup_i2c(i2c, delay_in_ms=1000):
	global gps
	gps = adafruit_gps.GPS_GtopI2C(i2c)
	setup_internal(delay_in_ms)

def header_string():
	return ", lat-deg, long-deg, #sat, alt/elev-m, HDOP-m"

def measure_string():
	try:
		gps.update()
	except:
		pass
	string = ""
	if gps.has_fix:
		string += ", %.6f" % gps.latitude
		string += ", %.6f" % gps.longitude
		#string += ", %d" % gps.fix_quality
		if gps.satellites is not None:
			string += ", %02d" % gps.satellites
		if gps.altitude_m is not None:
			if gps.height_geoid is not None:
				string += ", %.1f" % (gps.altitude_m-gps.height_geoid)
			else:
				string += ", %.1f" % gps.altitude_m
	#	if gps.speed_knots is not None:
	#		string += ", %.1f" % gps.speed_knots
	#	if gps.track_angle_deg is not None:
	#		string += ", %.1f" % gps.track_angle_deg
		if gps.horizontal_dilution is not None:
			string += ", %.2f" % gps.horizontal_dilution
	else:
		pass
		#info("Waiting for fix...")
	return string

def show_location():
	info(measure_string())

if __name__ == "__main__":
	if 1:
		uart = busio.UART(board.TX, board.RX, baudrate=9600, timeout=10)
		setup_uart(uart)
	else:
		i2c = busio.I2C(board.SCL, board.SDA)
		setup_i2c(i2c)
	while True:
		show_location()
		time.sleep(1)

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

