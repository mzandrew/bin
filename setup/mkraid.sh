#!/bin/bash -e

# written 2022-03-08 by mza
# based on notes from building raid on cadence server a couple years ago
# last updated 2022-04-01 by mza
 
# when mdadm says a drive is not fresh, you should rebuild:
#/sbin/mdadm /dev/md0 --fail /dev/sda5 --remove /dev/sda5
#/sbin/mdadm /dev/md0 --add /dev/sda5

declare -i number_of_devices=4
declare device_list="sde sdf sdg sdh" # create on these devices
declare unit="tb"
declare -i size=2
declare pvname="raid5" # use this name under /dev/md/
declare vgname="voyager"
declare lvname="funzies"

function make_partitions {
	for each in $device_list; do
		echo; echo "making partition on ${each}..."
		fdisk -l /dev/${each}
		parted /dev/${each} mklabel gpt
		parted /dev/${each} unit ${unit} mkpart pri ext2 0 ${size}
		parted /dev/${each} toggle 1 raid
		parted /dev/${each} print
		fdisk -l /dev/${each}
	done
}

function make_raid5 {
	echo; echo "making raid5 on ${pvname}..."
	pv_list=""
	for each in $device_list; do
		pv_list="$pv_list /dev/${each}1"
	done
	mdadm --create /dev/md/${pvname} --level 5 --raid-devices=$number_of_devices $pv_list
	mdadm --misc --detail /dev/md/${pvname}
	show_raid_status
}

function show_raid_status {
	cat /proc/mdstat
}

function register_physical_volume {
	pvs
	echo; echo "registering physical volume ${pvname} with lvm..."
	pvcreate /dev/md/${pvname} # registers this "physical volume" for use with lvm
	pvs
}

function create_volume_group {
	vgs
	echo; echo "creating volume group ${vgname} with our pv ${pvname}..."
	vgcreate ${vgname} /dev/md/${pvname} # creates a "volume group" container to which one can start adding "physical volumes", then add our pv
	vgs
}

function create_logical_volume {
	lvs
	echo; echo "creating logical volume ${lvname}..."
	lvcreate --extents 100%FREE ${vgname} -n ${lvname}
	lvs
}

function format_logical_volume {
	echo; echo "formatting logical volume ${lvname}..."
	mkfs.ext4 -m 0 /dev/mapper/${vgname}-${lvname}
	# add an entry for this in /etc/fstab
	#mount /${lvname}7
	# create symlink to it called /${lvname}
}

function add_a_physical_volume_and_expand_logical_volume_and_filesystem {
# to add a device after it is built:
	each="$1"
	parted /dev/${each} mklabel gpt
	parted /dev/${each} unit ${unit} mkpart pri ext2 0 ${size}
	parted /dev/${each} toggle 1 raid
	mdadm /dev/md127 --add /dev/${each}1
	mdadm /dev/md127 --grow --raid-disks=3
	mdadm /dev/md127 --grow --size=max
	pvresize /dev/md127
	lvextend /dev/${vgname}/${lvname} --extents +100%FREE --resizefs
}

make_partitions
make_raid5
register_physical_volume
create_volume_group
create_logical_volume
format_logical_volume
#add_a_physical_volume_and_expand_logical_volume_and_filesystem sde
show_raid_status

