#!/usr/bin/env python3

# written 2024-06-26 by mza
# from https://learn.adafruit.com/adafruit-mcp9601/python-circuitpython
# last updated 2024-07-25 by mza

# to install:
# cp -ar adafruit_mcp9600.mpy adafruit_register* /media/mza/THERMOCOUPL/lib/
# cp -a boxcar.py DebugInfoWarningError24.py /media/mza/THERMOCOUPL/
# cp -a thermocouple.py /media/mza/THERMOCOUPL/code.py; sync

import analogio
import adafruit_mcp9600
import boxcar
from DebugInfoWarningError24 import debug, info, warning, error, debug2

mode = "none"
number_of_sensors = 0

def setup_analog(pin_list, N=32):
	global mode
	mode = "analog"
	global sensor
	sensor = []
	for pin in pin_list:
		try:
			sensor.append(analogio.AnalogIn(pin))
		except (KeyboardInterrupt, ReloadException):
			raise
		except OSError as e:
			print("exception OSError (thermocouple): " + str(e))
			raise
		except RuntimeError as e:
			print("exception RuntimeError (thermocouple): " + str(e))
			raise
		except Exception as e:
			print("exception (thermocouple): " + str(e))
			raise
	global number_of_sensors
	number_of_sensors = len(sensor)
	global myboxcar
	myboxcar = boxcar.boxcar(number_of_sensors, N, "thermocouple")
	return 103

def setup_i2c(i2c, N=32):
	global mode
	mode = "i2c"
	global sensor
	try:
		sensor = adafruit_mcp9600.MCP9600(i2c)
	except (KeyboardInterrupt, ReloadException):
		raise
	except OSError as e:
		print("exception OSError (thermocouple): " + str(e))
		raise
	except RuntimeError as e:
		print("exception RuntimeError (thermocouple): " + str(e))
		raise
	except Exception as e:
		print("exception (thermocouple): " + str(e))
		raise
	global number_of_sensors
	number_of_sensors = 2
	global myboxcar
	myboxcar = boxcar.boxcar(2, N, "mcp9600")
	return 103

ADC_MAX_VOLAGE = 3.3
ADC_MAX_COUNT = 2**16
gain = ADC_MAX_VOLAGE/(ADC_MAX_COUNT*0.005)
offset = 0.0

def get_values():
	try:
		if "i2c"==mode:
			values = [ sensor.ambient_temperature, sensor.temperature ]
		elif "analog"==mode:
			values = [ gain*sensor[i].value+offset for i in range(number_of_sensors) ]
		else:
			print("?")
	except (KeyboardInterrupt, ReloadException):
		raise
	except:
		values = [ 0.0 for i in range(number_of_sensors) ]
	myboxcar.accumulate(values)
	return values

def measure_string():
	if "i2c"==mode:
		ambient, remote = get_values()
		return ", %.1f, %.1f" % (ambient, remote)
	elif "analog"==mode:
		values = get_values()
		string = ""
		for i in range(len(values)):
			string += ", %.1f" % values[i] 
		return string
	else:
		print("?")

def show_average_values():
	#myboxcar.show_average_values()
	if "i2c"==mode:
		ambient, remote = get_average_values()
		print(", %.1f, %.1f" % (ambient, remote))
	elif "analog"==mode:
		values = get_average_values()
		string = ""
		for i in range(len(values)):
			string += ", %.1f" % values[i] 
		print(string)
	else:
		print("?")

def get_average_values():
	return myboxcar.get_average_values()

def print_compact():
	#date = time.strftime("%Y-%m-%d+%X")
	string = measure_string()
	#info("%s, %s" % (date, string))
	info("%s" % (string))

def print_header():
	print(", ambient, remote")

if __name__ == "__main__":
	intended_mode = "analog"
	print()
	import time, re, board, busio, simpleio
	match = re.search("feather_esp32s", board.board_id)
	if match:
		tft_i2c_power = simpleio.DigitalOut(board.TFT_I2C_POWER, value=0)
		time.sleep(1.0)
		tft_i2c_power.value = 1
		time.sleep(0.5)
	if "i2c"==intended_mode:
		i2c = busio.I2C(board.SCL, board.SDA, frequency=100000)
		try:
			setup_i2c(i2c, 32)
		except (KeyboardInterrupt, ReloadException):
			raise
		except Exception as e:
			print("exception (thermocouple): " + str(e))
			i2c.try_lock()
			print("i2c.scan(): " + str(i2c.scan()))
			i2c.unlock()
			raise
	elif "analog"==intended_mode:
		setup_analog([board.A0, board.A1, board.A2, board.A3, board.A4, board.A5], 32)
	else:
		print("?")
	print_header()
	i = 0
	while True:
		if 32<i:
			get_values()
			show_average_values()
		else:
			print_compact()
		i += 1
		time.sleep(1)

