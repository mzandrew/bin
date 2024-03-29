# written 2022-07 by mza
# last updated 2023-04-16 by mza

# rsync -a *.py /media/mza/LORASEND/; rsync -a *.py /media/mza/LORARECEIVE/
# cd lib
# rsync -r adafruit_seesaw adafruit_ina260.mpy adafruit_onewire adafruit_esp32spi adafruit_bus_device adafruit_display_text simpleio.mpy adafruit_gps.mpy neopixel.mpy adafruit_sdcard.mpy adafruit_datetime.mpy adafruit_register adafruit_rfm9x.mpy adafruit_as7341.mpy adafruit_bme680.mpy adafruit_io adafruit_minimqtt adafruit_requests.mpy adafruit_pcf8523.mpy adafruit_dotstar.mpy /media/mza/LORARECEIVE/lib/
# rsync -r adafruit_ina260.mpy adafruit_onewire adafruit_esp32spi adafruit_bus_device adafruit_display_text simpleio.mpy adafruit_gps.mpy neopixel.mpy adafruit_sdcard.mpy adafruit_datetime.mpy adafruit_register adafruit_rfm9x.mpy adafruit_as7341.mpy adafruit_bme680.mpy adafruit_io adafruit_minimqtt adafruit_requests.mpy adafruit_pcf8523.mpy adafruit_dotstar.mpy /media/mza/LORASEND/lib/
# cp -a lora_transceiver_basic_test.py /media/mza/LORASEND/code.py; cp -a lora_transceiver_basic_test.py /media/mza/LORARECEIVE/code.py
# sync

target_period = 514
N = 32
ina260_N = 4
delay_between_acquisitions = 16
time_to_wait_for_each_packet = 1.0
BAUD_RATE = 4*57600
RADIO_FREQ_MHZ = 905.0 # 868-915 MHz (902-928 MHz is the allowed band in US/MEX/CAN)
current_tx_power_dbm = 20 # minimum 5; default 13; maximum 20
delay = 2.0

# failure rate for 915 MHz, 4*57600, timeout=0.5 TX_POWER=20 is 2844/14262

# started 400 mAh battery drain at 7:13am; stopped at 3pm; 467 minutes (7.78 hours) -> 51 mA; with a Adalogger_FeatherWing and a rfm95w and an unexpectedmaker_feathers2 and a bme680 and an as7341

import time
import board
import busio
import storage
import simpleio
import adafruit_rfm9x
import microsd_adafruit
import neopixel_adafruit
import ina260_adafruit
import generic
#import gc
#print(str(gc.mem_free()))
try:
	import lora
except (KeyboardInterrupt, ReloadException):
	raise
except MemoryError as error_message:
	print("MemoryError: " + str(error_message))
#print(str(gc.mem_free()))
from DebugInfoWarningError24 import debug, info, warning, error, debug2, debug3, set_verbosity, create_new_logfile_with_string, create_new_logfile_with_string_embedded

ina260_address = 0x40
dirname = "/logs"

def setup():
	generic.start_uptime()
	global node_type
	global label
	global my_adafruit_io_prefix
	global dotstar_is_available
	global neopixel_is_available
	global should_use_airlift
	info("we are " + board.board_id)
	generic.print_os_ver()
	dotstar_is_available = False
	neopixel_is_available = False
#	if 'unexpectedmaker_feathers2'==board.board_id: # for uf2 boot, click [RESET], then about a second later click [BOOT]
#		import feathers2
#		feathers2.enable_LDO2(True)
#		feathers2.led_set(False)
#		r = 25
#		g = 50
#		b = 100
#		global dotstar_brightness
#		dotstar_brightness = 0.05
#		import adafruit_dotstar
#		global dotstar
#		dotstar = adafruit_dotstar.DotStar(board.APA102_SCK, board.APA102_MOSI, 1, brightness=dotstar_brightness, auto_write=True)
#		dotstar[0] = (r, g, b, dotstar_brightness)
#		dotstar_is_available = True
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
	global my_lora_identifier
	my_lora_identifier = "lora? unknown"
	import digitalio
	CS = digitalio.DigitalInOut(board.D5)
	RESET = digitalio.DigitalInOut(board.D6)
	if "LORARECEIVE"==label:
		node_type = "uplink"
		should_use_bme680 = False
		should_use_as7341 = False
		should_use_RTC = True
		should_use_airlift = True # for uplink
		use_built_in_wifi = True
		my_wifi_name = "loratransponder"
		my_adafruit_io_prefix = "lora"
		should_use_ina260 = False
		nodeid = 1
		should_use_neopixel = False
		should_use_rotary_encoder = True
		should_use_sdcard = True
		my_lora_identifier = "lora1 transponder uplink esp32tft adalogger rotary"
	elif "LORASEND2"==label: # rp2040 feather
		node_type = "gathering"
		should_use_bme680 = False
		should_use_as7341 = True
		should_use_RTC = False
		should_use_airlift = False
		use_built_in_wifi = False
		should_use_ina260 = True
		nodeid = 2
		should_use_neopixel = True
		should_use_rotary_encoder = False
		should_use_sdcard = False
		my_lora_identifier = "lora2 rp2040 as7341 ina260 solar"
	elif "LORASEND3"==label: # feather_m0_rfm9x - m0 procesor needs loralight.py and even then it's difficult
		node_type = "gathering"
		should_use_bme680 = False
		should_use_as7341 = False
		should_use_RTC = False
		should_use_airlift = False
		use_built_in_wifi = False
		should_use_ina260 = False
		nodeid = 3
		should_use_neopixel = False
		should_use_rotary_encoder = False
		should_use_sdcard = False
		my_lora_identifier = "lora3 m0 can't circuitpython this much..."
	elif "LORASEND4"==label: # rp2040 rfm95x feather
		node_type = "gathering"
		should_use_bme680 = False
		should_use_as7341 = True
		should_use_RTC = False
		should_use_airlift = False
		use_built_in_wifi = False
		should_use_ina260 = True
		nodeid = 2
		should_use_neopixel = True
		should_use_rotary_encoder = False
		should_use_sdcard = False
		my_lora_identifier = "lora4 rp2040 rfm95x as7341 ina260 solar"
		CS = digitalio.DigitalInOut(board.RFM_CS)
		RESET = digitalio.DigitalInOut(board.RFM_RST)
	else:
		warning("board filesystem has no label")
	if should_use_neopixel:
		try:
			neopixel_is_available = neopixel_adafruit.setup_neopixel()
		except:
			warning("can't set up neopixel")
	if neopixel_is_available:
		neopixel_adafruit.set_color(255, 255, 255)
	global LED
	LED = digitalio.DigitalInOut(board.D13)
	LED.direction = digitalio.Direction.OUTPUT
	global button
#	if 'unexpectedmaker_feathers2'==board.board_id:
#		button = digitalio.DigitalInOut(board.D0)
#	else:
	try:
		button = digitalio.DigitalInOut(board.BUTTON)
	except (KeyboardInterrupt, ReloadException):
		raise
	except:
		button = digitalio.DigitalInOut(board.D0)
	button.switch_to_input(pull=digitalio.Pull.UP)
	global encoder
	global last_position
	global encoder_switch
	global encoder_pixel
	global spi
	try:
		spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
	except (KeyboardInterrupt, ReloadException):
		raise
	except Exception as error_message:
		spi = board.SPI()
#	if 'unexpectedmaker_feathers2'==board.board_id:
#		CS = digitalio.DigitalInOut(board.D20)
#		RESET = digitalio.DigitalInOut(board.D21)
	if neopixel_is_available:
		neopixel_adafruit.set_color(255, 0, 255)
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
	global rotary_encoder_is_available
	rotary_encoder_is_available = False
	if should_use_rotary_encoder:
		from adafruit_seesaw import seesaw, rotaryio, neopixel
		# with help from https://github.com/adafruit/Adafruit_CircuitPython_seesaw/blob/main/examples/seesaw_rotary_neopixel.py
		myseesaw = seesaw.Seesaw(i2c, 0x36)
		seesaw_product = (myseesaw.get_version() >> 16) & 0xFFFF
		#print("Found product {}".format(seesaw_product))
		if seesaw_product != 4991:
			error("Wrong firmware loaded?  Expected 4991")
		encoder = rotaryio.IncrementalEncoder(myseesaw)
		last_position = -encoder.position
		#info("encoder position: " + str(last_position))
		myseesaw.pin_mode(24, myseesaw.INPUT_PULLUP)
		#encoder_switch = digitalio.DigitalIO(myseesaw, 24)
		encoder_pixel = neopixel.NeoPixel(myseesaw, 6, 1)
		encoder_pixel.brightness = 0.5
		encoder_pixel.fill((0,31,31))
		rotary_encoder_is_available = True
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
	global ina260_is_available
	ina260_is_available = False
	if should_use_ina260:
		try:
			ina260_adafruit.setup(i2c, ina260_N, ina260_address, 2)
			ina260_is_available = True
		except (KeyboardInterrupt, ReloadException):
			raise
		except:
			warning("can't talk to ina260 at address " + generic.hex(ina260_address))
			raise
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
	#info("RTC is available")
	global sdcard_is_available
	sdcard_is_available = False
	global dirname
	if should_use_sdcard:
		sdcard_is_available = microsd_adafruit.setup_sdcard_for_logging_data(spi, board.D10, dirname)
	else:
		dirname = ""
	if sdcard_is_available:
		global log_filename
		if RTC_is_available:
			log_filename = create_new_logfile_with_string_embedded(dirname, "lora_transceiver", pcf8523_adafruit.get_timestring2())
		else:
			log_filename = create_new_logfile_with_string_embedded(dirname, "lora_transceiver")
		microsd_adafruit.list_files(dirname)
	global airlift_is_available
	airlift_is_available = False
	if should_use_airlift:
		global airlift
		import airlift
		if use_built_in_wifi:
			airlift_is_available = airlift.setup_wifi(my_wifi_name)
		else:
			airlift_is_available = airlift.setup_airlift(my_wifi_name, spi, board.D13, board.D11, board.D12)
	if neopixel_is_available:
		neopixel_adafruit.set_color(255, 255, 0)
	try:
		lora.setup(spi, CS, RESET, RADIO_FREQ_MHZ, BAUD_RATE, current_tx_power_dbm, airlift_is_available, RTC_is_available, node_type, my_adafruit_io_prefix, nodeid)
	except (KeyboardInterrupt, ReloadException):
		raise
	except MemoryError as error_message:
		error(str(error_message))
	except Exception as error_message:
		error(str(error_message))
	if airlift_is_available:
		try:
			#airlift.setup_feed(my_adafruit_io_prefix + "-temp")
			#airlift.setup_feed(my_adafruit_io_prefix + "-hum")
			#airlift.setup_feed(my_adafruit_io_prefix + "-pres")
			#airlift.setup_feed(my_adafruit_io_prefix + "-clear")
			#airlift.setup_feed(my_adafruit_io_prefix + "-skipped")
			airlift.setup_feed(my_adafruit_io_prefix + "-garb-rssi")
			#airlift.setup_feed(my_adafruit_io_prefix + "-rssi")
			#airlift.setup_feed(my_adafruit_io_prefix + "-batt")
			#airlift.setup_feed(my_adafruit_io_prefix + "-current0")
			#airlift.setup_feed(my_adafruit_io_prefix + "-current1")
		except (KeyboardInterrupt, ReloadException):
			raise
		except Exception as error_message:
			error(str(error_message))
	if 0:
		if airlift_is_available:
			if RTC_is_available:
				airlift.update_time_from_server()
	global old_t
	if RTC_is_available:
		old_t = pcf8523_adafruit.get_struct_time()

def loop():
	global last_position
	global current_tx_power_dbm
	generic.get_uptime()
	global old_t
	global delay_between_acquisitions
	global target_period
	i = 0
	j = 0
	button_was_pressed = False
	if "uplink"==node_type:
		info("Waiting for packets...")
	first_time_through = True
	while True:
		if rotary_encoder_is_available:
			position = -encoder.position
			#info("encoder position: " + str(position))
			if position != last_position:
				#info("encoder position: " + str(position))
				current_tx_power_dbm += position - last_position
				current_tx_power_dbm = lora.change_tx_power_dbm(current_tx_power_dbm)
			last_position = position
			encoder_pixel.fill([int(20*(current_tx_power_dbm-3)/20) for a in range(3)])
		if neopixel_is_available:
			neopixel_adafruit.set_color(255, 0, 0)
		LED.value = False
		button_was_pressed = False
		if not button.value:
			button_was_pressed = True
		if first_time_through:
			first_time_through = False
			lora.send_a_message_with_timestamp(my_lora_identifier + " coming online")
			if ina260_is_available:
				ina260_adafruit.get_values(1)
			if "gathering"==node_type:
				lora.sleep()
		if dotstar_is_available:
			dotstar[0] = (0, 0, 255, dotstar_brightness)
		if "uplink"==node_type:
			packet = lora.receive(time_to_wait_for_each_packet)
			if ina260_is_available:
				ina260_adafruit.get_values(1)
			if packet is not None:
				LED.value = True
				lora.decode_a_message(packet)
		else:
			time.sleep(delay_between_acquisitions/2)
			if ina260_is_available:
				ina260_adafruit.get_values(0)
			time.sleep(delay_between_acquisitions/2)
			if ina260_is_available:
				ina260_adafruit.get_values(0)
		if button_was_pressed:
			button_was_pressed = False
			lora.send_a_message_with_timestamp("button was pressed " + str(i))
			if ina260_is_available:
				ina260_adafruit.get_values(1)
			if "gathering"==node_type:
				lora.sleep()
			i += 1
		if dotstar_is_available:
			dotstar[0] = (255, 0, 0, dotstar_brightness)
		if "gathering"==node_type:
			if neopixel_is_available:
				neopixel_adafruit.set_color(0, 0, 255)
			if bme680_is_available:
				bme680_adafruit.get_values()
			if ina260_is_available:
				ina260_adafruit.get_values(0)
			if as7341_is_available: 
				as7341_adafruit.get_values()
			if ina260_is_available:
				ina260_adafruit.get_values(0)
		if RTC_is_available:
			if airlift_is_available:
				t = pcf8523_adafruit.get_struct_time()
				if old_t.tm_mday != t.tm_mday:
					airlift.update_time_from_server()
				old_t = t
		if "uplink"==node_type:
			if RTC_is_available:
				t = pcf8523_adafruit.get_struct_time()
				debug2(str(t.tm_sec))
				if 0==t.tm_sec:
				#if 0==t.tm_sec or 30==t.tm_sec:
				#if 0==t.tm_sec or 30==t.tm_sec or 15==t.tm_sec or 45==t.tm_sec:
					lora.send_a_message_with_timestamp("the current time")
				if 0==t.tm_sec and 0==t.tm_min:
					microsd_adafruit.list_file(dirname, log_filename)
		j += 1
		if "gathering"==node_type and N<=j:
			if 0==j%N:
				if neopixel_is_available:
					neopixel_adafruit.set_color(0, 255, 0)
				if dotstar_is_available:
					dotstar[0] = (0, 255, 0, dotstar_brightness)
				if airlift_is_available:
					target_period = airlift.get_most_recent_data("target-period")
					info("target_period = " + str(target_period))
				delay_between_acquisitions = generic.adjust_delay_for_desired_loop_time(delay_between_acquisitions, N, target_period)
				if bme680_is_available:
					values = bme680_adafruit.get_average_values()
					string = str(values)
					lora.send_a_message_with_timestamp("bme680 " + string)
					ina260_adafruit.get_values(1)
					time.sleep(delay)
				lora.sleep()
			if 3==j%N:
				if neopixel_is_available:
					neopixel_adafruit.set_color(0, 255, 0)
				if dotstar_is_available:
					dotstar[0] = (0, 255, 0, dotstar_brightness)
				if ina260_is_available:
					ina260_adafruit.show_average_values(0)
					values = ina260_adafruit.get_average_values(0)
					string = str(values)
					lora.send_a_message_with_timestamp("ina260bin0 " + string)
					ina260_adafruit.get_values(1)
					time.sleep(delay)
			if 6==j%N:
				if neopixel_is_available:
					neopixel_adafruit.set_color(0, 255, 0)
				if dotstar_is_available:
					dotstar[0] = (0, 255, 0, dotstar_brightness)
				if ina260_is_available:
					ina260_adafruit.show_average_values(1)
					values = ina260_adafruit.get_average_values(1)
					string = str(values)
					lora.send_a_message_with_timestamp("ina260bin1 " + string)
					ina260_adafruit.get_values(1)
					time.sleep(delay)
				lora.sleep()
			if 9==j%N:
				if neopixel_is_available:
					neopixel_adafruit.set_color(0, 255, 0)
				if dotstar_is_available:
					dotstar[0] = (0, 255, 0, dotstar_brightness)
				if as7341_is_available:
					values = as7341_adafruit.get_average_values()
					string = str(values)
					lora.send_a_message_with_timestamp("as7341 " + string)
					ina260_adafruit.get_values(1)
					time.sleep(delay)
				lora.sleep()

if __name__ == "__main__":
	set_verbosity(4)
	setup()
	loop()

