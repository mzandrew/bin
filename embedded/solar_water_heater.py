# written 2021-09-10 by mza
# last updated 2022-01-12 by mza

# to install on a circuitpython device:
# rsync -av *.py /media/circuitpython/
# cp -a solar_water_heater.py /media/circuitpython/code.py
# cd ~/build/adafruit-circuitpython/bundle/lib
# rsync -r simpleio.mpy adafruit_esp32spi adafruit_register adafruit_sdcard.mpy adafruit_pct2075.mpy adafruit_bh1750.mpy adafruit_vcnl4040.mpy adafruit_ltr390.mpy neopixel.mpy adafruit_as7341.mpy adafruit_pcf8523.mpy adafruit_tsl2591.mpy adafruit_onewire adafruit_ds18x20.mpy adafruit_pm25 adafruit_gps.mpy adafruit_sht31d.mpy adafruit_io adafruit_ili9341.mpy adafruit_requests.mpy /media/circuitpython/lib/

header_string = "date/time"
mydir = "/logs"
should_use_airlift = True
if 0: # for the one with the TFT and GPS but no adalogger
	FEATHER_ESP32S2 = True
	use_pwm_status_leds = False
	should_use_sdcard = False
	should_use_RTC = False
	should_use_display = True
	should_use_gps = True
	wifi_mapping_mode = True
	cat_on_a_hot_tin_roof_mode = False
	N = 8
	gps_delay_in_ms = 1000
	delay_between_acquisitions = 2. * gps_delay_in_ms/1000.
	delay_between_posting_and_next_acquisition = 2.0
	use_built_in_wifi = True
else: # cat on a hot tin roof
	FEATHER_ESP32S2 = False
	use_pwm_status_leds = True
	should_use_sdcard = True
	should_use_RTC = True
	should_use_display = False
	should_use_gps = False
	wifi_mapping_mode = False
	cat_on_a_hot_tin_roof_mode = True
	N = 32
	delay_between_acquisitions = 0.75
	gps_delay_in_ms = 2000
	delay_between_posting_and_next_acquisition = 4.0
	use_built_in_wifi = False

import sys
import time
import atexit
import supervisor
import board
import busio
import pwmio
import simpleio
from adafruit_onewire.bus import OneWireBus
import pct2075_adafruit
import bh1750_adafruit
import ltr390_adafruit
import vcnl4040_adafruit
import as7341_adafruit
import pcf8523_adafruit
import microsd_adafruit
import neopixel_adafruit
import pm25_adafruit
import ds18b20_adafruit
import tsl2591_adafruit
import anemometer
import sht31d_adafruit
import airlift
import gps_adafruit
from DebugInfoWarningError24 import debug, info, warning, error, debug2, debug3, set_verbosity, create_new_logfile_with_string_embedded, flush
import generic
import display_adafruit

# https://learn.adafruit.com/circuitpython-essentials/circuitpython-pwm
PWM_MAX = 65535
def setup_status_leds(red_pin, green_pin, blue_pin):
	global status_led
	status_led = []
	status_led.append(pwmio.PWMOut(red_pin,   frequency=5000, duty_cycle=PWM_MAX))
	status_led.append(pwmio.PWMOut(green_pin, frequency=5000, duty_cycle=PWM_MAX))
	status_led.append(pwmio.PWMOut(blue_pin,  frequency=5000, duty_cycle=PWM_MAX))

def set_status_led_color(desired_color):
	global status_led
	for i in range(3):
		duty_cycle = int(PWM_MAX - 1.0*PWM_MAX*desired_color[i])
		if duty_cycle<0:
			duty_cycle = 0
		if PWM_MAX<duty_cycle:
			duty_cycle = PWM_MAX
		status_led[i].duty_cycle = duty_cycle

def print_compact(string):
	date = ""
	if ""==date:
		try:
			date = time.strftime("%Y-%m-%d+%X")
		except:
			pass
	if ""==date and RTC_is_available:
		try:
			date = pcf8523_adafruit.get_timestring1()
		except:
			pass
	if ""==date and gps_is_available:
		try:
			date = gps_adafruit.get_time()
		except:
			pass
	info("%s%s" % (date, string))

def print_header():
	info("" + header_string)

def main():
	global header_string
	if use_pwm_status_leds:
		setup_status_leds(red_pin=board.A2, green_pin=board.D9, blue_pin=board.A3)
		set_status_led_color([1.0, 1.0, 1.0])
	if FEATHER_ESP32S2: # for feather esp32-s2 to turn on power to i2c bus:
		simpleio.DigitalOut(board.D7, value=0)
	global i2c
	try:
		i2c = busio.I2C(board.SCL1, board.SDA1)
		string = "using I2C1 "
	except:
		#i2c = busio.I2C(board.SCL, board.SDA)
		i2c = board.I2C()
		string = "using I2C0 "
	info(string)
	#i2c.try_lock()
	#i2c_list = i2c.scan()
	#i2c.unlock()
	#info(string + str(i2c_list))
	displayio.release_displays()
	global spi
	spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
	global uart
	uart = busio.UART(board.TX, board.RX, baudrate=9600, timeout=10)
	prohibited_addresses = []
	global RTC_is_available
	if should_use_RTC:
		try:
			i2c_address = pcf8523_adafruit.setup(i2c)
			prohibited_addresses.append(i2c_address)
			RTC_is_available = True
		except:
			RTC_is_available = False
	else:
		RTC_is_available = False
	global display_is_available
	if should_use_display:
		display_is_available = display_adafruit.setup_ili9341(spi, board.D9, board.D10)
	global sdcard_is_available
	global mydir
	if should_use_sdcard:
		sdcard_is_available = microsd_adafruit.setup_sdcard_for_logging_data(spi, board.D10, mydir) # D10 = adalogger featherwing
	else:
		sdcard_is_available = False
	if not sdcard_is_available:
		mydir = "/"
	if RTC_is_available:
		create_new_logfile_with_string_embedded(mydir, "solar_water_heater", pcf8523_adafruit.get_timestring2())
	else:
		create_new_logfile_with_string_embedded(mydir, "solar_water_heater")
	global gps_is_available
	if should_use_gps:
		if 1:
			gps_adafruit.setup_uart(uart, N, gps_delay_in_ms)
		else:
			gps_adafruit.setup_i2c(i2c, N, gps_delay_in_ms)
		gps_is_available = True
		header_string += gps_adafruit.header_string()
	else:
		gps_is_available = False
	global bh1750_is_available
	try:
		i2c_address = bh1750_adafruit.setup(i2c, N)
		prohibited_addresses.append(i2c_address)
		bh1750_is_available = True
		header_string += ", bh1750-lux"
	except:
		warning("bh1750 not found")
		bh1750_is_available = False
	global ltr390_is_available
	try:
		i2c_address = ltr390_adafruit.setup(i2c, N)
		prohibited_addresses.append(i2c_address)
		ltr390_is_available = True
		header_string += ", ltr390-uvs, ltr390-uvi, ltr390-light, ltr390-lux"
	except:
		warning("ltr390 not found")
		ltr390_is_available = False
	global vcnl4040_is_available
	try:
		i2c_address = vcnl4040_adafruit.setup(i2c, N)
		prohibited_addresses.append(i2c_address)
		vcnl4040_is_available = True
		header_string += ", vcnl4040-proximity, vcnl4040-lux"
	except:
		warning("vcnl4040 not found")
		vcnl4040_is_available = False
	global as7341_is_available
	try:
		i2c_address = as7341_adafruit.setup(i2c, N)
		prohibited_addresses.append(i2c_address)
		as7341_is_available = True
		header_string += ", as7341-415nm, as7341-445nm, as7341-480nm, as7341-515nm, as7341-555nm, as7341-590nm, as7341-630nm, as7341-680nm"
	except:
		warning("as7341 not found")
		as7341_is_available = False
	global tsl2591_is_available
	try:
		i2c_address = tsl2591_adafruit.setup(i2c, N)
		prohibited_addresses.append(i2c_address)
		tsl2591_is_available = True
		header_string += ", tsl2591.lux, tsl2591.infrared, tsl2591.visible, tsl2591.full-spectrum"
	except:
		warning("tsl2591 not found")
		tsl2591_is_available = False
	global neopixel_is_available
	try:
		neopixel_is_available = neopixel_adafruit.setup_neopixel()
	except:
		warning("error setting up neopixel")
	global anemometer_is_available
	try:
		anemometer_is_available = anemometer.setup(board.A0, N)
		header_string += ", anemometer-m/s"
	except:
		warning("anemometer not found")
		anemometer_is_available = False
	global pm25_is_available
	try:
		i2c_address = pm25_adafruit.setup(i2c, N)
		prohibited_addresses.append(i2c_address)
		pm25_is_available = True
		header_string += ", pm10s, pm25s, pm100s, pm10e, pm25e, pm100e, 3um, 5um, 10um, 25um, 50um, 100um"
	except:
		warning("pm25 not found")
		pm25_is_available = False
	global ow_bus
	global ds18b20_is_available
	try:
		ow_bus = OneWireBus(board.D5)
		ds18b20_adafruit.setup(ow_bus, N)
		ds18b20_is_available = True
		header_string += ", ds18b20-C"
	except:
		warning("ds18b20 not found")
		ds18b20_is_available = False
	global sht31d_is_available
	try:
		i2c_address = sht31d_adafruit.setup(i2c, N)
		prohibited_addresses.append(i2c_address)
		header_string += ", sht31d-%RH, sht31d-C"
		sht31d_is_available = True
	except:
		warning("sht31d not found")
		sht31d_is_available = False
	info("prohibited i2c addresses: " + str(prohibited_addresses)) # disallow treating any devices already discovered as pct2075s
	try:
		addresses = pct2075_adafruit.setup(i2c, prohibited_addresses, N)
		#info("pct2075" + str(addresses))
		header_string += ", pct2075-C"
	except:
		error("pct2075 not found")
		return
	if use_pwm_status_leds:
		set_status_led_color([0.5, 0.5, 0.5])
	global airlift_is_available
	if should_use_airlift:
		if use_built_in_wifi:
			airlift_is_available = airlift.setup_wifi()
		else:
			airlift_is_available = airlift.setup_airlift("rooftop", spi, board.D13, board.D11, board.D12)
		header_string += ", RSSI-dB"
	else:
		airlift_is_available = False
	if 0:
		if airlift_is_available:
			airlift.update_time_from_server()
	#gnuplot> set key autotitle columnheader
	#gnuplot> set style data lines
	#gnuplot> plot for [i=1:14] "solar_water_heater.log" using 0:i
	print_header()
	global i
	i = 0
	loop()
	info("pct2075 no longer available; cannot continue")

def loop():
	global i
	while pct2075_adafruit.test_if_present():
		#info("")
		#info(str(i))
		neopixel_adafruit.set_color(255, 0, 0)
		if use_pwm_status_leds:
			set_status_led_color([1, 0, 0])
		string = ""
		if gps_is_available:
			string += gps_adafruit.measure_string()
		if bh1750_is_available:
			#info("bh1750")
			#gnuplot> plot for [i=3:3] "solar_water_heater.log" using 0:i
			string += bh1750_adafruit.measure_string()
		if ltr390_is_available:
			#info("ltr390")
			#gnuplot> plot for [i=4:7] "solar_water_heater.log" using 0:i
			string += ltr390_adafruit.measure_string()
		if vcnl4040_is_available:
			#info("vcnl4040")
			#gnuplot> plot for [i=8:9] "solar_water_heater.log" using 0:i
			string += vcnl4040_adafruit.measure_string()
		if as7341_is_available:
			#info("as7341")
			#gnuplot> plot for [i=8:15] "solar_water_heater.log" using 0:i
			string += as7341_adafruit.measure_string()
		if tsl2591_is_available:
			#info("tsl2591")
			string += tsl2591_adafruit.measure_string()
		if pm25_is_available:
			string += pm25_adafruit.measure_string()
		if ds18b20_is_available:
			#info("ds18b20")
			string += ds18b20_adafruit.measure_string()
		if anemometer_is_available:
			#info("anemometer")
			string += anemometer.measure_string()
		if sht31d_is_available:
			#info("sht31d")
			string += sht31d_adafruit.measure_string()
		#info("pct2075")
		#gnuplot> plot for [i=2:2] "solar_water_heater.log" using 0:i
		string += ", " + pct2075_adafruit.measure_string()
		if airlift_is_available:
			string += airlift.measure_string()
		print_compact(string)
		flush()
		neopixel_adafruit.set_color(0, 255, 0)
		if use_pwm_status_leds:
			set_status_led_color([0, 1, 0])
		i += 1
#		if wifi_mapping_mode:
#			if airlift_is_available:
#				if 2==i:
#					airlift.test_posting_geolocated_data("test")
		if 0==i%N:
			if wifi_mapping_mode:
				if airlift_is_available:
					try:
						airlift.post_geolocated_data("wifi-signal-strength", gps_adafruit.average_location(), airlift.get_values()[0])
					except:
						warning("couldn't post data for wifi signal strength")
					networks = airlift.scan_networks()
					airlift.show_networks(networks)
			if cat_on_a_hot_tin_roof_mode:
				if bh1750_is_available:
					bh1750_adafruit.show_average_values()
					if airlift_is_available:
						try:
							airlift.post_data("bh1750", bh1750_adafruit.get_average_values()[0])
						except:
							warning("couldn't post data for bh1750")
				if anemometer_is_available:
					anemometer.show_average_values()
					if airlift_is_available:
						try:
							airlift.post_data("anemometer", anemometer.get_average_values()[0])
						except:
							warning("couldn't post data for anemometer")
				if sht31d_is_available:
					sht31d_adafruit.show_average_values()
					if airlift_is_available:
						try:
							airlift.post_data("sht31d", sht31d_adafruit.get_average_values()[0])
						except:
							warning("couldn't post data for sht31d")
				if ds18b20_is_available:
					ds18b20_adafruit.show_average_values()
					if airlift_is_available:
						try:
							airlift.post_data("ds18b20", ds18b20_adafruit.get_average_values()[0])
						except:
							warning("couldn't post data for ds18b20")
			if ltr390_is_available:
				ltr390_adafruit.show_average_values()
			if vcnl4040_is_available:
				vcnl4040_adafruit.show_average_values()
			if as7341_is_available:
				as7341_adafruit.show_average_values()
#				if airlift_is_available:
#					try:
#						airlift.post_data("as7341", as7341_adafruit.get_average_values())
#					except:
#						warning("couldn't post data for as7341")
			if tsl2591_is_available:
				tsl2591_adafruit.show_average_values()
			if pm25_is_available:
				pm25_adafruit.show_average_values()
			#pct2075_adafruit.show_average_values()
			info("waiting...")
			time.sleep(delay_between_posting_and_next_acquisition)
		neopixel_adafruit.set_color(0, 0, 255)
		if use_pwm_status_leds:
			set_status_led_color([0, 0, 1])
		if airlift_is_available:
			if 0==i%86300:
				airlift.update_time_from_server()
		time.sleep(delay_between_acquisitions)

if __name__ == "__main__":
	#supervisor.disable_autoreload()
	atexit.register(generic.reset)
	try:
		main()
	except KeyboardInterrupt:
		info("caught ctrl-c")
		flush()
		atexit.unregister(generic.reset)
		sys.exit(0)
	except ReloadException:
		info("reload exception")
		flush()
		atexit.unregister(generic.reset)
		time.sleep(1)
		supervisor.reload()
	info("leaving program...")
	flush()
	generic.reset()

