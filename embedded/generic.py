# written 2021-12-28 by mza
# last updated 2023-01-04 by mza

import os
import sys
import time
import atexit
import gc
from DebugInfoWarningError24 import debug, info, warning, error, debug2, debug3, set_verbosity, create_new_logfile_with_string_embedded, flush

def hex(number, width=1):
	return "%0*x" % (width, number)

def fround(value, precision):
	if value<0.0:
		extra = -0.5
	else:
		extra = 0.5
	debug2(str(value))
	debug2(str(value/precision))
	debug2(str(value/precision+extra))
	debug2(str(int(value/precision+extra)))
	debug2(str(precision*int(value/precision+extra)))
	return precision*int(value/precision+extra)

def start_uptime():
	global initial_time_monotonic
	global previous_time_monotonic
	initial_time_monotonic = time.monotonic()
	previous_time_monotonic = initial_time_monotonic

def get_uptime():
	global previous_time_monotonic
	try:
		initial_time_monotonic
	except:
		start_uptime()
	previous_time_monotonic = time.monotonic()
	diff = previous_time_monotonic - initial_time_monotonic
	debug2("previous_time_monotonic: " + str(previous_time_monotonic) + " s")
	debug2("diff: " + str(diff) + " s")
	return diff

def show_uptime():
	uptime = get_uptime()
	info("uptime: " + str(int(uptime + 0.5)) + " s")
	return uptime

def start_loop_time():
	global previous_loop_time_monotonic
	#previous_loop_time_monotonic = time.monotonic()
	try:
		previous_time_monotonic
	except:
		start_uptime()
	previous_loop_time_monotonic = previous_time_monotonic
	debug2("previous_loop_time_monotonic: " + str(previous_loop_time_monotonic) + " s")

def get_loop_time():
	global previous_loop_time_monotonic
	try:
		previous_loop_time_monotonic
	except:
		start_loop_time()
	new = time.monotonic()
	diff = new - previous_loop_time_monotonic
	previous_loop_time_monotonic = new
	debug2("new: " + str(new) + " s")
	debug2("diff: " + str(diff) + " s")
	debug2("previous_loop_time_monotonic: " + str(previous_loop_time_monotonic) + " s")
	return diff

def show_loop_time():
	loop_time = get_loop_time()
	info("loop time: " + str(loop_time) + " s")
	return loop_time

def adjust_delay_for_desired_loop_time(delay_between_acquisitions, N, desired_loop_time):
	loop_time = show_loop_time()
	if 1:
		time_needed_to_do_business = loop_time - float(N)*delay_between_acquisitions
		delay_between_acquisitions = (desired_loop_time - time_needed_to_do_business) / float(N)
	else:
		diff = loop_time - desired_loop_time
		delay_between_acquisitions -= diff / float(N)
	if delay_between_acquisitions<0.0:
		delay_between_acquisitions = 0.0
	info("new delay_between_acquisitions = " + str(delay_between_acquisitions))
	return delay_between_acquisitions

def register_atexit_handler():
	atexit.register(reset)

def keyboard_interrupt_exception_handler():
	atexit.unregister(reset)
	info("")
	info("caught ctrl-c")
	flush()
	sys.exit(0)

def reload_exception_handler():
	import supervisor
	atexit.unregister(reset)
	info("")
	info("reload exception")
	flush()
	time.sleep(2)
	supervisor.reload()

def reset():
	atexit.unregister(reset)
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
		time.sleep(60)
	except KeyboardInterrupt:
		keyboard_interrupt_exception_handler()
	except:
		info("couldn't sleep (60), sorry!")
		flush()
	try:
		info("")
		flush()
	except:
		pass
	try:
		time.sleep(2)
	except:
		info("couldn't sleep (2), sorry!")
		flush()
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
	sys.exit(0)

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

def convert_date_to_local_time(datestamp):
	from datetime import datetime
	from dateutil import tz
	from_zone = tz.tzutc()
	to_zone = tz.tzlocal()
	utc = datetime.strptime(datestamp, "%Y-%m-%dT%H:%M:%SZ")
	#print(str(utc))
	utc = utc.replace(tzinfo=from_zone)
	#print(str(utc))
	localtime = utc.astimezone(to_zone)
	#print(str(localtime))
	#datestamp = localtime.strptime(localtime, "%Y-%m-%d %H:%M:S%z")
	datestamp = localtime.strftime("%Y-%m-%d+%H:%M")
	#print(str(datestamp))
	return datestamp

def convert_date_to_UTC_time(datestamp):
	from datetime import datetime
	utc = datetime.strptime(datestamp, "%Y-%m-%dT%H:%M:%SZ")
	datestamp = utc.strftime("%Y-%m-%d %H:%M:%S UTC")
	#print(str(datestamp))
	return datestamp

def show_memory_situation():
	print("gc.mem_alloc(): " + str(gc.mem_alloc()))
	print("gc.mem_free(): " + str(gc.mem_free()))
	print("gc.collect()")
	gc.collect()
	print("gc.mem_alloc(): " + str(gc.mem_alloc()))
	print("gc.mem_free(): " + str(gc.mem_free()))

def show_memory_difference():
	global previous_allocated_memory
	try:
		previous_allocated_memory
	except:
		previous_allocated_memory = gc.mem_alloc()
	current_allocated_memory = gc.mem_alloc()
	difference = current_allocated_memory - previous_allocated_memory
	print("difference: " + str((difference)))
	previous_allocated_memory = current_allocated_memory
	return difference

def collect_garbage():
	gc.collect()

def running_circuitpython():
	uname = os.uname()
	# posix.uname_result(sysname='Linux', nodename='2023-pi0w-hyperpixel', release='5.15.76+', version='#1597 Fri Nov 4 12:11:43 GMT 2022', machine='armv6l')
	# (sysname='samd51', nodename='samd51', release='7.2.5', version='7.2.5 on 2022-04-06', machine='SparkFun Thing Plus - SAMD51 with samd51j20')
	if 'Linux'==uname.sysname:
		return False
	return True

def os_ver():
	uname = os.uname()
	return uname.release

def print_os_ver():
	print("running on circuitpython " + os_ver())

