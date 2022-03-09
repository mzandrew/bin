#!/bin/bash -e

# written 2022-03-08 by mza
# based on notes from building raid on cadence server a couple years ago
# last updated 2022-03-08 by mza

declare device_list="sdb sdc sdd" # create on these devices
declare destination="raid5" # use this name under /dev/md/

declare pv_list=""

pvs
for each in $device_list; do
	fdisk -l /dev/${each}
#	parted /dev/${each} mklabel gpt
#	parted /dev/${each} unit tb mkpart pri ext2 0 2
#	parted /dev/${each} toggle 1 raid
#	parted /dev/${each} print
#	fdisk -l /dev/${each}
#	pvcreate /dev/${each}1
	pv_list="$pv_list /dev/${each}1"
done
#pvs
#mdadm --create /dev/md/${destination} --level 5 --raid-devices=3 $pv_list
#mdadm --misc --detail /dev/md/${destination}

