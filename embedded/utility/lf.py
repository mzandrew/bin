# to install:
# cd lib
# rsync -av adafruit_datetime.mpy adafruit_sdcard.mpy /media/mza/CIRCUITPY/lib/
# cd ..
# cp -a lf.py /media/mza/CIRCUITPY/code.py; sync

import microsd_adafruit
print("")
microsd_adafruit.list_files("")

