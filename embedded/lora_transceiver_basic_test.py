# basic bits taken from adafruit's rfm9x_simpletest.py by Tony DiCola and rfm9x_node1_ack.py by Jerry Needell
# last updated 2022-07-14 by mza

# rsync -a *.py /media/mza/LORASEND/; rsync -a *.py /media/mza/LORARECEIVE/
# cd lib
# rsync -r adafruit_register adafruit_rfm9x.mpy adafruit_as7341.mpy adafruit_bme680.mpy adafruit_requests.mpy adafruit_pcf8523.mpy adafruit_dotstar.mpy /media/mza/LORASEND/lib/; rsync -r adafruit_register adafruit_rfm9x.mpy adafruit_as7341.mpy adafruit_bme680.mpy adafruit_requests.mpy adafruit_pcf8523.mpy adafruit_dotstar.mpy /media/mza/LORARECEIVE/lib/
# cp -a rfm9x_simpletest.py /media/mza/LORASEND/lib/; cp -a rfm9x_simpletest.py /media/mza/LORARECEIVE/lib/
# sync

BAUD_RATE = 1000000
TIMEOUT = 0.5
PREFIX = "SCOOPY"
SUFFIX = "BOOPS"
N = 32
USE_ACKNOWLEDGE = False
RADIO_FREQ_MHZ = 915.0 # Must match your module!
#RADIO_FREQ_MHZ = 868.0 # Must match your module!
TX_POWER_DBM = 23 # default 13; maximum 23
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
	print("we are " + board.board_id)
	global dotstar_is_available
	dotstar_is_available = False
	if 'unexpectedmaker_feathers2'==board.board_id: # for uf2 boot, click [RESET], then about a second later click [BOOT]
		import feathers2
		feathers2.enable_LDO2(True)
		feathers2.led_set(False)
		r = 25
		g = 50
		b = 100
		dotstar_brightness = 0.125
		global dotstar
		dotstar = adafruit_dotstar.DotStar(board.APA102_SCK, board.APA102_MOSI, 1, brightness=dotstar_brightness, auto_write=True)
		dotstar[0] = (r, g, b, dotstar_brightness)
		dotstar_is_available = True
	#else:
	m = storage.getmount("/")
	label = m.label
	print("our label is " + label)
	if "LORARECEIVE"==label:
		should_use_bme680 = False
		should_use_as7341 = False
		should_use_RTC = False
		should_use_airlift = False
		use_built_in_wifi = True
	else:
		should_use_bme680 = True
		should_use_as7341 = True
		should_use_RTC = True
		should_use_airlift = False
		use_built_in_wifi = True
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
		print("we are node " + str(rfm9x.node))
	global RTC_is_available
	if should_use_RTC:
		try:
			i2c_address = pcf8523_adafruit.setup(i2c)
			#prohibited_addresses.append(i2c_address)
			RTC_is_available = True
		except:
			RTC_is_available = False
	else:
		RTC_is_available = False
	global airlift_is_available
	if should_use_airlift:
		if use_built_in_wifi:
			airlift_is_available = airlift.setup_wifi("russell")
		else:
			airlift_is_available = airlift.setup_airlift("russell", spi, board.D13, board.D11, board.D12)
		#header_string += ", RSSI-dB"
	else:
		airlift_is_available = False
	if 1:
		if airlift_is_available:
			airlift.update_time_from_server()

def send_a_message(message):
	message_with_prefix_and_suffix = PREFIX + message + SUFFIX
	if 252<len(message_with_prefix_and_suffix):
		warning("should truncate or parcel message because it is too long")
	print("sending: " + message)
	if USE_ACKNOWLEDGE:
		if rfm9x.send_with_ack(bytes(message_with_prefix_and_suffix, "utf-8")):
			print("ack received")
		else:
			print("no ack received")
	else:
		rfm9x.send(bytes(message_with_prefix_and_suffix, "utf-8"))

def send_a_message_with_timestamp(message):
	if RTC_is_available:
		timestring = pcf8523_adafruit.get_timestring2()
		message = timestring + " " + message
	send_a_message(message)

def decode_a_message(packet):
	rssi = rfm9x.last_rssi
	#print("Received signal strength: {0} dBm".format(rssi))
	try:
		packet_text = str(packet, "ascii")
		match = re.search("^(" + PREFIX + ")(.*)(" + SUFFIX + ")$", packet_text)
		if match:
			message = match.group(2)
			#print("Received (raw bytes): {0}".format(packet))
			print("received: " + message + " RSSI=" + str(rssi) + "dBm")
	except (KeyboardInterrupt, ReloadException):
		raise
	except:
		print("warning:  message garbled RSSI=" + str(rssi) + "dBm")

setup()
send_a_message("Hello world!")

i = 0
j = 0
should_send_a_message = False
print("Waiting for packets...")
while True:
	if dotstar_is_available:
		dotstar[0] = (0, 0, 255)
	LED.value = False
	should_send_a_message = False
	if not button.value:
		should_send_a_message = True
	if should_send_a_message:
		should_send_a_message = False
		send_a_message("the eating is good " + str(i))
		i += 1
	if USE_ACKNOWLEDGE:
		packet = rfm9x.receive(with_ack=True, timeout=TIMEOUT)
	else:
		packet = rfm9x.receive(timeout=TIMEOUT)
	if packet is not None:
		LED.value = True
		decode_a_message(packet)
	if dotstar_is_available:
		dotstar[0] = (255, 0, 0)
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
			dotstar[0] = (0, 255, 0)
		if bme680_is_available:
			values = bme680_adafruit.get_average_values()
			string = str(values)
			#print(string)
			#print(len(string))
			send_a_message_with_timestamp("bme680 " + string)
			#if airlift_is_available:

