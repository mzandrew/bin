# from https://learn.adafruit.com/adafruit-ultimate-gps-featherwing/circuitpython-library
# written 2021-11-28 by mza
# last updated 2021-12-08 by mza

import time
import board
import busio
import adafruit_gps
import boxcar
from DebugInfoWarningError24 import debug, info, warning, error, debug2, debug3, set_verbosity, create_new_logfile_with_string_embedded, flush

shmepsilon = 1.5
DESIRED_PRECISION_DEGREES = 7
DESIRED_PRECISION_METERS = 3
MAX_TIMES_GPS_CAN_NOT_UPDATE_BEFORE_RESETTING_MICROCONTROLLER = 25
STORE_IN_DEGREES = False
if STORE_IN_DEGREES:
	DIVISOR = 1.
else:
	DIVISOR = 60.

def setup_internal(N, delay_in_ms=1000):
	#gps.send_command(b"PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0") # GLL, RMC, VTG, GGA, GSA, GSV, 0, 0, 0, 0, 0, 0, 0, MCHN
	gps.send_command(b"PMTK314,0,4,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0") # GLL, RMC, VTG, GGA, GSA, GSV, 0, 0, 0, 0, 0, 0, 0, MCHN
	gps.send_command(b'PMTK220,' + str(delay_in_ms))
	global myboxcar
	myboxcar = boxcar.boxcar(6, N, "gps")

def setup_uart(uart, N, delay_in_ms=1000):
	global gps
	gps = adafruit_gps.GPS(uart, debug=False) # set debug to True to print out NMEA sentences
	setup_internal(N, delay_in_ms)

def setup_i2c(i2c, N, delay_in_ms=1000):
	global gps
	gps = adafruit_gps.GPS_GtopI2C(i2c)
	setup_internal(N, delay_in_ms)

def has_fix():
	try:
		if 10<count_of_times_gps_did_not_update:
			return False
		else:
			return gps.has_fix
	except:
		return gps.has_fix

def try_to_update():
	global count_of_times_gps_did_not_update
	global last_gps_fix_time_monotonic
	updated = False
	try:
		for i in range(8):
			#info(str(gps.in_waiting))
			updated = gps.update()
			if updated:
				last_gps_fix_time_monotonic = time.monotonic()
				count_of_times_gps_did_not_update = 0
				break
			else:
				time.sleep(0.125)
		if not updated:
			try:
				count_of_times_gps_did_not_update += 1
			except:
				count_of_times_gps_did_not_update = 1
			duration = time.monotonic() - last_gps_fix_time_monotonic
			if 2<count_of_times_gps_did_not_update:
				warning("GPS did not get a fix for last " + str(count_of_times_gps_did_not_update) + " successive attempts (last " + str(duration) + " seconds)")
			string = gps.read(gps.in_waiting) # read whatever is waiting
			debug(string)
	except:
		warning("GPS did not update")
		try:
			count_of_times_gps_did_not_update += 1
		except:
			count_of_times_gps_did_not_update = 1
		try:
			duration = time.monotonic() - last_gps_fix_time_monotonic
		except:
			duration = time.monotonic()
		if 2<count_of_times_gps_did_not_update:
			warning("GPS did not get a fix for last " + str(count_of_times_gps_did_not_update) + " successive attempts (last " + str(duration) + " seconds)")
	if MAX_TIMES_GPS_CAN_NOT_UPDATE_BEFORE_RESETTING_MICROCONTROLLER<count_of_times_gps_did_not_update:
		error("resetting board...")
		time.sleep(1)
		info("")
		import microcontroller
		microcontroller.reset()

def get_values():
	try_to_update()
	values = [ 0., 0., 0., 0., 0., 0 ]
	if has_fix():
		hd = gps.horizontal_dilution
		if hd is not None and hd<shmepsilon:
			lat_deg = gps.latitude
			lon_deg = gps.longitude
			if STORE_IN_DEGREES:
				values = [ lat_deg, lon_deg, gps.altitude_m, gps.height_geoid, gps.horizontal_dilution, gps.satellites ]
				#values = [ round(lat_deg, DESIRED_PRECISION_DEGREES), round(lon_deg, DESIRED_PRECISION_DEGREES), round(gps.altitude_m, DESIRED_PRECISION_METERS), gps.height_geoid, gps.horizontal_dilution, gps.satellites ]
			else:
				lat_min = 60. * lat_deg
				lon_min = 60. * lon_deg
				values = [ lat_min, lon_min, gps.altitude_m, gps.height_geoid, gps.horizontal_dilution, gps.satellites ]
			myboxcar.accumulate(values)
	return values

def header_string():
	return ", lat-deg, long-deg, alt/elev-m, #sat, HDOP-m"

def measure_string():
	string = ""
	if has_fix():
		values = get_values()
		string += ", %.*f" % (DESIRED_PRECISION_DEGREES, values[0]/DIVISOR)
		string += ", %.*f" % (DESIRED_PRECISION_DEGREES, values[1]/DIVISOR)
		#string += ", %d" % gps.fix_quality
		if values[2] is not None:
			if values[3] is not None:
				string += ", %.*f" % (DESIRED_PRECISION_METERS, values[2] - values[3])
			else:
				string += ", %.*f" % (DESIRED_PRECISION_METERS, values[2])
	#	if gps.speed_knots is not None:
	#		string += ", %.1f" % gps.speed_knots
	#	if gps.track_angle_deg is not None:
	#		string += ", %.1f" % gps.track_angle_deg
		if values[5] is not None:
			string += ", %02d" % values[5]
		if values[4] is not None:
			string += ", %.2f" % values[4]
	else:
		try_to_update()
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
		location = [ location[0]/DIVISOR, location[1]/DIVISOR, location[2] - location[3] ]
		#info("location = " + str([ "%.6f" % z for z in location]))
		return location
	except:
		raise

def instantaneous_location():
	try_to_update()
	if has_fix():
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

def get_time():
	try:
		duration = time.monotonic() - last_gps_fix_time_monotonic
	except:
		duration = time.monotonic()
	if 1.0<duration:
		try_to_update()
	if has_fix():
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

