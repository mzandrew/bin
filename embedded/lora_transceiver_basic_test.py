# written 2022-07 by mza
# basic bits taken from adafruit's rfm9x_simpletest.py by Tony DiCola and rfm9x_node1_ack.py by Jerry Needell
# more help from https://learn.adafruit.com/multi-device-lora-temperature-network/using-with-adafruitio
# last updated 2022-12-03 by mza

# rsync -a *.py /media/mza/LORASEND/; rsync -a *.py /media/mza/LORARECEIVE/
# cd lib
# rsync -r adafruit_onewire adafruit_esp32spi adafruit_bus_device adafruit_display_text simpleio.mpy adafruit_gps.mpy neopixel.mpy adafruit_sdcard.mpy adafruit_datetime.mpy adafruit_register adafruit_rfm9x.mpy adafruit_as7341.mpy adafruit_bme680.mpy adafruit_io adafruit_minimqtt adafruit_requests.mpy adafruit_pcf8523.mpy adafruit_dotstar.mpy /media/mza/LORARECEIVE/lib/
# rsync -r adafruit_onewire adafruit_esp32spi adafruit_bus_device adafruit_display_text simpleio.mpy adafruit_gps.mpy neopixel.mpy adafruit_sdcard.mpy adafruit_datetime.mpy adafruit_register adafruit_rfm9x.mpy adafruit_as7341.mpy adafruit_bme680.mpy adafruit_io adafruit_minimqtt adafruit_requests.mpy adafruit_pcf8523.mpy adafruit_dotstar.mpy /media/mza/LORASEND/lib/
# cp -a lora_transceiver_basic_test.py /media/mza/LORASEND/code.py; cp -a lora_transceiver_basic_test.py /media/mza/LORARECEIVE/code.py
# sync

BAUD_RATE = 4*57600
TIMEOUT = 0.5
PREFIX = "SCOOPY"
SUFFIX = "BOOPS"
N = 64
USE_ACKNOWLEDGE = False
RADIO_FREQ_MHZ = 905.0 # 868-915 MHz
TX_POWER_DBM = 5 # minimum 5; default 13; maximum 23

# failure rate for 915 MHz, 4*57600, timeout=0.5 TX_POWER=20 is 2844/14262

# you can put uf2+circuitpython on a radiofruit feather m0 rfm95, but then there's only 45k free for code and libraries:
# https://learn.adafruit.com/installing-circuitpython-on-samd21-boards/installing-the-uf2-bootloader
# https://github.com/adafruit/uf2-samdx1/releases
# https://circuitpython.org/board/feather_m0_rfm9x/
# https://learn.adafruit.com/adafruit-feather-m0-radio-with-lora-radio-module/circuitpython-for-rfm9x-lora
# https://learn.adafruit.com/welcome-to-circuitpython/non-uf2-installation
# installed bossa from package manager:  device is not supported
# installed bossa from source (need wxgtk3.0-gtk3-dev):  device not supported
# it has to be in bootloader mode
# use offset=0x2000
# but there's no more space free on the drive, so it's flipping useless

# RX_POWER
# [-49,-48] dBm when the tx and rx are in the same spot
# [-62,-61] dBm when they are separated by 1 room (on top of fridge)
# [-95,-82] dBm when the tx is outdoors (in car)
# [-85,-82] dBm when the tx is on Jen's deck
# [-113,-99] dBm when the tx is in Jen's front yard

import time
import re
import board
import busio
import digitalio
import storage
import adafruit_rfm9x
import adafruit_dotstar
import bme680_adafruit
import as7341_adafruit
import pcf8523_adafruit
import airlift
from DebugInfoWarningError24 import debug, info, warning, error, debug2, debug3, set_verbosity, create_new_logfile_with_string

def setup():
	set_verbosity(4)
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
		global dotstar
		dotstar = adafruit_dotstar.DotStar(board.APA102_SCK, board.APA102_MOSI, 1, brightness=dotstar_brightness, auto_write=True)
		dotstar[0] = (r, g, b, dotstar_brightness)
		dotstar_is_available = True
	#else:
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
	if "LORARECEIVE"==label:
		should_use_bme680 = False
		should_use_as7341 = False
		should_use_RTC = False
		should_use_airlift = True # for uplink
		use_built_in_wifi = True
		my_wifi_name = "loratransponder"
		my_adafruit_io_prefix = "lora"
	elif "LORASEND"==label:
		should_use_bme680 = True
		should_use_as7341 = True
		should_use_RTC = True
		should_use_airlift = False
		use_built_in_wifi = False
	elif "LORASEND2"==label: # feather_m0_rfm9x
		should_use_bme680 = False
		should_use_as7341 = False
		should_use_RTC = False
		should_use_airlift = False
		use_built_in_wifi = False
	else:
		warning("board filesystem has no label")
	global LED
	LED = digitalio.DigitalInOut(board.D13)
	LED.direction = digitalio.Direction.OUTPUT
	global button
	if 'unexpectedmaker_feathers2'==board.board_id:
		button = digitalio.DigitalInOut(board.D0)
		button.switch_to_input(pull=digitalio.Pull.UP)
	else:
		button = digitalio.DigitalInOut(board.BUTTON)
		button.switch_to_input(pull=digitalio.Pull.UP)
	global spi
	try:
		spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
	except (KeyboardInterrupt, ReloadException):
		raise
	except Exception as error_message:
		spi = board.SPI()
	global i2c
	try:
		i2c = board.I2C()
	except (KeyboardInterrupt, ReloadException):
		raise
	except Exception as error_message:
		i2c = busio.I2C(board.SCL, board.SDA)
	global bme680_is_available
	bme680_is_available = False
	if should_use_bme680:
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
		try:
			i2c_address = as7341_adafruit.setup(i2c, N)
			#prohibited_addresses.append(i2c_address)
			as7341_is_available = True
		except (KeyboardInterrupt, ReloadException):
			raise
		except Exception as error_message:
			warning("as7341 not present")
			error(str(error_message))
	if 'unexpectedmaker_feathers2'==board.board_id:
		CS = digitalio.DigitalInOut(board.D20)
		RESET = digitalio.DigitalInOut(board.D21)
	else:
		CS = digitalio.DigitalInOut(board.D5)
		RESET = digitalio.DigitalInOut(board.D6)
	global rfm9x
	rfm9x = adafruit_rfm9x.RFM9x(spi=spi, cs=CS, reset=RESET, frequency=RADIO_FREQ_MHZ, baudrate=BAUD_RATE)
	#rfm9x = adafruit_rfm9x.RFM9x(spi=spi, cs=CS, reset=RESET, frequency=RADIO_FREQ_MHZ)
	rfm9x.tx_power = TX_POWER_DBM
	#rfm9x.signal_bandwidth = 62500
	#rfm9x.coding_rate = 6
	#rfm9x.spreading_factor = 8
	#rfm9x.enable_crc = True
	if USE_ACKNOWLEDGE:
		rfm9x.ack_delay = 0.1
		if "LORASEND"==label:
			rfm9x.node = 2
			rfm9x.destination = 1
		else:
			time.sleep(2)
			rfm9x.node = 1
			rfm9x.destination = 2
		info("we are node " + str(rfm9x.node))
	global RTC_is_available
	RTC_is_available = False
	if should_use_RTC:
		try:
			i2c_address = pcf8523_adafruit.setup(i2c)
			#prohibited_addresses.append(i2c_address)
			RTC_is_available = True
		except (KeyboardInterrupt, ReloadException):
			raise
		except Exception as error_message:
			RTC_is_available = False
			error(str(error_message))
	global airlift_is_available
	airlift_is_available = False
	if should_use_airlift:
		if use_built_in_wifi:
			airlift_is_available = airlift.setup_wifi(my_wifi_name)
		else:
			airlift_is_available = airlift.setup_airlift(my_wifi_name, spi, board.D13, board.D11, board.D12)
		#header_string += ", RSSI-dB"
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

def send_a_message(message):
	global message_id
	try:
		message_id += 1
	except (KeyboardInterrupt, ReloadException):
		raise
	except Exception as error_message:
		message_id = 1
	message_id_string = "[" + str(message_id) + "] "
	message_with_prefix_and_suffix = PREFIX + message_id_string + message + SUFFIX
	if 252<len(message_with_prefix_and_suffix):
		warning("should truncate or parcel message because it is too long")
	info("sending: " + message_id_string + message)
	if USE_ACKNOWLEDGE:
		if rfm9x.send_with_ack(bytes(message_with_prefix_and_suffix, "utf-8")):
			info("ack received")
		else:
			info("no ack received")
	else:
		rfm9x.send(bytes(message_with_prefix_and_suffix, "utf-8"))

def send_a_message_with_timestamp(message):
	if RTC_is_available:
		timestring = pcf8523_adafruit.get_timestring3()
		message = timestring + " " + message
	send_a_message(message)

def decode_a_message(packet):
	global previously_received_message_id
	try:
		previously_received_message_id
	except (KeyboardInterrupt, ReloadException):
		raise
	except Exception as error_message:
		previously_received_message_id = 0
	global total_skipped_messages
	try:
		total_skipped_messages
	except (KeyboardInterrupt, ReloadException):
		raise
	except Exception as error_message:
		total_skipped_messages = 0
	this_message_id = 0
	try:
		rssi = rfm9x.last_rssi
	except (KeyboardInterrupt, ReloadException):
		raise
	except Exception as error_message:
		rssi = 0
	#info("Received signal strength: {0} dBm".format(rssi))
	try:
		packet_text = str(packet, "ascii")
		match = re.search("^" + PREFIX + "\[([0-9]+)\](.*)" + SUFFIX + "$", packet_text)
		if match:
			this_message_id = match.group(1)
			message = match.group(2)
			this_message_id = int(this_message_id)
			#info("Received (raw bytes): {0}".format(packet))
			skipped_messages = this_message_id - previously_received_message_id - 1
			#debug("previously_received_message_id: " + str(previously_received_message_id))
			#debug("this_message_id: " + str(this_message_id))
			#debug("skipped_messages: " + str(skipped_messages))
			if 0<skipped_messages:
				total_skipped_messages += skipped_messages
				#warning("skipped " + str(skipped_messages) + " message(s)")
				if this_message_id:
					percentage = int(1000.0 * total_skipped_messages / this_message_id)/10.0
				else:
					percentage = "?"
				warning("skipped " + str(skipped_messages) + " message(s); total skipped: " + str(total_skipped_messages) + "/" + str(this_message_id) + " = " + str(percentage) + "%")
				if airlift_is_available:
					try:
						airlift.post_data(my_adafruit_io_prefix + "-skipped", skipped_messages)
					except (KeyboardInterrupt, ReloadException):
						raise
					except Exception as error_message:
						warning("unable to post skipped data")
						airlift.show_network_status()
						error(str(error_message))
			info("received: [" + str(this_message_id) + "]" + message + " RSSI=" + str(rssi) + "dBm")
			previously_received_message_id = this_message_id
			if "LORARECEIVE"==label:
				parse(message)
		else:
			debug("received: " + packet_text + " RSSI=" + str(rssi) + "dBm")
	except (KeyboardInterrupt, ReloadException):
		raise
	except Exception as error_message:
		warning("message garbled RSSI=" + str(rssi) + "dBm")
		error(str(error_message))
		if airlift_is_available:
			try:
				airlift.post_data(my_adafruit_io_prefix + "-garb-rssi", rssi)
			except (KeyboardInterrupt, ReloadException):
				raise
			except Exception as error_message:
				warning("unable to post garb_rssi data")
				airlift.show_network_status()
				error(str(error_message))
		#info("total skipped messages: " + str(total_skipped_messages))
	return this_message_id

def parse_bme680(message):
	match = re.search("bme680 \[([0-9.]+), ([0-9.]+), ([0-9.]+),", message)
	if match:
		temp = float(match.group(1))
		hum = float(match.group(2))
		pres = float(match.group(3))
		info("temperature: " + str(temp) + " C")
		info("humidity: " + str(hum) + " %RH")
		info("presure: " + str(pres) + " ATM")
		if airlift_is_available:
			try:
				airlift.post_data(my_adafruit_io_prefix + "-temp", temp)
				airlift.post_data(my_adafruit_io_prefix + "-hum", hum)
				airlift.post_data(my_adafruit_io_prefix + "-pres", pres)
			except (KeyboardInterrupt, ReloadException):
				raise
			except Exception as error_message:
				warning("couldn't post data for remote bme680")
				airlift.show_network_status()
				error(str(error_message))
		return True
	else:
		return False

def parse_as7341(message):
	match = re.search("as7341 \[([0-9.]+), ([0-9.]+), ([0-9.]+), ([0-9.]+), ([0-9.]+), ([0-9.]+), ([0-9.]+), ([0-9.]+), ([0-9.]+), ([0-9.]+)\]", message)
	if match:
		nm415 = float(match.group(1))
		nm445 = float(match.group(2))
		nm480 = float(match.group(3))
		nm515 = float(match.group(4))
		nm555 = float(match.group(5))
		nm590 = float(match.group(6))
		nm630 = float(match.group(7))
		nm680 = float(match.group(8))
		clear = float(match.group(9))
		nir   = float(match.group(10))
		info("nm415: " + str(nm415))
		info("nm445: " + str(nm445))
		info("nm480: " + str(nm480))
		info("nm515: " + str(nm515))
		info("nm555: " + str(nm555))
		info("nm590: " + str(nm590))
		info("nm630: " + str(nm630))
		info("nm680: " + str(nm680))
		info("clear: " + str(clear))
		info("nir: " + str(nir))
		if airlift_is_available:
			try:
				pass
				airlift.post_data(my_adafruit_io_prefix + "-clear", clear)
			except (KeyboardInterrupt, ReloadException):
				raise
			except Exception as error_message:
				warning("couldn't post data for remote as7341")
				airlift.show_network_status()
				error(str(error_message))
		return True
	else:
		return False

def parse(message):
	info(message)
	if parse_bme680(message):
		return True
	if parse_as7341(message):
		return True
	return False

setup()
i = 0
j = 0
button_was_pressed = False
info("Waiting for packets...")
first_time_through = True
while True:
	#if airlift_is_available:
		#airlift.get_values()
	LED.value = False
	button_was_pressed = False
	if not button.value:
		button_was_pressed = True
	if first_time_through:
		first_time_through = False
		if "LORASEND"==label:
			time.sleep(10)
		send_a_message_with_timestamp("lora node coming online")
	if dotstar_is_available:
		dotstar[0] = (0, 0, 255, dotstar_brightness)
	if USE_ACKNOWLEDGE:
		packet = rfm9x.receive(with_ack=True, timeout=TIMEOUT)
	else:
		packet = rfm9x.receive(timeout=TIMEOUT)
	if packet is not None:
		#info(str(len(packet)))
		LED.value = True
		#airlift.show_average_values()
		decode_a_message(packet)
	if button_was_pressed:
		button_was_pressed = False
		send_a_message_with_timestamp("button was pressed " + str(i))
		i += 1
	if dotstar_is_available:
		dotstar[0] = (255, 0, 0, dotstar_brightness)
	if bme680_is_available:
		#bme680_adafruit.print_compact()
		bme680_adafruit.get_values()
	if as7341_is_available: 
		#as7341_adafruit.verbose_output()
		#as7341_adafruit.compact_output()
		as7341_adafruit.get_values()
	j += 1
	if 0==j%N:
		if dotstar_is_available:
			dotstar[0] = (0, 255, 0, dotstar_brightness)
		if bme680_is_available:
			values = bme680_adafruit.get_average_values()
			string = str(values)
			send_a_message_with_timestamp("bme680 " + string)
		if as7341_is_available:
			values = as7341_adafruit.get_average_values()
			string = str(values)
			send_a_message_with_timestamp("as7341 " + string)

