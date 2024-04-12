#!/bin/bash -e

# written 2023-10-22 by mza
# from section 8 "Alternatives" on https://wiki.archlinux.org/title/badblocks
# last updated 2023-10-28 by mza

# times listed are for an 8 GB microSD card / 512 GB microSD card
declare device="${@}"

if [ ! -e "${device}" ]; then
	echo "usage:"
	echo "$0 /dev/sde"
	exit 1
fi

function go {
	local device="${@}"
	local datestamp=$(date +"%Y%m%d%H%M%S")
	local name="goodblock-${datestamp}"
	read -p "Are you sure?  This will destroy all data on device ${device} : " -n 1 -r
	echo
	if [[ $REPLY =~ ^[Yy]$ ]]; then
		echo "dd..."
		time dd if=/dev/zero of=${device} bs=1M # 41m / 1448m
		echo "cryptsetup open..."
		time echo -n "12345" | cryptsetup open ${device} ${name} --type plain --cipher aes-xts-plain64 - # 1s / 4s
		echo "shred..."
		time shred -v -n 0 -z /dev/mapper/${name} # 23m / 266m
		echo "cmp..."
		time cmp -b /dev/zero /dev/mapper/${name} # 3m / 197m
		echo "cryptsetup close..."
		time cryptsetup close ${name}
		echo "dd..."
		time dd if=/dev/zero of=${device} bs=1M # 41m / 1448m
	else
		echo "cancelled"
	fi
}

# from https://unix.stackexchange.com/a/269080/150012
GOFUNC=$(declare -f go)
sudo bash -c "$GOFUNC; go ${device}"

