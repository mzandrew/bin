#!/bin/bash

# last updated 2025-01-13 by mza

declare file="640" dir="750"
declare filename="actions-taken-to-clean-up-files.txt"
declare action_file="-exec rm -fv {} ;"
declare action_dirtree="-exec rm -rfv {} ;"
declare action_emptyfile="-exec rm -fv {} ;"
declare action_emptydir="-exec rmdir -v {} ;"
declare -i verbosity=4

#sudo chown mza . -R
#find -type d -exec chmod --changes $dir {} \; -o -type f -exec chmod --changes $file {} \;

if [ $verbosity -gt 3 ]; then echo; echo "lf-r.original"; fi
if [ ! -e lf-r.original ]; then lf > lf-r.original; fi
if [ $verbosity -gt 3 ]; then echo; echo "du-ma1.original"; fi
if [ ! -e du-ma1.original ]; then dume; mv du-ma1 du-ma1.original; fi

if [ $verbosity -gt 3 ]; then echo; echo "chmod u+rwx dirs"; fi
find -type d -exec chmod u+rwx --changes {} \; | tee -a ${filename}

if [ $verbosity -gt 3 ]; then echo; echo "superfluous files"; fi
find -depth -type f -name "*.log" -print0 | tar rf log.tar --remove-files --null -T -

if [ $verbosity -gt 3 ]; then echo; echo "empty files"; fi
find -type f -empty ${action_emptyfile} | tee -a ${filename}

if [ $verbosity -gt 3 ]; then echo; echo "superfluous dirs"; fi
mkdir -p extracts
find -depth -type d -wholename "*/.cache/mozilla" -exec rm -rf {} \;
find -depth -type d -wholename "*/.mozilla/firefox/*/saved-telemetry-pings" -exec rm -rf {} \;
find -depth -type d -wholename "*/.mozilla/firefox/*/extensions" -exec rm -rf {} \;
find -depth -type d -wholename "*/.mozilla/firefox/*/datareporting" -exec rm -rf {} \;
find -depth -type d -name adexl -print0 | tar rvf extracts/adexl.tar --remove-files --null -T -
find -depth -type d -name spectre -print0 | tar rvf extracts/spectre.tar --remove-files --null -T -
find -depth -type d -name .artist_states -print0 | tar rvf extracts/artist-states.tar --remove-files --null -T -
find -depth -type d -name LVS -print0 | tar rvf extracts/LVS.tar --remove-files --null -T -
find -depth -type d -name LVS_Calibre -print0 | tar rvf extracts/LVS_Calibre.tar --remove-files --null -T -
find -depth -type d -name DRC -print0 | tar rvf extracts/DRC.tar --remove-files --null -T -
find -depth -type d -name DRC_Calibre -print0 | tar rvf extracts/DRC_Calibre.tar --remove-files --null -T -
find -depth -type d -name skywater-pdk -print0 | tar rvf extracts/skywater-pdk.tar --remove-files --null -T -
find -depth -type d -name ".local" -print0 | tar rvf extracts/local.tar --remove-files --null -T -
find -depth -type d -iname logs -print0 | tar rvf extracts/logs.tar --remove-files --null -T -
find -depth -type d -name .abstract -print0 | tar rvf extracts/abstract.tar --remove-files --null -T -
find -depth -type d -name .cache -print0 | tar rvf extracts/cache.tar --remove-files --null -T -
#find -depth -type d -name "T-013-MM-SP.RF-1P8M-FSG-IMD.thin_old" -o -name "TSMC_025G_1P5M" -o -name "T-013-MM-SP.RF-1P8M-FSG-IMD.thin" -o -name "TSMC_025G_1P5M" -o -name "TSMC_018_1P6M" -o -name "tcb018gbwp7t" -print0 | tar rvf extracts/design-kit-copies.tar --remove-files --null -T -

#for each lowest level, do this: find -maxdepth 1 -name ".[a-zA-Z0-9]*" -print0 | tar rvf extracts/dotfiles.tar --remove-files --null -T -

if [ $verbosity -gt 3 ]; then echo; echo "empty dirs"; fi
find -depth -type d -empty ${action_emptydir} | tee -a ${filename}

if [ $verbosity -gt 3 ]; then echo; echo "duplicate files"; fi
echo
lf | duplicate_finder.py
./script_to_remove_all_duplicates_that_are_not_golden.sh

if [ $verbosity -gt 3 ]; then echo; echo "adjust timestamps of dirs"; fi
adjust_datestamps_of_dirs_based_on_their_contents

if [ $verbosity -gt 3 ]; then echo; echo "lf-r"; fi
lf > lf-r
if [ $verbosity -gt 3 ]; then echo; echo "du-ma1"; fi
dume

# search harder for key files in the design kit dirs
# consier deleting 0 byte files

