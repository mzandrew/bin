#!/bin/bash -e

# written 2020-05-14 by mza
# merged content from other, similar script "create-tar-file-with-linux-configuration-stuff-in-etc"
# last updated 2020-08-09 by mza

configfile="${HOME}/.collect_linux_customizations"
if [ ! -e "${configfile}" ]; then
	declare hostname=$(hostname)
	echo "
name=\"${hostname}-server-config-files\"
destination=\"/root\"
" >"${configfile}"
fi

. "${configfile}"

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
list="$list etc/inittab"
list="$list etc/sudoers"
list="$list etc/sysconfig/networking/devices/ifcfg-em1"
list="$list etc/sysconfig/networking/devices/ifcfg-eth0"
list="$list etc/sysconfig/iptables"
list="$list etc/resolv.conf"
list="$list etc/ssh/sshd_config"
list="$list etc/rsyslog.conf"
list="$list etc/logrotate.conf"

declare final_list=""
cd /
for each in $list; do
	if [ -e "$each" ]; then
		final_list="$final_list $each"
#	else
#		echo "file \"$each\" not found"
	fi
done

declare date=$(date +"%Y-%m-%d")
declare filename="${destination}/${date}.${name}.tar"
mkdir -p "${HOME}/build"
#sudo tar cf "${HOME}/build/${date}.${hostname}.linux-customizations.tar" $final_list
sudo tar cf "${filename}" ${final_list}
sudo ls -lart "${filename}"

