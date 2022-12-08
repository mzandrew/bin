# written 2022-12-07 by mza
# based on lora.py and lora_transceiver_basic_test.py
# last updated 2022-12-07 by mza

import time
import board
import busio
import digitalio
import adafruit_rfm9x
import gc

PREFIX = "SCOOPY"
SUFFIX = "BOOPS"
node_type = "gathering"
BAUD_RATE = 4*57600
RADIO_FREQ_MHZ = 905.0 # 868-915 MHz (902-928 MHz is the allowed band in US/MEX/CAN)
TX_POWER_DBM = 5 # minimum 5; default 13; maximum 23
N = 6

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
		print("should truncate or parcel message because it is too long")
	print("sending: " + message_id_string + message)
	rfm9x.send(bytes(message_with_prefix_and_suffix, "utf-8"))

def setup(spi, cs, reset, frequency, baudrate, tx_power_dbm):
	print("mem free: " + str(gc.mem_free())) # 14k free
	global rfm9x
	rfm9x = adafruit_rfm9x.RFM9x(spi=spi, cs=cs, reset=reset, frequency=frequency, baudrate=baudrate)
	rfm9x.tx_power = tx_power_dbm

def loop():
	print("mem free: " + str(gc.mem_free())) # 14k free
	i = 0
	while True:
		if 0==i%N:
			print("doing something")
			send_a_message("I am here!")
		else:
			print("did nothing")
		i += 1
		time.sleep(10)

if __name__ == "__main__":
	try:
		spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
	except (KeyboardInterrupt, ReloadException):
		raise
	except Exception as error_message:
		spi = board.SPI()
	CS = digitalio.DigitalInOut(board.RFM9X_CS)
	RESET = digitalio.DigitalInOut(board.RFM9X_RST)
	setup(spi, CS, RESET, RADIO_FREQ_MHZ, BAUD_RATE, TX_POWER_DBM)
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
		print(str(error_message))
	loop()

