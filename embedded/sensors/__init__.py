# written 2020-11-25 by mza
# from sensor_readout.py
# last updated 2024-06-29 by mza

import sys
import board, busio
sys.path.append("sensors")

#light_sensors = [ "as7341_adafruit", "bh1750_adafruit", "ltr390_adafruit", "tsl2591_adafruit", "vcnl4040_adafruit" ]
#temperature_humidity_pressure_sensors = [ "bme680_adafruit" ]
#temperature_humidity_sensors = [ "am2320_adafruit", "sht31d_adafruit" ]
#temperature_sensors = [ "ds18b20_adafruit", "max31865_adafruit", "pct2075_adafruit", "thermocouple" ]
#temperature_sensors.extend(temperature_humidity_sensors)
#temperature_sensors.extend(temperature_humidity_pressure_sensors)
#temperature_sensors.sort()
#rtcs = [ "ds3231_adafruit", "pcf8523_adafruit" ]
#voltage_current_measurement = [ "ina260_adafruit" ]
#battery_monitors = [ "lc709203f_adafruit" ]
#gpio_expanders = [ "aw9523_adafruit" ]
#other = [ "anemometer", "pm25_adafruit" ]

#all_sensors = []
#for each_list in [ light_sensors, temperature_sensors, rtcs, voltage_current_measurement, battery_monitors, gpio_expanders, other ]:
#	all_sensors.extend(each_list)
#print(str(all_sensors))

# list all sensors here by interface type:
#spi_list = [ "max31865_adafruit" ]
#onewire_list = [ "ds18b20_adafruit" ]
#other_list = [ "anemometer" ]
#i2c_list = [ "as7341_adafruit", "bh1750_adafruit", "ina260_adafruit", "lc709203f_adafruit", "ltr390_adafruit", "pct2075_adafruit", "pm25_adafruit", "sht31d_adafruit", "thermocouple", "tsl2591_adafruit", "vcnl4040_adafruit", "bme680_adafruit", "am2320_adafruit", "aw9523_adafruit", "ds3231_adafruit", "pcf8523_adafruit" ]

#def check_list_try1(list_of_things, bus):
#	print(str(bus))
##	global sensors
#	for each in list_of_things:
##		try:
##			__import__(each) # works to check that it would import, but doesn't actually import...
##			#eval("import(" + str(each) + ")") # SyntaxError: invalid syntax
##			#exec("import(" + str(each) + ")") # SyntaxError: invalid syntax
##			#importlib.import_module(each) # not available in circuitpython
##		except (KeyboardInterrupt, ReloadException):
##			raise
##		except Exception as e:
##			print("Exception (import): " + str(each) + ": " + str(e))
##			continue
#		try:
##			pass
#			#import adafruit_max31865
#			#import max31865_adafruit
#			max31865_adafruit.setup(spi)
#			#exec(str(each) + ".setup(bus)")
#			#sensors.append(each)
#		except (KeyboardInterrupt, ReloadException):
#			raise
#		except Exception as e:
#			print("Exception (setup): " + str(each) + ": " + str(e))
#			continue

#def setup_try1():
#	try:
#		spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
#		check_list(spi_list, spi)
#	except (KeyboardInterrupt, ReloadException):
#		raise
#	except Exception as e:
#		print("Exception (spi): " + str(e))
#	try:
#		#i2c = busio.I2C(board.SCL, board.SDA)
#		i2c = busio.I2C(board.SCL1, board.SDA1)
#		check_list(i2c_list, i2c)
#	except (KeyboardInterrupt, ReloadException):
#		raise
#	except Exception as e:
#		print("Exception (i2c): " + str(e))
#	try:
#		check_list(other_list, other)
#	except (KeyboardInterrupt, ReloadException):
#		raise
#	except Exception as e:
#		print("Exception (other): " + str(e))
#	try:
#		check_list(onewire_list, onewire)
#	except (KeyboardInterrupt, ReloadException):
#		raise
#	except Exception as e:
#		print("Exception (onewire): " + str(e))
#	#print("sensors: " + str(sensors))

# ------------- i2c: ----------------
#i2c_list = [ "as7341_adafruit", "bh1750_adafruit", "ina260_adafruit", "lc709203f_adafruit", "ltr390_adafruit", "pct2075_adafruit", "pm25_adafruit", "sht31d_adafruit", "thermocouple", "tsl2591_adafruit", "vcnl4040_adafruit", "bme680_adafruit", "am2320_adafruit", "aw9523_adafruit", "ds3231_adafruit", "pcf8523_adafruit" ]

as7341_present       = False
bh1750_present       = False
ina260_present       = False
lc709203f_present    = False
ltr390_present       = False
pct2075_present      = False
pm25_present         = False
sht31d_present       = False
thermocouple_present = False
tsl2591_present      = False
vcnl4040_present     = False
bme680_present       = False
am2320_present       = False
aw9523_present       = False
ds3231_present       = False
pcf8523_present      = False

import bme680_adafruit, pct2075_adafruit, ina260_adafruit, as7341_adafruit, bh1750_adafruit, lc709203f_adafruit, ltr390_adafruit, pm25_adafruit, sht31d_adafruit, thermocouple, tsl2591_adafruit, vcnl4040_adafruit, am2320_adafruit, ds3231_adafruit, pcf8523_adafruit

def setup_i2c_sensors(i2c, N=32):
	global as7341_present, bh1750_present, ina260_present, lc709203f_present, ltr390_present, pct2075_present, pm25_present, sht31d_present, thermocouple, tsl2591_present, vcnl4040_present, bme680_present, am2320_present, aw9523_present, ds3231_present, pcf8523_present
	try:
		bme680_adafruit.setup(i2c, N); bme680_present = True
	except:
		pass
	try:
		ina260_adafruit.setup(i2c, N, address=0x40); ina260_present = True
	except:
		pass
	try:
		as7341_adafruit.setup(i2c, N); as7341_present = True
	except:
		pass
	try:
		bh1750_adafruit.setup(i2c, N); bh1750_present = True
	except:
		pass
	try:
		lc709203f_adafruit.setup(i2c, N); lc709203f_present = True
	except:
		pass
	try:
		ltr390_adafruit.setup(i2c, N); ltr390_present = True
	except:
		pass
	try:
		pm25_adafruit.setup(i2c, N); pm25_present = True
	except:
		pass
	try:
		sht31d_adafruit.setup(i2c, N); sht31d_present = True
	except:
		pass
	try:
		thermocouple.setup(i2c, N); thermocouple_present = True
	except:
		pass
	try:
		tsl2591_adafruit.setup(i2c, N); tsl2591_present = True
	except:
		pass
	try:
		vcnl4040_adafruit.setup(i2c, N); vcnl4040_present = True
	except:
		pass
	try:
		am2320_adafruit.setup(i2c, N); am2320_present = True
	except:
		pass
# the following is a gpio expander and doesn't really fit the pattern of "sensors":
#	try:
#		aw9523_adafruit.setup(i2c); aw9523_present = True
#	except:
#		raise
#		pass
	try:
		ds3231_adafruit.setup(i2c); ds3231_present = True
	except:
		pass
# something went wrong with this adafruit library since the last time we used this rtc:
#	try:
#		pcf8523_adafruit.setup(i2c); pcf8523_present = True
#	except:
#		raise
#		pass
# the following needs a prohibited address list or it accidentally matches some devices:
#	try:
#		pct2075_adafruit.setup(i2c, N); pct2075_present = True
#	except:
#		pass

# --------------- spi -------------------
#spi_list = [ "max31865_adafruit" ]

max31865_present = False

import max31865_adafruit

def setup_spi_sensors(spi, N=32):
	global max31865_present
	try:
		max31865_adafruit.setup(spi, N); max31865_present = True
	except:
		pass

# --------------- onewire -------------------
#onewire_list = [ "ds18b20_adafruit" ]

ds18b20_present = False

import ds18b20_adafruit

def setup_onewire_sensors(ow_bus, N=32):
	try:
		ds18b20_adafruit.setup(ow_bus, N); ds18b20_present = True
	except:
		pass

# --------------- other -------------------
#other_list = [ "anemometer" ]

# --------------- common -------------------

def get_values():
	values = {}
	# temperature, humidity, pressure, etc:
	if am2320_present:
		values['am2320'] = am2320_adafruit.get_values()
	if bme680_present:
		values['bme680'] = bme680_adafruit.get_values()
	if ds18b20_present:
		values['ds18b20'] = ds18b20_adafruit.get_values()
	if max31865_present:
		values['max31865'] = max31865_adafruit.get_values()
	if pct2075_present:
		values['pct2075'] = pct2075_adafruit.get_values()
	if sht31d_present:
		values['sht31d'] = sht31d_adafruit.get_values()
	if thermocouple_present:
		values['thermocouple'] = thermocouple.get_values()
	# light, lux, proximity:
	if as7341_present:
		values['as7341'] = as7341_adafruit.get_values()
	if bh1750_present:
		values['bh1750'] = bh1750_adafruit.get_values()
	if ltr390_present:
		values['ltr390'] = ltr390_adafruit.get_values()
	if tsl2591_present:
		values['tsl2591'] = tsl2591_adafruit.get_values()
	if vcnl4040_present:
		values['vcnl4040'] = vcnl4040_adafruit.get_values()
	# current, voltage, power:
	if ina260_present:
		values['ina260'] = ina260_adafruit.get_values()
	# battery monitoring:
	if lc709203f_present:
		values['lc709203f'] = lc709203f_adafruit.get_values()
	# other:
	if pm25_present:
		values['pm25'] = pm25_adafruit.get_values()
	# gpio:
#	if aw9523_present:
#		values['aw9523'] = aw9523_adafruit.get_values()
	# rtc:
	if ds3231_present:
		values['ds3231'] = ds3231_adafruit.get_values()
#	if pcf8523_present:
#		values['pcf8523'] = pcf8523_adafruit.get_values()
	return values

def show_values():
	# temperature, humidity, pressure, etc:
	if am2320_present:
		print(am2320_adafruit.measure_string())
	if bme680_present:
		print(bme680_adafruit.measure_string())
	if ds18b20_present:
		print(ds18b20_adafruit.measure_string())
	if max31865_present:
		print(max31865_adafruit.measure_string())
	if pct2075_present:
		print(pct2075_adafruit.measure_string())
	if sht31d_present:
		print(sht31d_adafruit.measure_string())
	if thermocouple_present:
		print(thermocouple.measure_string())
	# light, lux, proximity:
	if as7341_present:
		print(as7341_adafruit.measure_string())
	if bh1750_present:
		print(bh1750_adafruit.measure_string())
	if ltr390_present:
		print(ltr390_adafruit.measure_string())
	if tsl2591_present:
		print(tsl2591_adafruit.measure_string())
	if vcnl4040_present:
		print(vcnl4040_adafruit.measure_string())
	# current, voltage, power:
	if ina260_present:
		print(ina260_adafruit.measure_string())
	# battery monitoring:
	if lc709203f_present:
		print(lc709203f_adafruit.measure_string())
	# other:
	if pm25_present:
		print(pm25_adafruit.measure_string())
	# gpio:
#	if aw9523_present:
#		print(aw9523_adafruit.measure_string())
	# rtc:
	if ds3231_present:
		print(ds3231_adafruit.measure_string())
#	if pcf8523_present:
#		print(pcf8523_adafruit.measure_string())

def get_average_values():
	values = {}
	# temperature, humidity, pressure, etc:
	if am2320_present:
		values['am2320'] = am2320_adafruit.get_average_values()
	if bme680_present:
		values['bme680'] = bme680_adafruit.get_average_values()
	if ds18b20_present:
		values['ds18b20'] = ds18b20_adafruit.get_average_values()
	if max31865_present:
		values['max31865'] = max31865_adafruit.get_average_values()
	if pct2075_present:
		values['pct2075'] = pct2075_adafruit.get_average_values()
	if sht31d_present:
		values['sht31d'] = sht31d_adafruit.get_average_values()
	if thermocouple_present:
		values['thermocouple'] = thermocouple.get_average_values()
	# light, lux, proximity:
	if as7341_present:
		values['as7341'] = as7341_adafruit.get_average_values()
	if bh1750_present:
		values['bh1750'] = bh1750_adafruit.get_average_values()
	if ltr390_present:
		values['ltr390'] = ltr390_adafruit.get_average_values()
	if tsl2591_present:
		values['tsl2591'] = tsl2591_adafruit.get_average_values()
	if vcnl4040_present:
		values['vcvl4040'] = vcnl4040_adafruit.get_average_values()
	# current, voltage, power:
	if ina260_present:
		values['ina260'] = ina260_adafruit.get_average_values()
	# battery monitoring:
	if lc709203f_present:
		values['lc709203f'] = lc709203f_adafruit.get_average_values()
	# other:
	if pm25_present:
		values['pm25'] = pm25_adafruit.get_average_values()
	# gpio:
#	if aw9523_present:
#		values['aw9523'] = aw9523_adafruit.get_average_values()
	# rtc:
	if ds3231_present:
		values['ds3231'] = ds3231_adafruit.get_values()
#	if pcf8523_present:
#		values['pcf8523'] = pcf8523_adafruit.get_values()
	return values

def show_average_values():
	# temperature, humidity, pressure, etc:
	if am2320_present:
		am2320_adafruit.show_average_values()
	if bme680_present:
		bme680_adafruit.show_average_values()
	if ds18b20_present:
		ds18b20_adafruit.show_average_values()
	if max31865_present:
		max31865_adafruit.show_average_values()
	if pct2075_present:
		pct2075_adafruit.show_average_values()
	if sht31d_present:
		sht31d_adafruit.show_average_values()
	if thermocouple_present:
		thermocouple.show_average_values()
	# light, lux, proximity:
	if as7341_present:
		as7341_adafruit.show_average_values()
	if bh1750_present:
		bh1750_adafruit.show_average_values()
	if ltr390_present:
		ltr390_adafruit.show_average_values()
	if tsl2591_present:
		tsl2591_adafruit.show_average_values()
	if vcnl4040_present:
		vcnl4040_adafruit.show_average_values()
	# current, voltage, power:
	if ina260_present:
		ina260_adafruit.show_average_values()
	# battery monitoring:
	if lc709203f_present:
		lc709203f_adafruit.show_average_values()
	# other:
	if pm25_present:
		pm25_adafruit.show_average_values()
	# gpio:
#	if aw9523_present:
#		aw9523_adafruit.show_average_values()
	# rtc:
	if ds3231_present:
		ds3231_adafruit.get_values()
#	if pcf8523_present:
#		pcf8523_adafruit.get_values()

