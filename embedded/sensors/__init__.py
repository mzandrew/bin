# written 2020-11-25 by mza
# from sensor_readout.py
# last updated 2024-07-01 by mza

import sys
import board, busio
sys.path.append("sensors")

# ------------- i2c: ----------------
# unimplemented: "gps_adafruit" # i2c or uart

# temperature, humidity, pressure, etc:
am2320_present       = False
bme680_present       = False
pct2075_present      = False
sht31d_present       = False
thermocouple_present = False
# light, lux, proximity:
as7341_present   = False
bh1750_present   = False
ltr390_present   = False
tsl2591_present  = False
vcnl4040_present = False
# current, voltage, power:
ina260_present = False
# battery monitoring:
lc709203f_present       = False
battery_monitor_present = False
# other:
pm25_present = False
# rtc:
ds3231_present  = False
pcf8523_present = False

# temperature, humidity, pressure, etc:
should_use_am2320       = True
should_use_bme680       = True
should_use_pct2075      = True
should_use_sht31d       = True
should_use_thermocouple = True
# light, lux, proximity:
should_use_as7341   = True
should_use_bh1750   = True
should_use_ltr390   = True
should_use_tsl2591  = True
should_use_vcnl4040 = True
# current, voltage, power:
should_use_ina260 = True
# battery monitoring:
should_use_lc709203f       = True
should_use_battery_monitor = True
# other:
should_use_pm25 = True
# rtc:
should_use_ds3231  = True
should_use_pcf8523 = True

import am2320_adafruit, bme680_adafruit, pct2075_adafruit, sht31d_adafruit, thermocouple
import as7341_adafruit, bh1750_adafruit, ltr390_adafruit, tsl2591_adafruit, vcnl4040_adafruit
import ina260_adafruit
import lc709203f_adafruit, battery_monitor
import pm25_adafruit
import ds3231_adafruit, pcf8523_adafruit

def scan_i2c_bus(i2c):
	i2c.try_lock()
	print("i2c.scan(): " + str(i2c.scan()))
	i2c.unlock()

def setup_i2c_sensors(i2c, N=32):
	global as7341_present, bh1750_present, ina260_present, lc709203f_present, battery_monitor_present, ltr390_present, pct2075_present, pm25_present, sht31d_present, thermocouple, tsl2591_present, vcnl4040_present, bme680_present, am2320_present, ds3231_present, pcf8523_present
	# temperature, humidity, pressure, etc:
	try:
		if should_use_am2320:
			am2320_adafruit.setup(i2c, N); am2320_present = True
	except (KeyboardInterrupt, ReloadException):
		raise
	except Exception as e:
		pass
	try:
		if should_use_bme680:
			bme680_adafruit.setup(i2c, N); bme680_present = True
	except (KeyboardInterrupt, ReloadException):
		raise
	except Exception as e:
		pass
	try:
		if should_use_sht31d:
			sht31d_adafruit.setup(i2c, N); sht31d_present = True
	except (KeyboardInterrupt, ReloadException):
		raise
	except Exception as e:
		pass
	try:
		if should_use_thermocouple:
			thermocouple.setup_i2c(i2c, N); thermocouple_present = True
	except (KeyboardInterrupt, ReloadException):
		raise
	except Exception as e:
		print("exception (thermocouple): " + str(e))
		pass
	# light, lux, proximity:
	try:
		if should_use_as7341:
			as7341_adafruit.setup(i2c, N); as7341_present = True
	except (KeyboardInterrupt, ReloadException):
		raise
	except Exception as e:
		pass
	try:
		if should_use_bh1750:
			bh1750_adafruit.setup(i2c, N); bh1750_present = True
	except (KeyboardInterrupt, ReloadException):
		raise
	except Exception as e:
		pass
	try:
		if should_use_ltr390:
			ltr390_adafruit.setup(i2c, N); ltr390_present = True
	except (KeyboardInterrupt, ReloadException):
		raise
	except Exception as e:
		pass
	try:
		if should_use_tsl2591:
			tsl2591_adafruit.setup(i2c, N); tsl2591_present = True
	except (KeyboardInterrupt, ReloadException):
		raise
	except Exception as e:
		pass
	try:
		if should_use_vcnl4040:
			vcnl4040_adafruit.setup(i2c, N); vcnl4040_present = True
	except (KeyboardInterrupt, ReloadException):
		raise
	except Exception as e:
		pass
	# current, voltage, power:
	try:
		if should_use_ina260:
			ina260_adafruit.setup(i2c, N, address=0x40); ina260_present = True
	except (KeyboardInterrupt, ReloadException):
		raise
	except Exception as e:
		pass
	# battery monitoring:
	try:
		if should_use_lc709203f:
			lc709203f_adafruit.setup(i2c, N); lc709203f_present = True
	except (KeyboardInterrupt, ReloadException):
		raise
	except Exception as e:
		pass
	try:
		battery_monitor.setup(i2c, N); battery_monitor_present = True
	except (KeyboardInterrupt, ReloadException):
		raise
	except Exception as e:
		pass
	# other:
	try:
		if should_use_pm25:
			pm25_adafruit.setup(i2c, N); pm25_present = True
	except (KeyboardInterrupt, ReloadException):
		raise
	except Exception as e:
		pass
	# rtc:
	try:
		if should_use_ds3231:
			ds3231_adafruit.setup(i2c); ds3231_present = True
	except (KeyboardInterrupt, ReloadException):
		raise
	except Exception as e:
		pass
# something went wrong with this adafruit library since the last time we used this rtc:
#	try:
#		if should_use_pcf8523:
#			pcf8523_adafruit.setup(i2c); pcf8523_present = True
#	except (KeyboardInterrupt, ReloadException):
#		raise
#	except Exception as e:
#		raise
#		pass
# the following needs a prohibited address list or it accidentally matches some devices:
#	try:
#		if should_use_pct2075:
#			pct2075_adafruit.setup(i2c, N); pct2075_present = True
#	except (KeyboardInterrupt, ReloadException):
#		raise
#	except Exception as e:
#		pass

# --------------- spi -------------------
#spi_list = [ "max31865_adafruit" ]

max31865_present = False

import max31865_adafruit

def setup_spi_sensors(spi, cs_pin_list, N=32):
	global max31865_present
	for cs_pin in cs_pin_list:
		try:
			max31865_adafruit.setup(spi, cs_pin, N); max31865_present = True
		except (KeyboardInterrupt, ReloadException):
			raise
		except:
			pass

# --------------- onewire -------------------
#onewire_list = [ "ds18b20_adafruit" ]

ds18b20_present = False

import ds18b20_adafruit

def setup_onewire_sensors(ow_bus, N=32):
	try:
		ds18b20_adafruit.setup(ow_bus, N); ds18b20_present = True
	except (KeyboardInterrupt, ReloadException):
		raise
	except:
		pass

# --------------- other -------------------
#other_list = [ "anemometer" ]

# unimplemented: "anemometer" # analog

#def setup_analog_sensors() # need to have a pin list (could try all board.A0, etc...)

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
	if battery_monitor_present:
		values['battery_monitor'] = battery_monitor.get_values()
	# other:
	if pm25_present:
		values['pm25'] = pm25_adafruit.get_values()
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
	if battery_monitor_present:
		print(battery_monitor.measure_string())
	# other:
	if pm25_present:
		print(pm25_adafruit.measure_string())
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
	if battery_monitor_present:
		values['battery_monitor'] = battery_monitor.get_average_values()
	# other:
	if pm25_present:
		values['pm25'] = pm25_adafruit.get_average_values()
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
	if battery_monitor_present:
		battery_monitor.show_average_values()
	# other:
	if pm25_present:
		pm25_adafruit.show_average_values()
	# rtc:
	if ds3231_present:
		ds3231_adafruit.get_values()
#	if pcf8523_present:
#		pcf8523_adafruit.get_values()

