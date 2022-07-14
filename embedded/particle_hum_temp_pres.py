#!/usr/bin/env python3

# written 2022-06-23 by mza
# based on indoor_hum_temp_pres.py
# last updated 2022-06-29 by mza

# to install on a circuitpython device:
# rsync -av *.py /media/circuitpython/
# cp -a particle-hum-temp-pres.py /media/circuitpython/code.py
# cd ~/build/adafruit-circuitpython/bundle/lib
# rsync -r adafruit_minimqtt adafruit_display_text adafruit_bme680.mpy simpleio.mpy adafruit_esp32spi adafruit_register adafruit_sdcard.mpy neopixel.mpy adafruit_onewire adafruit_gps.mpy adafruit_io adafruit_requests.mpy adafruit_lc709203f.mpy adafruit_bus_device /media/circuitpython/lib/

import sys
import time
import atexit
import board
import busio
import simpleio
import microsd_adafruit
import neopixel_adafruit
import bme680_adafruit
import airlift
import gps_adafruit
try:
	from DebugInfoWarningError24 import debug, info, warning, error, debug2, debug3, set_verbosity, create_new_logfile_with_string_embedded, flush
except (KeyboardInterrupt, ReloadException):
	raise
except:
	print("can't find DebugInfoWarningError24.py")
	sys.exit(0)
import generic
import display_adafruit

MIN_TEMP_TO_PLOT = 10.0
MAX_TEMP_TO_PLOT = 80.0
MIN_HUM_TO_PLOT = 40.0
MAX_HUM_TO_PLOT = 100.0
MIN_PRES_TO_PLOT = 0.997
MAX_PRES_TO_PLOT = 1.011
MIN_PARTICLE_COUNT_TO_PLOT = 0.0
MAX_PARTICLE_COUNT_TO_PLOT = 350.0

header_string = "date/time"
mydir = "/logs"
board_id = board.board_id
info("we are " + board_id)
if board_id=="pyportal_titano" or board_id=="pyportal":
	my_wifi_name = "part-hum-temp-pres-portal"
	my_adafruit_io_prefix = "congdon"
	FEATHER_ESP32S2 = False
	use_pwm_status_leds = False
	should_use_sdcard = True
	should_use_RTC = False
	should_use_gps = False
	N = 32
	desired_loop_time = 60.0
	delay_between_acquisitions = 1.5
	gps_delay_in_ms = 2000
	delay_between_posting_and_next_acquisition = 1.0
	should_use_airlift = False
	use_built_in_wifi = False
	should_use_display = True
	number_of_plots = 4
elif board_id=="adafruit_feather_esp32s2_tft" or board_id=="adafruit_feather_esp32s3_tft":
	my_wifi_name = "part-hum-temp-pres-feather"
	my_adafruit_io_prefix = "congdon"
	FEATHER_ESP32S2 = True
	use_pwm_status_leds = False
	should_use_sdcard = False
	should_use_RTC = False
	should_use_gps = False
	N = 32
	desired_loop_time = 60.0
	delay_between_acquisitions = 1.5
	gps_delay_in_ms = 2000
	delay_between_posting_and_next_acquisition = 1.0
	should_use_airlift = True
	use_built_in_wifi = True
	should_use_display = True
	number_of_plots = 1
elif board_id=="adafruit_qtpy_esp32s2" or board_id=="adafruit_qtpy_esp32s3":
	my_wifi_name = "part-hum-temp-pres-qtpy"
	#my_adafruit_io_prefix = "congdon"
	my_adafruit_io_prefix = "russell"
	FEATHER_ESP32S2 = False
	use_pwm_status_leds = False
	should_use_sdcard = False
	should_use_RTC = False
	should_use_gps = False
	N = 32
	desired_loop_time = 60.0
	delay_between_acquisitions = 1.5
	gps_delay_in_ms = 2000
	delay_between_posting_and_next_acquisition = 1.0
	#should_use_airlift = False
	should_use_airlift = True
	use_built_in_wifi = True
	should_use_display = False
	number_of_plots = 1
else:
	error("what kind of board am I?")

def print_header():
	info("" + header_string)

def print_compact(string):
	date = ""
	if ""==date:
		try:
			import time
			date = time.strftime("%Y-%m-%d+%X")
		except (KeyboardInterrupt, ReloadException):
			raise
		except:
			pass
	if ""==date and RTC_is_available:
		try:
			import pcf8523_adafruit
			date = pcf8523_adafruit.get_timestring1()
		except (KeyboardInterrupt, ReloadException):
			raise
		except:
			pass
	if ""==date and gps_is_available:
		try:
			import gps_adafruit
			date = gps_adafruit.get_time()
		except (KeyboardInterrupt, ReloadException):
			raise
		except:
			pass
	info("%s%s" % (date, string))

def main():
	generic.start_uptime()
	global header_string
	if use_pwm_status_leds:
		generic.setup_status_leds(red_pin=board.A2, green_pin=board.D9, blue_pin=board.A3)
		generic.set_status_led_color([1.0, 1.0, 1.0])
#	if FEATHER_ESP32S2: # for feather esp32-s2 to turn on power to i2c bus:
#		simpleio.DigitalOut(board.I2C_TFT_POWER, value=1)
	global i2c
	try:
		i2c = busio.I2C(board.SCL1, board.SDA1)
		string = "using I2C1 "
	except (KeyboardInterrupt, ReloadException):
		raise
	except:
		#i2c = busio.I2C(board.SCL, board.SDA)
		i2c = board.I2C()
		string = "using I2C0 "
	info(string)
	#i2c.try_lock()
	#i2c_list = i2c.scan()
	#i2c.unlock()
	#info(string + str(i2c_list))
	global pm25_is_available
	try:
		i2c_address = pm25_adafruit.setup(i2c, N)
		header_string += pm25_adafruit.header_string
		prohibited_addresses.append(i2c_address)
		pm25_is_available = True
	except (KeyboardInterrupt, ReloadException):
		raise
	except:
		error("particle count sensor not found")
		pm25_is_available = False
		#sys.exit(1)
	global spi
	try:
		spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO) # this line stops the builtin from working
		info("builtin SPI (2)")
	except (KeyboardInterrupt, ReloadException):
		raise
	except:
		try:
			spi = board.SPI
			info("builtin SPI (1)")
		except (KeyboardInterrupt, ReloadException):
			raise
		except:
			raise
	global display_is_available
	display_is_available = False
	if should_use_display:
		if board.DISPLAY:
			display_is_available = True
			display_adafruit.setup_builtin_display()
			board.DISPLAY.brightness = 0.75
			#display_adafruit.setup_pwm_backlight(board.TFT_BACKLIGHT, backlight_brightness=0.5)
			info("display is available (builtin)")
		elif display_adafruit.setup_st7789(spi, board.TFT_DC, board.TFT_CS, board.TFT_RESET):
#		if display_adafruit.setup_st7789(spi, board.TFT_DC, board.TFT_CS, board.TFT_RESET):
			display_adafruit.setup_pwm_backlight(board.TFT_BACKLIGHT, backlight_brightness=0.95)
			display_is_available = True
			info("display is available (external/spi)")
		else:
			warning("display is not available")
	if display_is_available:
		if 1<number_of_plots:
			display_adafruit.setup_for_n_m_plots(2, 2, [["temperature", "cold"], ["humidity", "under"], ["pressure", "under"], ["particle count", "0.3", "0.5", "1.0", "2.5", "5.0"]])
		else:
			display_adafruit.setup_for_n_m_plots(1, 1, [["stuff", "temp", "hum", "press", "1.0", "2.5"]])
			#display_adafruit.setup_for_n_m_plots(1, 1, [["stuff", "temp", "hum", "press", "0.3", "0.5", "1.0", "2.5", "5.0"]])
		#display_adafruit.setup_for_n_m_plots(1, 1, [["indoor", "temperature", "humidity", "pressure", "1p0"]])
		display_adafruit.refresh()
		#display_adafruit.test_st7789()
		#info("done with st7789 test")
	#global uart
	#uart = busio.UART(board.TX, board.RX, baudrate=9600, timeout=10)
	prohibited_addresses = []
	global RTC_is_available
	if should_use_RTC:
		try:
			i2c_address = pcf8523_adafruit.setup(i2c)
			prohibited_addresses.append(i2c_address)
			RTC_is_available = True
		except (KeyboardInterrupt, ReloadException):
			raise
		except:
			RTC_is_available = False
	else:
		RTC_is_available = False
	global sdcard_is_available
	global mydir
	if should_use_sdcard:
		sdcard_is_available = microsd_adafruit.setup_sdcard_for_logging_data(spi, board.SD_CS, mydir)
	else:
		sdcard_is_available = False
	if not sdcard_is_available:
		mydir = ""
	if RTC_is_available:
		create_new_logfile_with_string_embedded(mydir, my_wifi_name, pcf8523_adafruit.get_timestring2())
	else:
		create_new_logfile_with_string_embedded(mydir, my_wifi_name)
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
	global neopixel_is_available
	try:
		neopixel_is_available = neopixel_adafruit.setup_neopixel()
	except (KeyboardInterrupt, ReloadException):
		raise
	except:
		warning("error setting up neopixel")
	global bme680_is_available
	try:
		i2c_address = bme680_adafruit.setup(i2c, N)
		prohibited_addresses.append(i2c_address)
		header_string += bme680_adafruit.header_string
		bme680_is_available = True
	except (KeyboardInterrupt, ReloadException):
		raise
	except:
		error("bme680 not found")
		sys.exit(1)
		bme680_is_available = False
	#info("prohibited i2c addresses: " + str(prohibited_addresses)) # disallow treating any devices already discovered as pct2075s
	global battery_monitor_is_available
	try:
		battery_monitor_is_available = generic.setup_battery_monitor(i2c)
	except (KeyboardInterrupt, ReloadException):
		raise
	except:
		battery_monitor_is_available = False
		warning("battery monitor is not available")
	if use_pwm_status_leds:
		generic.set_status_led_color([0.5, 0.5, 0.5])
	global airlift_is_available
	if should_use_airlift:
		if use_built_in_wifi:
			airlift_is_available = airlift.setup_wifi(my_wifi_name)
		else:
			airlift_is_available = airlift.setup_airlift(my_wifi_name, spi, board.ESP_CS, board.ESP_BUSY, board.ESP_RESET)
		if airlift_is_available:
			header_string += ", RSSI-dB"
			if bme680_is_available:
				airlift.setup_feed(my_adafruit_io_prefix + "-temp")
				airlift.setup_feed(my_adafruit_io_prefix + "-hum")
				airlift.setup_feed(my_adafruit_io_prefix + "-pressure")
			#airlift.setup_feed("indoor-altitude")
			#airlift.setup_feed("indoor-gas")
			if pm25_is_available:
				airlift.setup_feed(my_adafruit_io_prefix + "-0p3")
				airlift.setup_feed(my_adafruit_io_prefix + "-0p5")
				airlift.setup_feed(my_adafruit_io_prefix + "-1p0")
				airlift.setup_feed(my_adafruit_io_prefix + "-2p5")
				airlift.setup_feed(my_adafruit_io_prefix + "-5p0")
	else:
		airlift_is_available = False
	if 0:
		if airlift_is_available:
			airlift.update_time_from_server()
	#gnuplot> set key autotitle columnheader
	#gnuplot> set style data lines
	#gnuplot> plot for [i=1:14] "solar_water_heater.log" using 0:i
	print_header()
	loop()
	info("bme680 no longer available; cannot continue")

def loop():
	if display_is_available:
		info("allocating memory...")
		if bme680_is_available:
			temperatures_to_plot = [ -40.0 for i in range(display_adafruit.plot_width) ]
			humidities_to_plot   = [ -40.0 for i in range(display_adafruit.plot_width) ]
			pressures_to_plot    = [ -40.0 for i in range(display_adafruit.plot_width) ]
		if pm25_is_available:
			particle_counts_to_plot = [ [ -40.0 for i in range(display_adafruit.plot_width) ] for j in range(5) ]
		info("finished allocating memory")
	generic.get_uptime()
	global delay_between_acquisitions
	i = 0
	while bme680_adafruit.test_if_present():
		neopixel_adafruit.set_color(255, 0, 0)
		if use_pwm_status_leds:
			generic.set_status_led_color([1, 0, 0])
		string = ""
		if gps_is_available:
			string += gps_adafruit.measure_string()
		if pm25_is_available:
			string += pm25_adafruit.measure_string()
		if bme680_is_available:
			#info("bme680")
			string += bme680_adafruit.measure_string()
		if airlift_is_available:
			string += airlift.measure_string()
		if battery_monitor_is_available:
			string += generic.get_battery_percentage()
		print_compact(string)
		flush()
		neopixel_adafruit.set_color(0, 255, 0)
		if use_pwm_status_leds:
			generic.set_status_led_color([0, 1, 0])
		i += 1
		if 0==i%N:
			if bme680_is_available:
				bme680_adafruit.show_average_values()
				if display_is_available:
					temperatures_to_plot.append((bme680_adafruit.get_average_values()[0] - MIN_TEMP_TO_PLOT) / (MAX_TEMP_TO_PLOT-MIN_TEMP_TO_PLOT))
					temperatures_to_plot.pop(0)
					humidities_to_plot.append(  (bme680_adafruit.get_average_values()[1] - MIN_HUM_TO_PLOT)  / (MAX_HUM_TO_PLOT-MIN_HUM_TO_PLOT))
					humidities_to_plot.pop(0)
					pressures_to_plot.append(   (bme680_adafruit.get_average_values()[2] - MIN_PRES_TO_PLOT) / (MAX_PRES_TO_PLOT-MIN_PRES_TO_PLOT))
					pressures_to_plot.pop(0)
				#print(str(temperatures_to_plot))
				#print(str(humidities_to_plot))
				#print(str(pressures_to_plot))
				if airlift_is_available:
					try:
						airlift.post_data(my_adafruit_io_prefix + "-temp",     bme680_adafruit.get_average_values()[0])
						airlift.post_data(my_adafruit_io_prefix + "-hum",      bme680_adafruit.get_average_values()[1])
						airlift.post_data(my_adafruit_io_prefix + "-pressure", bme680_adafruit.get_average_values()[2])
						#airlift.post_data("indoor-altitude", bme680_adafruit.get_average_values()[3])
						#airlift.post_data("indoor-gas", bme680_adafruit.get_average_values()[4])
					except (KeyboardInterrupt, ReloadException):
						raise
					except:
						warning("couldn't post data for bme680")
			if pm25_is_available:
				pm25_adafruit.show_average_values()
				if display_is_available:
					for j in range(5):
						particle_counts_to_plot[j].append((pm25_adafruit.get_average_values()[6+j] - MIN_PARTICLE_COUNT_TO_PLOT) / (MAX_PARTICLE_COUNT_TO_PLOT-MIN_PARTICLE_COUNT_TO_PLOT))
						particle_counts_to_plot[j].pop(0)
				if airlift_is_available:
					try:
						airlift.post_data(my_adafruit_io_prefix + "-0p3", pm25_adafruit.get_average_values()[6])
						airlift.post_data(my_adafruit_io_prefix + "-0p5", pm25_adafruit.get_average_values()[7])
						airlift.post_data(my_adafruit_io_prefix + "-1p0", pm25_adafruit.get_average_values()[8])
						airlift.post_data(my_adafruit_io_prefix + "-2p5", pm25_adafruit.get_average_values()[9])
						airlift.post_data(my_adafruit_io_prefix + "-5p0", pm25_adafruit.get_average_values()[10])
					except (KeyboardInterrupt, ReloadException):
						raise
					except:
						warning("couldn't post data for particle count sensor")
			if display_is_available:
				if 1<number_of_plots:
					if bme680_is_available:
						display_adafruit.update_plot(0, [temperatures_to_plot])
						display_adafruit.update_plot(1, [humidities_to_plot])
						display_adafruit.update_plot(2, [pressures_to_plot])
					if pm25_is_available:
						display_adafruit.update_plot(3, [particle_counts_to_plot[2], particle_counts_to_plot[3]])
				else:
					if bme680_is_available and pm25_is_available:
						display_adafruit.update_plot(0, [temperatures_to_plot, humidities_to_plot, pressures_to_plot, particle_counts_to_plot[2], particle_counts_to_plot[3]])
					elif bme680_is_available:
						display_adafruit.update_plot(0, [temperatures_to_plot, humidities_to_plot, pressures_to_plot])
					elif pm25_is_available:
						display_adafruit.update_plot(0, [particle_counts_to_plot[2], particle_counts_to_plot[3]])
				display_adafruit.refresh()
			info("waiting...")
			time.sleep(delay_between_posting_and_next_acquisition)
			delay_between_acquisitions = generic.adjust_delay_for_desired_loop_time(delay_between_acquisitions, N, desired_loop_time)
		neopixel_adafruit.set_color(0, 0, 255)
		if use_pwm_status_leds:
			generic.set_status_led_color([0, 0, 1])
		if airlift_is_available:
			if 0==i%86300:
				airlift.update_time_from_server()
		time.sleep(delay_between_acquisitions)

if __name__ == "__main__":
	atexit.register(generic.reset)
	try:
		main()
	except KeyboardInterrupt:
		generic.keyboard_interrupt_exception_handler()
	except ReloadException:
		generic.reload_exception_handler()
	info("leaving program...")
	flush()
	generic.reset()

