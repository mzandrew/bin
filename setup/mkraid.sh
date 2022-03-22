#!/bin/bash -e

# written 2022-03-08 by mza
# based on notes from building raid on cadence server a couple years ago
# last updated 2022-03-09 by mza
 
declare -i number_of_devices=2
declare device_list="sdc sdd" # create on these devices
declare destination="raid5" # use this name under /dev/md/

declare pv_list=""

for each in $device_list; do
	#fdisk -l /dev/${each}
	#parted /dev/${each} mklabel gpt
	#parted /dev/${each} unit tb mkpart pri ext2 0 2
	#parted /dev/${each} toggle 1 raid
	#parted /dev/${each} print
	#fdisk -l /dev/${each}
	partition_list="$pv_list /dev/${each}1"
done
#mdadm --create /dev/md/${destination} --level 5 --raid-devices=$number_of_devices $partition_list
#mdadm --misc --detail /dev/md/${destination}

#pvs
#pvcreate /dev/md/${destination} # registers this "physical volume" for use with lvm
#pvs

#vgs
#vgcreate voyager /dev/md/${destination} # creates a "volume group" container to which one can start adding "physical volumes"
#vgs

#lvs
#lvcreate --extents 100%FREE voyager -n home
#lvs

#mkfs.ext4 -m 0 /dev/mapper/voyager-home
#add an entry for this in /etc/fstab
#mount /home7
#create symlink to it called /home

# to add a device after it is built:
#each="sde"
#parted /dev/${each} mklabel gpt
#parted /dev/${each} unit tb mkpart pri ext2 0 2
#parted /dev/${each} toggle 1 raid
#mdadm /dev/md127 --add /dev/${each}1
#mdadm /dev/md127 --grow --raid-disks=3
#mdadm /dev/md127 --grow --size=max
#pvresize /dev/md127
#lvextend /dev/voyager/home --extents +100%FREE --resizefs

