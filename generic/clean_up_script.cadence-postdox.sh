#!/bin/bash

declare file="640" dir="750"

#sudo chown mza . -R
#find -type d -exec chmod --changes $dir {} \; -o -type f -exec chmod --changes $file {} \;
#lf > lf-r.original
#find -depth -type d -name adexl -print0 | tar cf adexl.tar --remove-files --null -T -
#find -depth -type d -name spectre -print0 | tar cf spectre.tar --remove-files --null -T -
#find -depth -type d -name .artist_states -print0 | tar cf artist-states.tar --remove-files --null -T -
#find -depth -type d -name LVS -print0 | tar cf LVS.tar --remove-files --null -T -
#find -depth -type d -name LVS_Calibre -print0 | tar cf LVS_Calibre.tar --remove-files --null -T -
#find -depth -type d -name DRC -print0 | tar cf DRC.tar --remove-files --null -T -
#find -depth -type d -name DRC_Calibre -print0 | tar cf DRC_Calibre.tar --remove-files --null -T -
#find -depth -type d -name skywater-pdk -print0 | tar cf skywater-pdk.tar --remove-files --null -T -
#find -depth -type d -name ".local" -print0 | tar cf "local.tar" --remove-files --null -T -
#find -depth -type d -iname logs -print0 | tar cf logs.tar --remove-files --null -T -
#find -depth -type d -name .abstract -print0 | tar cf abstract.tar --remove-files --null -T -
#find -depth -type d -name .cache -print0 | tar cf cache.tar --remove-files --null -T -
#find -depth -type d -wholename "*/.cache/mozilla" -exec rm -rf {} \;
#find -depth -type d -wholename "*/.mozilla/firefox/*/saved-telemetry-pings" -exec rm -rf {} \;
#find -depth -type d -wholename "*/.mozilla/firefox/*/extensions" -exec rm -rf {} \;
#find -depth -type d -wholename "*/.mozilla/firefox/*/datareporting" -exec rm -rf {} \;
#find -depth -type f -name "*.log" -print0 | tar cf log.tar --remove-files --null -T -
#find -depth -type d -name "T-013-MM-SP.RF-1P8M-FSG-IMD.thin_old" -o -name "TSMC_025G_1P5M" -o -name "T-013-MM-SP.RF-1P8M-FSG-IMD.thin" -o -name "TSMC_025G_1P5M" -o -name "TSMC_018_1P6M" -o -name "tcb018gbwp7t" -print0 | tar cf design-kit-copies.tar --remove-files --null -T -
#for each lowest level, do this: find -maxdepth 1 -name ".[a-zA-Z0-9]*" -print0 | tar cf dotfiles.tar --remove-files --null -T -
find -depth -type d -empty -exec rmdir {} \;
lf > lf-r
wc lf-r

# search harder for key files in the design kit dirs
# consier deleting 0 byte files

