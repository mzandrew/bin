# written 2021-12-28 by mza
# last updated 2022-01-08 by mza

import sys
import time
from DebugInfoWarningError24 import debug, info, warning, error, debug2, debug3, set_verbosity, create_new_logfile_with_string_embedded, flush

def reset():
	try:
		error("resetting board...")
		sys.stdout.flush()
	except:
		pass
	try:
		time.sleep(10)
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

