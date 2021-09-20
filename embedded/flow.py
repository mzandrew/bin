# written 2021-09-19 by mza
# last updated 2021-09-20 by mza

# for a qt py 2040 with a https://www.adafruit.com/product/833 flow meter

# to install on a circuitpython device:

# mount /media/circuitpython/; cd ~/build/adafruit-circuitpython/bundle/lib/; cp adafruit_ssd1327.mpy /media/circuitpython/lib/ ; rsync -r adafruit_display_text /media/circuitpython/lib/; cd ~/build/bin/embedded/; cp oled_adafruit.py /media/circuitpython/; cp flow.py /media/circuitpython/code.py; umount /media/circuitpython

liters_per_count = 0.002

import time
import board
import countio
import busio

def check_pins():
	# https://learn.adafruit.com/circuitpython-essentials/circuitpython-pwm
	import pwmio
	#for pin_name in dir(board):
	for pin_name in ["D0", "A0", "D1", "A1", "SCL"]:
		pin = getattr(board, pin_name)
		try:
			p = pwmio.PWMOut(pin)
			p.deinit()
			print("PWM on:", pin_name)  # Prints the valid, PWM-capable pins!
		except ValueError:  # This is the error returned when the pin is invalid.
			print("No PWM on:", pin_name)  # Prints the invalid pins.
		except RuntimeError:  # Timer conflict error.
			print("Timers in use:", pin_name)  # Prints the timer conflict pins.
		except TypeError:  # Error returned when checking a non-pin object in dir(board).
			pass  # Passes over non-pin objects in dir(board).

def setup():
	global mycounter
	try:
		#print("trying board.D0")
		mycounter = countio.Counter(board.D0) # "RuntimeError: PWM slice already in use"
	except RuntimeError:
		#check_pins()
		time.sleep(2)
		# https://learn.adafruit.com/circuitpython-essentials/circuitpython-resetting
		#import supervisor
		#supervisor.reload() # "Code stopped by auto-reload.  soft reboot" (and does so repeatedly) but does not clear the PWM slice problem
		import microcontroller
		microcontroller.reset() # disconnects /dev/ttyACM0 and forcably unmounts /media/circuitpython, but works in clearing the PWM slice problem
		#print("trying board.D0")
		#mycounter = countio.Counter(board.D0) # "RuntimeError: PWM slice already in use"
		#print("trying board.SCL")
		#mycounter = countio.Counter(board.SCL) # "RuntimeError: PWM slice already in use"
		#raise

def measure():
	return mycounter.count

def measure_string():
	global newcount
	newcount = measure()
	liters = liters_per_count*newcount
	return "%.3f l" % liters

def show_if_changed():
	global oldcount
	string = measure_string()
	if oldcount<newcount:
		print(string)
		oldcount = newcount
	return string

if __name__ == "__main__":
	time.sleep(2)
	setup()
	time.sleep(2)
	try:
		i2c = busio.I2C(board.SCL1, board.SDA1)
		import oled_adafruit
		oled_display_available = oled_adafruit.setup_i2c_oled_display_ssd1327(i2c, 0x3d)
		print("oled display is available")
		#oled_adafruit.clear_display_on_oled_ssd1327()
	except:
		print("unable to find ssd1327 oled display on i2c")
		oled_display_available = False
	oldcount = measure()
	print(measure_string())
	while True:
		string = show_if_changed()
#		if oled_display_available:
#			oled_adafruit.show_text_on_ssd1327(string)
		time.sleep(1)

