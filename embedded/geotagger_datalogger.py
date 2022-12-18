# written 2021-09-10 by mza
# derived from solar_water_heater.py
# last updated 2022-12-16 by mza

# to install on a circuitpython device:
# rsync -av *.py /media/circuitpython/
# cp -a geotagger_datalogger.py /media/circuitpython/code.py
# cd ~/build/adafruit-circuitpython/bundle/lib
# rsync -r adafruit_ili9341.mpy adafruit_display_text adafruit_rfm9x.mpy adafruit_datetime.mpy adafruit_minimqtt simpleio.mpy adafruit_esp32spi adafruit_register adafruit_sdcard.mpy neopixel.mpy adafruit_pcf8523.mpy adafruit_gps.mpy adafruit_io adafruit_requests.mpy /media/circuitpython/lib/

BAUD_RATE = 4*57600
RADIO_FREQ_MHZ = 905.0 # 868-915 MHz (902-928 MHz is the allowed band in US/MEX/CAN)
TX_POWER_DBM = 5 # minimum 5; default 13; maximum 23

import generic
#generic.show_memory_situation() # 17k allocated
import sys
import time
import atexit
import supervisor
import board
import busio
import pwmio
import simpleio
import displayio
#generic.show_memory_situation() # 
import microsd_adafruit
import neopixel_adafruit
import airlift
import lora
from DebugInfoWarningError24 import debug, info, warning, error, debug2, debug3, set_verbosity, create_new_logfile_with_string_embedded, flush # uses 1k
#generic.show_memory_situation() # 

board_id = board.board_id
info("we are " + board_id)
if board_id=="adafruit_feather_esp32s2": # featherwing TFT and sparkfun GPS with RTK
	should_use_airlift = True
	should_use_lora = False
	my_wifi_name = "geotagger-datalogger"
	my_adafruit_io_prefix = "geotagger-datalogger"
	FEATHER_ESP32S2 = True
	should_use_sdcard = False
	should_use_RTC = False
	should_use_display = True
	should_use_gps = True
	N = 8
	gps_delay_in_ms = 1000
	delay_between_acquisitions = 2. * gps_delay_in_ms/1000.
	use_built_in_wifi = True
	import gps_adafruit
	import display_adafruit
else:
	error("what board am I?")
	sys.exit(2)

def print_compact(string):
	date = ""
	if ""==date:
		try:
			date = time.strftime("%Y-%m-%d+%X")
		except (KeyboardInterrupt, ReloadException):
			raise
		except:
			pass
	if ""==date and RTC_is_available:
		try:
			date = pcf8523_adafruit.get_timestring1()
		except (KeyboardInterrupt, ReloadException):
			raise
		except:
			pass
	if ""==date and gps_is_available:
		try:
			date = gps_adafruit.get_time()
		except (KeyboardInterrupt, ReloadException):
			raise
		except:
			pass
	info("%s%s" % (date, string))

def print_header():
	info("" + header_string)

def main():
	global header_string
	header_string = "date/time"
	if FEATHER_ESP32S2: # for feather esp32-s2 to turn on power to i2c bus:
		simpleio.DigitalOut(board.D7, value=0)
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
	if should_use_display:
		displayio.release_displays()
	global spi
	spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
	global uart
	uart = busio.UART(board.TX, board.RX, baudrate=9600, timeout=10)
	global RTC_is_available
	if should_use_RTC:
		try:
			i2c_address = pcf8523_adafruit.setup(i2c)
			RTC_is_available = True
		except (KeyboardInterrupt, ReloadException):
			raise
		except:
			RTC_is_available = False
	else:
		RTC_is_available = False
	global display_is_available
	if should_use_display:
		display_is_available = display_adafruit.setup_ili9341(spi, board.D9, board.D10)
	global sdcard_is_available
	global mydir
	mydir = "/logs"
	if should_use_sdcard:
		sdcard_is_available = microsd_adafruit.setup_sdcard_for_logging_data(spi, board.D10, mydir) # D10 = adalogger featherwing
	else:
		sdcard_is_available = False
	if not sdcard_is_available:
		mydir = "/"
#	if RTC_is_available:
#		create_new_logfile_with_string_embedded(mydir, "geotagger_datalogger", pcf8523_adafruit.get_timestring2())
#	else:
#		create_new_logfile_with_string_embedded(mydir, "geotagger_datalogger")
	global gps_is_available
	gps_is_available = False
	if should_use_gps:
		if 0:
			gps_adafruit.setup_uart(uart, N, gps_delay_in_ms)
		else:
			gps_adafruit.setup_i2c(i2c, N, gps_delay_in_ms)
		gps_is_available = True
		header_string += gps_adafruit.header_string()
	global neopixel_is_available
	try:
		neopixel_is_available = neopixel_adafruit.setup_neopixel()
	except (KeyboardInterrupt, ReloadException):
		raise
	except:
		warning("error setting up neopixel")
	global airlift_is_available
	if should_use_airlift:
		if use_built_in_wifi:
			airlift_is_available = airlift.setup_wifi(my_wifi_name)
		else:
			airlift_is_available = airlift.setup_airlift(my_wifi_name, spi, board.D13, board.D11, board.D12)
		header_string += ", RSSI-dB"
	else:
		airlift_is_available = False
	if 0:
		if airlift_is_available:
			airlift.update_time_from_server()
	generic.collect_garbage()
	#generic.show_memory_situation() #
	global lora_is_available
	lora_is_available = False
	if should_use_lora:
		import digitalio
		CS = digitalio.DigitalInOut(board.D5)
		RESET = digitalio.DigitalInOut(board.D6)
		lora.setup(spi, CS, RESET, RADIO_FREQ_MHZ, BAUD_RATE, TX_POWER_DBM, airlift_is_available, RTC_is_available, node_type, my_adafruit_io_prefix, nodeid)
		lora_is_available = True
	if airlift_is_available:
#		airlift.setup_feed(my_adafruit_io_prefix + "-wifi-rssi")
#		time.sleep(1)
		if lora_is_available:
			airlift.setup_feed(my_adafruit_io_prefix + "-lora-rssi")
			time.sleep(1)
	generic.collect_garbage()
	#generic.show_memory_situation() #
	print_header()
	global i
	i = 0
	loop()

def loop():
	global i
	while True:
		#info("")
		#info(str(i))
		neopixel_adafruit.set_color(255, 0, 0)
		string = ""
		if gps_is_available:
			string += gps_adafruit.measure_string()
		if airlift_is_available:
			string += airlift.measure_string()
		if lora_is_available:
			string += lora.measure_string()
		print_compact(string)
		#flush()
		neopixel_adafruit.set_color(0, 255, 0)
		i += 1
		if 0==i%N:
			if airlift_is_available:
				try:
					airlift.post_geolocated_data(my_adafruit_io_prefix + "-wifi-rssi", gps_adafruit.average_location(), airlift.get_average_values()[0])
				except (KeyboardInterrupt, ReloadException):
					raise
				except:
					warning("couldn't post geotagged wifi rssi")
					try:
						airlift.post_data(my_adafruit_io_prefix + "-wifi-rssi", airlift.get_average_values()[0])
					except (KeyboardInterrupt, ReloadException):
						raise
					except:
						warning("couldn't post data for wifi rssi")
				networks = airlift.scan_networks()
				airlift.show_networks(networks)
			if airlift_is_available and lora_is_available:
				try:
					airlift.post_geolocated_data(my_adafruit_io_prefix + "-lora-rssi", gps_adafruit.average_location(), lora.get_average_values()[0])
				except (KeyboardInterrupt, ReloadException):
					raise
				except:
					warning("couldn't post geotagged lora rssi")
					try:
						airlift.post_data(my_adafruit_io_prefix + "-lora-rssi", lora.get_average_values()[0])
					except (KeyboardInterrupt, ReloadException):
						raise
					except:
						warning("couldn't post data for lora rssi")
		neopixel_adafruit.set_color(0, 0, 255)
		if airlift_is_available:
			if 0==i%86300:
				airlift.update_time_from_server()
		generic.collect_garbage()
		#generic.show_memory_situation() # 
		time.sleep(delay_between_acquisitions)

if __name__ == "__main__":
	#supervisor.disable_autoreload()
	atexit.register(generic.reset)
	try:
		#generic.show_memory_situation() # 
		main()
	except KeyboardInterrupt:
		info("caught ctrl-c")
		flush()
		atexit.unregister(generic.reset)
		sys.exit(0)
	except MemoryError:
		#generic.show_memory_situation()
		raise
	except ReloadException:
		info("reload exception")
		flush()
		atexit.unregister(generic.reset)
		time.sleep(1)
		supervisor.reload()
	info("leaving program...")
	flush()
	generic.reset()

