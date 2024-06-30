# written 2021-12-28 by mza
# last updated 2024-06-29 by mza

import os, sys, time, atexit, re
import gc
from DebugInfoWarningError24 import debug, info, warning, error, debug2, debug3, set_verbosity, create_new_logfile_with_string_embedded, flush

def hex(number, width=1, pad_with_zeroes=True):
	if pad_with_zeroes:
		return "%0*x" % (width, number)
	else:
		return "%*x" % (width, number)

def dec(number, width=1, pad_with_zeroes=True):
	if pad_with_zeroes:
		return "%0*d" % (width, number)
	else:
		return "%*d" % (width, number)

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
		error("resetting board in 300 seconds... (ctrl-c to abort)")
		sys.stdout.flush()
	except:
		pass
#	try:
#		displayio.release_displays()
#	except:
#		pass
	try:
		time.sleep(300)
	except KeyboardInterrupt:
		keyboard_interrupt_exception_handler()
	except:
		info("couldn't sleep (300), sorry!")
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

def collect_garbage(should_show_status=False):
	alloc_before = gc.mem_alloc()
	free_before = gc.mem_free()
	gc.collect()
	alloc_after = gc.mem_alloc()
	free_after = gc.mem_free()
	if should_show_status:
		print("gc.mem_alloc(before/after): " + str(alloc_before) + "/" + str(alloc_after))
		print("gc.mem_free(before/after): " + str(free_before) + "/" + str(free_after))

def show_memory_situation():
	collect_garbage(True)

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

def is_blinka():
	from board import board_id
	if board_id=='GENERIC_LINUX_PC':
		info("running blinka")
		print_os_ver()
		if running_circuitpython():
			info("uname.sysname is Linux")
		info(str(os.uname()))

def filesize(filename):
	from os import stat
	stats = stat(filename)
	filesize = stats[6]
	return filesize

def show_filesize(filename):
	myfilesize = filesize(filename)
	info('{0:>12} {1:<40}'.format(str(myfilesize), filename))

def linecount(filename):
	linecount = 0
	# from https://stackoverflow.com/a/1019572/5728815
	with open(filename, "rb") as myfile:
		linecount = sum(1 for _ in myfile)
	return linecount

def show_linecount(filename):
	mylinecount = linecount(filename)
	info('{0:>6} {1:<40}'.format(str(mylinecount), filename))

def wc(filename):
	myfilesize = filesize(filename)
	mylinecount = linecount(filename)
	return myfilesize, mylinecount

def show_wc(filename):
	myfilesize, mylinecount = wc(filename)
	info('{0:>6} {1:>12} {2:<40}'.format(str(mylinecount), str(myfilesize), filename))

ignore_dir_list = [ ".git", "__pycache__" ]
def walktree(dirname, func_file, additional_func_dir=None):
	import stat
	#print("dirname \"" + dirname + "\" found")
	matched = False
	for pdn in ignore_dir_list:
		#match = re.search(pdn, dirname, flags=re.IGNORECASE)
		match = re.search("^" + pdn + "$", os.path.basename(dirname))
		if match:
			matched = True
	if matched:
		return False
	if not os.path.exists(dirname):
		error(dirname + " does not exist")
		return False
	dirmode = os.stat(dirname).st_mode
	filelist = []
	if stat.S_ISDIR(dirmode):
		filelist = os.listdir(dirname)
	elif stat.S_ISREG(dirmode):
		filelist = [ dirname ]
		dirname = ""
	for filename in filelist:
		pathname = os.path.join(dirname, filename)
		if not os.path.exists(pathname):
			error("file " + pathname + " does not exist")
			continue
		mode = os.stat(pathname).st_mode
		if stat.S_ISDIR(mode):
			if walktree(pathname, func_file, additional_func_dir):
				if additional_func_dir is not None:
					additional_func_dir(pathname)
		elif stat.S_ISREG(mode):
			func_file(pathname)
		else:
			info("found non-dir, non-regular-file " + pathname)
	return True

dirnames = []
def process_dir(dirname):
	dirnames.append(dirname)

filenames = []
def process_file(filename):
	filenames.append(filename)

def process_files(destination):
	import shutil
	for filename in filenames:
		#info("(file) " + filename)
		src = int(os.stat(filename).st_mtime)//2
		try:
			dst = int(os.stat(destination + "/" + filename).st_mtime)//2
		except:
			dst = 0
		if dst<src:
			info(filename)
			shutil.copy2(filename, destination + "/" + filename)

def process_dirs(destination):
	for dirname in dirnames:
		#info("(dir) " + dirname)
		if not os.path.exists(destination + "/" + dirname):
			info(dirname)
			mkdir_with_parents(destination + "/" + dirname)

def mkdir_with_parents(dirname):
	if 3<=sys.version_info.major and 5<=sys.version_info.minor:
		import pathlib
		pathlib.Path(dirname).mkdir(parents=True, exist_ok=True)
	else:
		error("unimplemented in python < 3.5")

def rsync(src, dst):
	walktree(src, process_file, process_dir)
	if not os.path.exists(dst):
		mkdir_with_parents(dst)
	process_dirs(dst)
	process_files(dst)

def install(destination, self, files_list, other_dir_list, lib_dir, lib_files_list, lib_dirs_list):
	import shutil
	info("installing to " + destination + "/")
	for dir in lib_dirs_list:
		src = int(os.stat(lib_dir + "/" + dir).st_mtime)//2
		try:
			dst = int(os.stat(destination + "/lib/" + dir).st_mtime)//2
		except:
			dst = 0
		if dst<src:
			info(dir)
			shutil.copytree(lib_dir + "/" + dir, destination + "/lib/" + dir)
	for i in range(len(other_dir_list)):
		if not os.path.exists(dst):
			mkdir_with_parents(destination + "/" + other_dir_list[i])
		rsync(other_dir_list[i], destination)
	for file in lib_files_list:
		src = int(os.stat(lib_dir + "/" + file).st_mtime)//2
		try:
			dst = int(os.stat(destination + "/lib/" + file).st_mtime)//2
		except:
			dst = 0
		if dst<src:
			info(file)
			shutil.copy2(lib_dir + "/" + file, destination + "/lib")
	for file in files_list:
		src = int(os.stat(file).st_mtime)//2
		try:
			dst = int(os.stat(destination + "/" + file).st_mtime)//2
		except:
			dst = 0
		#info(str(src) + " " + str(dst))
		if dst<src:
			info(file)
			shutil.copy2(file, destination)
	self = os.path.basename(self)
	info(self + " -> code.py")
	shutil.copy2(self, destination + "/code.py")
	os.sync()

