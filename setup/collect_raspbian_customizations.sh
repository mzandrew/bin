#!/bin/bash -e

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
list="$list etc/ntp.conf"
list="$list etc/apt/apt.conf"
list="$list boot/config.txt"
#list="$list boot/SSH"
cd /
sudo tar cf ${HOME}/build/${date}.${hostname}.raspbian-customizations.tar $list

