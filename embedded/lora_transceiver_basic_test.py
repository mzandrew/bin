# basic bits taken from adafruit's rfm9x_simpletest.py by Tony DiCola and rfm9x_node1_ack.py by Jerry Needell
# last updated 2022-10-18 by mza

# rsync -a *.py /media/mza/LORASEND/; rsync -a *.py /media/mza/LORARECEIVE/
# cd lib
# rsync -r adafruit_register adafruit_rfm9x.mpy adafruit_as7341.mpy adafruit_bme680.mpy adafruit_requests.mpy adafruit_pcf8523.mpy adafruit_dotstar.mpy /media/mza/LORASEND/lib/; rsync -r adafruit_register adafruit_rfm9x.mpy adafruit_as7341.mpy adafruit_bme680.mpy adafruit_io adafruit_minimqtt adafruit_requests.mpy adafruit_pcf8523.mpy adafruit_dotstar.mpy /media/mza/LORARECEIVE/lib/
# cp -a lora_transceiver_basic_test.py /media/mza/LORASEND/code.py; cp -a lora_transceiver_basic_test.py /media/mza/LORARECEIVE/code.py
# sync

BAUD_RATE = 4*57600
TIMEOUT = 0.5
PREFIX = "SCOOPY"
SUFFIX = "BOOPS"
N = 32
USE_ACKNOWLEDGE = False
RADIO_FREQ_MHZ = 915.0 # Must match your module!
#RADIO_FREQ_MHZ = 868.0 # Must match your module!
#TX_POWER_DBM = 23 # default 13; maximum 23
TX_POWER_DBM = 20 # default 13; maximum 23
#TX_POWER_DBM = 13 # default 13; maximum 23

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
	info("we are " + board.board_id)
	global dotstar_is_available
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
	global label
	label = "unknown"
	try:
		m = storage.getmount("/")
		label = m.label
	except:
		pass
	info("our label is " + label)
	if "LORARECEIVE"==label:
		should_use_bme680 = False
		should_use_as7341 = False
		should_use_RTC = False
		should_use_airlift = False
		use_built_in_wifi = True
	elif "LORASEND"==label:
		should_use_bme680 = True
		should_use_as7341 = True
		should_use_RTC = True
		should_use_airlift = False
		use_built_in_wifi = True
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
	except:
		spi = board.SPI()
	global i2c
	try:
		i2c = board.I2C()
	except (KeyboardInterrupt, ReloadException):
		raise
	except:
		i2c = busio.I2C(board.SCL, board.SDA)
	global bme680_is_available
	bme680_is_available = False
	if should_use_bme680:
		try:
			bme680_adafruit.setup(i2c, N)
			bme680_is_available = True
		except (KeyboardInterrupt, ReloadException):
			raise
		except:
			warning("bme680 not present")
	global as7341_is_available
	as7341_is_available = False
	if should_use_as7341:
		try:
			i2c_address = as7341_adafruit.setup(i2c, N)
			#prohibited_addresses.append(i2c_address)
			as7341_is_available = True
		except (KeyboardInterrupt, ReloadException):
			raise
		except:
			warning("as7341 not present")
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
		except:
			RTC_is_available = False
	global airlift_is_available
	airlift_is_available = False
	if should_use_airlift:
		if use_built_in_wifi:
			airlift_is_available = airlift.setup_wifi("russell")
		else:
			airlift_is_available = airlift.setup_airlift("russell", spi, board.D13, board.D11, board.D12)
		#header_string += ", RSSI-dB"
	if 1:
		if airlift_is_available:
			if RTC_is_available:
				airlift.update_time_from_server()

def send_a_message(message):
	global message_id
	try:
		message_id += 1
	except:
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
	except:
		previously_received_message_id = 0
	global total_skipped_messages
	try:
		total_skipped_messages
	except:
		total_skipped_messages = 0
	this_message_id = 0
	try:
		rssi = rfm9x.last_rssi
	except (KeyboardInterrupt, ReloadException):
		raise
	except:
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
				warning("skipped " + str(skipped_messages) + " message(s)")
			total_skipped_messages += skipped_messages
			info("received: [" + str(this_message_id) + "]" + message + " RSSI=" + str(rssi) + "dBm")
			previously_received_message_id = this_message_id
		else:
			debug("received: " + packet_text + " RSSI=" + str(rssi) + "dBm")
	except (KeyboardInterrupt, ReloadException):
		raise
	except:
		warning("message garbled RSSI=" + str(rssi) + "dBm")
		info("total skipped messages: " + str(total_skipped_messages))
	return this_message_id

setup()
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
		if "LORASEND"==label:
			time.sleep(3)
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
			#info(string)
			#info(len(string))
			send_a_message_with_timestamp("bme680 " + string)
			#if airlift_is_available:

