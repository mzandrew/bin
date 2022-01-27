# https://learn.adafruit.com/diy-air-quality-monitor/code-usage
# https://github.com/adafruit/Adafruit_CircuitPython_PM25/blob/main/adafruit_pm25/__init__.py
# https://github.com/adafruit/Adafruit_CircuitPython_PM25/blob/main/adafruit_pm25/i2c.py
# written 2021-11-25 by mza
# last updated 2021-11-25 by mza

import time
import board
import busio
from adafruit_pm25.i2c import PM25_I2C
import boxcar

def setup(i2c, N):
	global pm25
	reset_pin = None
	pm25 = PM25_I2C(i2c, reset_pin)
	global myboxcar
	myboxcar = boxcar.boxcar(12, N, "pm25")
	return 0x12

def test_if_present():
	try:
		pm25.read()
	except:
		print("pm25 not present")
		return False
	return True

def get_values():
	# dict ordering should be:
	# "pm10 standard" "pm25 standard" "pm100 standard"
	# "pm10 env" "pm25 env" "pm100 env"
	# "particles 03um" "particles 05um" "particles 10um"
	# "particles 25um" "particles 50um" "particles 100um"
	try:
		values = list(pm25.read().values())
	except:
		values = [ .0, .0, .0, .0, .0, .0, .0, .0, .0, .0, .0, .0 ]
	myboxcar.accumulate(values)
	return values

def show_average_values():
	myboxcar.show_average_values()

def get_average_values():
	return myboxcar.get_average_values()

def get_previous_values():
	return myboxcar.previous_values()

def measure_string():
	values = get_values()
	return ", %.2f, %.2f, %.2f, %.2f, %.2f, %.2f, %.2f, %.2f, %.2f, %.2f, %.2f, %.2f" % ( values[0], values[1], values[2], values[3], values[4], values[5], values[6], values[7], values[8], values[9], values[10], values[11] )

def print_compact():
	print(measure_string())

if __name__ == "__main__":
	i2c = busio.I2C(board.SCL1, board.SDA1)
	#i2c = board.I2C()
	setup(i2c)
	while test_if_present():
		print_compact()
		time.sleep(1)

