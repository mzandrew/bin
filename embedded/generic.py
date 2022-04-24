# written 2021-12-28 by mza
# last updated 2022-01-18 by mza

import sys
import time
import atexit
import supervisor
from DebugInfoWarningError24 import debug, info, warning, error, debug2, debug3, set_verbosity, create_new_logfile_with_string_embedded, flush

def register_atexit_handler():
	atexit.register(reset)

def keyboard_interrupt_exception_handler():
	info("caught ctrl-c")
	flush()
	atexit.unregister(reset)
	sys.exit(0)

def reload_exception_handler():
	info("reload exception")
	flush()
	atexit.unregister(reset)
	time.sleep(1)
	supervisor.reload()

def reset():
	try:
		error("resetting board... (ctrl-c to abort)")
		sys.stdout.flush()
	except:
		pass
#	try:
#		displayio.release_displays()
#	except:
#		pass
	try:
		time.sleep(10)
	except KeyboardInterrupt:
		info("caught ctrl-c")
		flush()
		atexit.unregister(reset)
		sys.exit(0)
	except:
		pass
	try:
		info("")
		flush()
	except:
		pass
	try:
		import microcontroller
		microcontroller.reset()
	except:
		pass
	try:
		warning("can't reset board")
		flush()
	except:
		pass

# https://learn.adafruit.com/circuitpython-essentials/circuitpython-pwm
PWM_MAX = 65535
def setup_status_leds(red_pin, green_pin, blue_pin):
	global status_led
	status_led = []
	try:
		import pwmio
		PWM_MAX = 65535
		status_led.append(pwmio.PWMOut(red_pin,   frequency=5000, duty_cycle=PWM_MAX))
		status_led.append(pwmio.PWMOut(green_pin, frequency=5000, duty_cycle=PWM_MAX))
		status_led.append(pwmio.PWMOut(blue_pin,  frequency=5000, duty_cycle=PWM_MAX))
		return True
	except:
		warning("can't find library pwmio; can't control backlight brightness")
		return False

def set_status_led_color(desired_color):
	global status_led
	for i in range(3):
		duty_cycle = int(PWM_MAX - 1.0*PWM_MAX*desired_color[i])
		if duty_cycle<0:
			duty_cycle = 0
		if PWM_MAX<duty_cycle:
			duty_cycle = PWM_MAX
		try:
			status_led[i].duty_cycle = duty_cycle
		except:
			pass

def setup_battery_monitor(i2c):
	global battery
	try:
		import adafruit_bus_device
	except:
		warning("can't find lib adafruit_bus_device")
		return False
	try:
		import adafruit_lc709203f
	except:
		warning("can't find lib adafruit_lc709203f")
		return False
	try:
		battery = adafruit_lc709203f.LC709203F(i2c)
	except:
		warning("can't initialize battery monitor")
		return False
	return True

def get_battery_percentage():
	try:
		return ", %.1f" % battery.cell_percent
	except:
		return ""

def report_battery_percentage():
	try:
		info(get_battery_percentage())
	except:
		pass

