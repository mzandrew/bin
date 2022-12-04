# written 2022-07 by mza
# last updated 2022-12-04 by mza

# rsync -a *.py /media/mza/LORASEND/; rsync -a *.py /media/mza/LORARECEIVE/
# cd lib
# rsync -r adafruit_onewire adafruit_esp32spi adafruit_bus_device adafruit_display_text simpleio.mpy adafruit_gps.mpy neopixel.mpy adafruit_sdcard.mpy adafruit_datetime.mpy adafruit_register adafruit_rfm9x.mpy adafruit_as7341.mpy adafruit_bme680.mpy adafruit_io adafruit_minimqtt adafruit_requests.mpy adafruit_pcf8523.mpy adafruit_dotstar.mpy /media/mza/LORARECEIVE/lib/
# rsync -r adafruit_onewire adafruit_esp32spi adafruit_bus_device adafruit_display_text simpleio.mpy adafruit_gps.mpy neopixel.mpy adafruit_sdcard.mpy adafruit_datetime.mpy adafruit_register adafruit_rfm9x.mpy adafruit_as7341.mpy adafruit_bme680.mpy adafruit_io adafruit_minimqtt adafruit_requests.mpy adafruit_pcf8523.mpy adafruit_dotstar.mpy /media/mza/LORASEND/lib/
# cp -a lora_transceiver_basic_test.py /media/mza/LORASEND/code.py; cp -a lora_transceiver_basic_test.py /media/mza/LORARECEIVE/code.py
# sync

TIMEOUT = 0.5
N = 64
BAUD_RATE = 4*57600
RADIO_FREQ_MHZ = 905.0 # 868-915 MHz (902-928 MHz is the allowed band in US/MEX/CAN)
TX_POWER_DBM = 5 # minimum 5; default 13; maximum 23

# failure rate for 915 MHz, 4*57600, timeout=0.5 TX_POWER=20 is 2844/14262

# started 400 mAh battery drain at 7:13am; stopped at 3pm; 467 minutes (7.78 hours) -> 51 mA; with a Adalogger_FeatherWing and a rfm95w and an unexpectedmaker_feathers2 and a bme680 and an as7341

import time
import board
import busio
import storage
import adafruit_rfm9x
#import gc
#print(str(gc.mem_free()))
try:
	import lora
except (KeyboardInterrupt, ReloadException):
	raise
except MemoryError as error_message:
	print("MemoryError: " + str(error_message))
#print(str(gc.mem_free()))
from DebugInfoWarningError24 import debug, info, warning, error, debug2, debug3, set_verbosity, create_new_logfile_with_string

def setup():
	global node_type
	global label
	global my_adafruit_io_prefix
	global dotstar_is_available
	info("we are " + board.board_id)
	dotstar_is_available = False
	if 'unexpectedmaker_feathers2'==board.board_id: # for uf2 boot, click [RESET], then about a second later click [BOOT]
		import feathers2
		feathers2.enable_LDO2(True)
		feathers2.led_set(False)
		r = 25
		g = 50
		b = 100
		global dotstar_brightness
		dotstar_brightness = 0.05
		import adafruit_dotstar
		global dotstar
		dotstar = adafruit_dotstar.DotStar(board.APA102_SCK, board.APA102_MOSI, 1, brightness=dotstar_brightness, auto_write=True)
		dotstar[0] = (r, g, b, dotstar_brightness)
		dotstar_is_available = True
	label = "unknown"
	try:
		m = storage.getmount("/")
		label = m.label
	except (KeyboardInterrupt, ReloadException):
		raise
	except Exception as error_message:
		error(str(error_message))
		pass
	info("our label is " + label)
	my_adafruit_io_prefix = ""
	node_type = None
	if "LORARECEIVE"==label:
		node_type = "uplink"
		should_use_bme680 = False
		should_use_as7341 = False
		should_use_RTC = False
		should_use_airlift = True # for uplink
		use_built_in_wifi = True
		my_wifi_name = "loratransponder"
		my_adafruit_io_prefix = "lora"
	elif "LORASEND"==label:
		node_type = "gathering"
		should_use_bme680 = True
		should_use_as7341 = True
		should_use_RTC = True
		should_use_airlift = False
		use_built_in_wifi = False
	elif "LORASEND2"==label: # feather_m0_rfm9x
		node_type = "gathering"
		should_use_bme680 = False
		should_use_as7341 = False
		should_use_RTC = False
		should_use_airlift = False
		use_built_in_wifi = False
	else:
		warning("board filesystem has no label")
	global LED
	import digitalio
	LED = digitalio.DigitalInOut(board.D13)
	LED.direction = digitalio.Direction.OUTPUT
	global button
	if 'unexpectedmaker_feathers2'==board.board_id:
		button = digitalio.DigitalInOut(board.D0)
	else:
		try:
			button = digitalio.DigitalInOut(board.BUTTON)
		except (KeyboardInterrupt, ReloadException):
			raise
		except:
			button = digitalio.DigitalInOut(board.D0)
	button.switch_to_input(pull=digitalio.Pull.UP)
	try:
		global i2c
		try:
			i2c = board.I2C()
		except (KeyboardInterrupt, ReloadException):
			raise
		except Exception as error_message:
			i2c = busio.I2C(board.SCL, board.SDA)
	except (KeyboardInterrupt, ReloadException):
		raise
	except Exception as error_message:
		error(str(error_message))
	global bme680_is_available
	bme680_is_available = False
	if should_use_bme680:
		global bme680_adafruit
		import bme680_adafruit
		try:
			bme680_adafruit.setup(i2c, N)
			bme680_is_available = True
		except (KeyboardInterrupt, ReloadException):
			raise
		except Exception as error_message:
			warning("bme680 not present")
			error(str(error_message))
	global as7341_is_available
	as7341_is_available = False
	if should_use_as7341:
		global as7341_adafruit
		import as7341_adafruit
		try:
			i2c_address = as7341_adafruit.setup(i2c, N)
			as7341_is_available = True
		except (KeyboardInterrupt, ReloadException):
			raise
		except Exception as error_message:
			warning("as7341 not present")
			error(str(error_message))
	global spi
	try:
		spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
	except (KeyboardInterrupt, ReloadException):
		raise
	except Exception as error_message:
		spi = board.SPI()
	if 'unexpectedmaker_feathers2'==board.board_id:
		CS = digitalio.DigitalInOut(board.D20)
		RESET = digitalio.DigitalInOut(board.D21)
	else:
		CS = digitalio.DigitalInOut(board.D5)
		RESET = digitalio.DigitalInOut(board.D6)
	global RTC_is_available
	RTC_is_available = False
	if should_use_RTC:
		global pcf8523_adafruit
		import pcf8523_adafruit
		try:
			i2c_address = pcf8523_adafruit.setup(i2c)
			RTC_is_available = True
		except (KeyboardInterrupt, ReloadException):
			raise
		except Exception as error_message:
			RTC_is_available = False
			error(str(error_message))
	global airlift_is_available
	airlift_is_available = False
	if should_use_airlift:
		global airlift
		import airlift
		if use_built_in_wifi:
			airlift_is_available = airlift.setup_wifi(my_wifi_name)
		else:
			airlift_is_available = airlift.setup_airlift(my_wifi_name, spi, board.D13, board.D11, board.D12)
	try:
		lora.setup(spi, CS, RESET, RADIO_FREQ_MHZ, BAUD_RATE, TX_POWER_DBM, airlift_is_available, RTC_is_available, node_type, my_adafruit_io_prefix)
	except (KeyboardInterrupt, ReloadException):
		raise
	except MemoryError as error_message:
		error(str(error_message))
	except Exception as error_message:
		error(str(error_message))
	if airlift_is_available:
		try:
			airlift.setup_feed(my_adafruit_io_prefix + "-temp")
			airlift.setup_feed(my_adafruit_io_prefix + "-hum")
			airlift.setup_feed(my_adafruit_io_prefix + "-pres")
			airlift.setup_feed(my_adafruit_io_prefix + "-clear")
			airlift.setup_feed(my_adafruit_io_prefix + "-skipped")
			airlift.setup_feed(my_adafruit_io_prefix + "-garb-rssi")
		except (KeyboardInterrupt, ReloadException):
			raise
		except Exception as error_message:
			error(str(error_message))
	if 1:
		if airlift_is_available:
			if RTC_is_available:
				airlift.update_time_from_server()

def loop():
	i = 0
	j = 0
	button_was_pressed = False
	info("Waiting for packets...")
	first_time_through = True
	while True:
		LED.value = False
		button_was_pressed = False
		if not button.value:
			button_was_pressed = True
		if first_time_through:
			first_time_through = False
			lora.send_a_message_with_timestamp("lora node coming online")
		if dotstar_is_available:
			dotstar[0] = (0, 0, 255, dotstar_brightness)
		packet = lora.receive(TIMEOUT)
		if packet is not None:
			LED.value = True
			lora.decode_a_message(packet)
		if button_was_pressed:
			button_was_pressed = False
			lora.send_a_message_with_timestamp("button was pressed " + str(i))
			i += 1
		if dotstar_is_available:
			dotstar[0] = (255, 0, 0, dotstar_brightness)
		if bme680_is_available:
			bme680_adafruit.get_values()
		if as7341_is_available: 
			as7341_adafruit.get_values()
		j += 1
		if 0==j%N:
			if dotstar_is_available:
				dotstar[0] = (0, 255, 0, dotstar_brightness)
			if bme680_is_available:
				values = bme680_adafruit.get_average_values()
				string = str(values)
				lora.send_a_message_with_timestamp("bme680 " + string)
			if as7341_is_available:
				values = as7341_adafruit.get_average_values()
				string = str(values)
				lora.send_a_message_with_timestamp("as7341 " + string)

if __name__ == "__main__":
	set_verbosity(4)
	setup()
	loop()

