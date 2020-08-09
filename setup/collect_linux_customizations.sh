#!/bin/bash -e

# last updated 2020-08-09 by mza

declare date=$(date +"%Y-%m-%d")
declare hostname=$(hostname)
mkdir -p ${HOME}/build
declare list=""
list="$list etc/wpa_supplicant/wpa_supplicant.conf"
list="$list etc/hostname"
list="$list etc/hosts"
list="$list etc/passwd"
list="$list etc/group"
list="$list etc/shadow"
list="$list etc/fstab"
list="$list etc/sysctl.conf"
list="$list etc/default/keyboard"
list="$list etc/sysconfig/keyboard"
list="$list etc/ntp.conf"
list="$list etc/apt/apt.conf"
list="$list etc/yum.conf"
list="$list etc/yum.repos.d"
list="$list boot/config.txt"
#list="$list boot/SSH"

declare final_list=""
cd /
for each in $list; do
	if [ -e "$each" ]; then
		final_list="$final_list $each"
#	else
#		echo "file \"$each\" not found"
	fi
done

mkdir -p "${HOME}/build"
sudo tar cf "${HOME}/build/${date}.${hostname}.linux-customizations.tar" $final_list

