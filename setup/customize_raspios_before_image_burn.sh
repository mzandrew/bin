#!/bin/bash -e

# written 2020-11-21 by mza
# last updated 2022-06-02 by mza

declare desired_locale="en_US.UTF-8"
declare desired_keyboard="us"
declare desired_timezone="Pacific/Honolulu"

declare -i should_add_a_third_partition=0
declare -i wholeimagesize_intended=7500000000
declare -i partition2size_intended=7000000000

# helpful stuff on resizing loop-mounted partitions, etc here:
# https://superuser.com/questions/1373289/how-do-i-shrink-the-partition-of-an-img-file-made-from-dd
# https://www.raspberrypi.org/forums/posting.php?mode=quote&f=66&p=977050&sid=a026d0f0528381944d4716cb0793d6a9
# https://raspberrypi.stackexchange.com/a/56623/38978
# https://unix.stackexchange.com/a/215354/150012

declare loop_device="/dev/loop0"
#declare loop_device="/dev/loop130"
loop_device=$(sudo losetup -f) # find an unused loop device
echo "using loop device ${loop_device}"

declare -i native=0
if [ -e /etc/os-release ]; then
	#native=$(detect_linux_variant | grep -ic rasp)
	native=$(cat /etc/os-release | grep -ic rasp || /bin/true)
fi
if [ $native -ne 0 ]; then
	echo "running natively"
else
	# https://wiki.archlinux.org/title/QEMU#Chrooting_into_arm/arm64_environment_from_x86_64
	if [ -x /usr/bin/qemu-arm-static ]; then
		native=1
	fi
	if [ -e /proc/sys/fs/binfmt_misc/qemu-arm ]; then
		native=1
	fi
	if [ $native -ne 0 ]; then
		echo "running via qemu-arm-static"
	else
		echo "not running natively"
		echo "consider installing qemu-arm-static with:"
		echo "sudo apt install -y qemu-user-static"
	fi
fi

function unmount_unloop_inner {
	#lsof | grep "/media/boot" || /bin/true
	#lsof | grep "/media/root" || /bin/true
	sudo umount /media/boot/ || /bin/true
	sudo umount /media/root/ || /bin/true
	if [ ${should_add_a_third_partition} -gt 0 ]; then
		#lsof | grep "/media/home" || /bin/true
		sudo umount /media/home/ || /bin/true
	fi
	sudo losetup --detach ${loop_device} || /bin/true
}

function unmount_unloop {
	local -i keep_quiet=${1}
	if [ $keep_quiet -gt 0 ]; then
		unmount_unloop_inner 2>/dev/null
	else
		if [ ${should_add_a_third_partition} -gt 0 ]; then
			echo "unmounting boot, root, home..."
		else
			echo "unmounting boot, root..."
		fi
		unmount_unloop_inner
	fi
}

function fix_dns_resolve {
	declare resolvedcount=$(grep -c "127.0.0.53" /media/root/etc/resolv.conf || /bin/true)
	if [ $resolvedcount -lt 1 ]; then
		echo "nameserver 127.0.0.53" | sudo tee -a /media/root/etc/resolv.conf >/dev/null
		#cat /media/root/etc/resolv.conf
	fi
}

function update_and_install_new_packages {
	sudo sed -i 's,raspbian.raspberrypi.org/raspbian,mirrordirector.raspbian.org/raspbian,' /media/root/etc/apt/sources.list
	local package_list="vim git ntp tmux mlocate subversion rsync nfs-common"
	package_list="$package_list mdadm lvm2 nfs-kernel-server smartmontools"
	package_list="$package_list python3-picamera"
	if [ $native -gt 0 ]; then
		sudo chroot /media/root apt update
#		sudo chroot /media/root apt upgrade -y
		sudo chroot /media/root apt install -y $package_list
#		sudo chroot /media/root apt install -y raspinfo rpi.gpio-common raspi-gpio python-rpi.gpio python3-rpi.gpio python3-gpiozero python-gpiozero python3-spidev python-spidev i2c-tools spi-tools python3-picamera python-picamera u-boot-rpi rpiboot lm-sensors lshw wiringpi libpigpio-dev pigpio-tools python-pigpio python3-pigpio
#		sudo chroot /media/root apt-get clean
#		sudo chroot /media/root apt-get -y autoremove
	else
		echo "install $package_list"
	fi
}

if [ $# -lt 2 ]; then
	echo "usage:"
	echo "$0 2020-08-20-raspios-buster-armhf-lite.img hostname"
	echo "and it will generate a custom image \"2020-08-20-raspios-buster-armhf-lite.hostname.img\" from that"
	exit 1
fi
sudo mkdir -p /media/boot /media/root
if [ ${should_add_a_third_partition} -gt 0 ]; then
	sudo mkdir -p /media/home
fi
declare original_image="$1"
declare hostname="$2"
declare modified_image=$(echo $original_image | sed -e "s,\.img$,.$hostname.img,")
modified_image=$(basename "$modified_image")
#echo "$modified_image"
declare -i GID=$(getent passwd $USER | sed -e "s,$USER:x:\([0-9]\+\):\([0-9]\+\):.*,\2,")
#echo "GID is $GID"
declare GROUP=$(grep ":x:$GID:" /etc/group | sed -e "s,\([^:]\):.*,\1,")
#echo "GROUP is $GROUP"

unmount_unloop 1
if [ ! -e $modified_image ]; then
	echo "copying original..."
	cp -a $original_image $modified_image
fi
#ls -lart $modified_image

if [ ${should_add_a_third_partition} -gt 0 ]; then
	declare -i imagesize=$(du --bytes $modified_image | awk '{ print $1 }')
	if [ $imagesize -lt $wholeimagesize_intended ]; then
		echo "expanding image..."
		sudo dd bs=1M seek=$((wholeimagesize_intended/1000000)) of=$modified_image </dev/null
	fi
	#ls -lart $modified_image
fi

sudo losetup --partscan ${loop_device} $modified_image
lsblk ${loop_device}

if [ ${should_add_a_third_partition} -gt 0 ]; then
	declare -i partitioncount=$(lsblk ${loop_device} | grep -c loop0p)
	if [ $partitioncount -lt 3 ]; then
		declare -i partition1size_current=$(lsblk ${loop_device} --bytes | grep loop0p1 | awk '{ print $4 }')
		declare -i partition2size_current=$(lsblk ${loop_device} --bytes | grep loop0p2 | awk '{ print $4 }')
		if [ $partition2size_current -lt $((partition2size_intended)) ]; then
			echo "resizing partition..."
			declare -i partition2end=$(( (partition2size_intended+partition1size_current)/1000000))
			sudo parted ${loop_device} resizepart 2 $partition2end
			sudo e2fsck -f ${loop_device}p2
			sudo resize2fs ${loop_device}p2
		fi
		echo "adding home partition..."
		sudo parted ${loop_device} mkpart primary $partition2end 100%
		lsblk ${loop_device}
		echo "creating ext4 filesystem for /home partition..."
		sudo mkfs.ext4 ${loop_device}p3
	fi
	echo "mounting boot, root, home..."
	sudo mount ${loop_device}p3 /media/home/
else
	echo "mounting boot, root..."
fi
sudo mount ${loop_device}p1 /media/boot/
sudo mount ${loop_device}p2 /media/root/

if [ -e /media/root/home/pi ]; then
	#echo "moving pi to home..."
	#sudo mv /media/root/home/pi /media/home/
	echo "removing pi account's files..."
	sudo rm -rf /media/root/home/pi
fi

if [ ${should_add_a_third_partition} -gt 0 ]; then
	declare init_resize=$(grep -c init_resize /media/boot/cmdline.txt)
	if [ $init_resize -gt 0 ]; then
		echo "halting automatic partition resize..."
		#cat /media/boot/cmdline.txt
		sudo sed -i -e "s, init=.*,," /media/boot/cmdline.txt
		#cat /media/boot/cmdline.txt
	fi
	if [ -e /media/root/etc/rc3.d/S01resize2fs_once ]; then
		echo "halting automatic filesystem resize..."
		sudo rm /media/root/etc/rc3.d/S01resize2fs_once
	fi
	declare -i homecount=$(grep -c home /media/root/etc/fstab)
	if [ $homecount -eq 0 ]; then
		echo "adding home to fstab..."
		declare line=$(grep boot /media/root/etc/fstab)
		#echo $line
		declare newline=$(echo "$line" | sed -e "s,\(PARTUUID=.*\)-01,\1-03," | sed -e "s,/boot,/home," | sed -e "s,vfat,ext4,")
		#echo $newline
		echo "$newline" | sudo tee -a /media/root/etc/fstab >/dev/null
		#cat /media/root/etc/fstab
	fi
fi

if [ ! -e /media/boot/SSH ]; then
	sudo touch /media/boot/SSH
fi
declare -i londoncount=$(grep -c London /media/root/etc/timezone)
if [ $londoncount -gt 0 ]; then
	echo "setting timezone..."
	#sudo chroot /media/root timedatectl set-timezone "$desired_timezone"
	echo "$desired_timezone" | sudo tee /media/root/etc/timezone >/dev/null
	#cat /media/root/etc/timezone
	#sudo chroot /media/root dpkg-reconfigure -f noninteractive tzdata
	#sudo chroot /media/root/ ln -fs "/usr/share/zoneinfo/$desired_timezone" /etc/localtime
fi
#declare original_hostname=$(grep "^127.0.1.1" /media/root/etc/hosts | awk '{ print $2 }')
declare original_hostname=$(cat /media/root/etc/hostname)
declare -i hostnamecount=$(grep -c "$hostname" /media/root/etc/hostname)
if [ $hostnamecount -eq 0 ]; then
	echo "original hostname: $original_hostname"
	echo "setting hostname to $hostname..."
	echo "$hostname" | sudo tee /media/root/etc/hostname >/dev/null
	# should add self to /etc/hosts (but don't know the ip address ahead of time) - partial workaround:
	sudo sed -i -e "s,^127.0.1.1.*,127.0.1.1\t$hostname," /media/root/etc/hosts
fi
#cat /media/root/etc/hosts
#cat /media/root/etc/hostname
declare -i hostscount=$(grep -c nas /media/root/etc/hosts)
if [ $hostscount -lt 1 ]; then
	grep "nas\|192.168" /etc/hosts | sudo tee -a /media/root/etc/hosts 1>/dev/null
	#cat /media/root/etc/hosts
fi
declare -i ssidcount=$(sudo grep -c ssid /media/root/etc/wpa_supplicant/wpa_supplicant.conf)
if [ $ssidcount -lt 1 ]; then
	sudo bash -c "if [ -e /root/wpa_supplicant.conf ]; then cp -a /root/wpa_supplicant.conf /media/root/etc/wpa_supplicant/; fi"
fi

if [ $native -gt 0 ]; then
	# https://raspberrypi.stackexchange.com/a/47958/38978
	# https://raspberrypi.stackexchange.com/a/66939/38978
	declare -i localecount=$(grep -c "$desired_locale" /media/root/etc/default/locale)
	if [ $localecount -lt 1 ]; then
		sudo chroot /media/root raspi-config nonint do_change_locale "$desired_locale"
	fi
	declare -i keyboardcount=$(grep -c "$desired_keyboard" /media/root/etc/default/keyboard)
	if [ $keyboardcount -lt 1 ]; then
		sudo chroot /media/root raspi-config nonint do_configure_keyboard "$desired_keyboard"
	fi
else
	echo "detected cross-platform situation; you must manually do the following:"
	echo "fix the locale"
	echo "fix the keyboard"
	echo "delete the pi user"
	echo "delete the pi group"
	echo "add your own group"
	echo "add your own user"
fi
declare -i fstabcount1=$(grep -c nas /etc/fstab)
if [ $fstabcount1 -gt 0 ]; then
	declare -i fstabcount2=$(grep -c nas /media/root/etc/fstab)
	if [ $fstabcount2 -eq 0 ]; then
		grep "nas" /etc/fstab | sudo tee -a /media/root/etc/fstab 1>/dev/null
		#cat /media/root/etc/fstab
	fi
	declare -i fstabcount3=$(grep -c nas /media/root/etc/fstab)
	if [ $fstabcount3 -gt 0 ]; then
		cd /media/root
		sudo mkdir -p $(grep nas /media/root/etc/fstab | awk '{ print "/media/root"$2 }')
		cd -
	fi
fi
if [ $native -gt 0 ]; then
	declare piusercount=$(grep -c "^pi" /media/root/etc/passwd)
	if [ $piusercount -gt 0 ]; then
		sudo chroot /media/root deluser pi
	fi
	declare pigroupcount=$(grep -c ":pi\|,pi" /media/root/etc/group)
	if [ $pigroupcount -gt 0 ]; then
		sudo chroot /media/root delgroup pi
	fi
	declare groupcount=$(grep -c ":x:$GID:" /media/root/etc/group || /bin/true)
	if [ $groupcount -lt 1 ]; then
		echo "adding group $GROUP ($GID)..."
		sudo chroot /media/root groupadd --gid $GID $GROUP
	fi
	declare -i usercount=$(grep -c $USER /media/root/etc/passwd)
	if [ $usercount -lt 1 ]; then
		echo "adding user $USER..."
		sudo chroot /media/root useradd --create-home --uid $UID --gid $GID --no-user-group --groups adm,sudo,dialout,cdrom,video,plugdev,staff,games,input,netdev,audio,users,spi,i2c,gpio $USER
	fi
fi
declare -i shadowcount=$(sudo grep -c "^${USER}:\\!:" /media/root/etc/shadow)
if [ $shadowcount -gt 0 ]; then
	sudo sed -i "s/^${USER}:.*//" /media/root/etc/shadow
fi
sudo sh -c 'grep "^'${USER}':" /etc/shadow >> /media/root/etc/shadow'

declare NEWHOME
if [ ${should_add_a_third_partition} -gt 0 ]; then
	NEWHOME="/media/home"
else
	NEWHOME="/media/root/home"
fi
if [ -e "${HOME}/build/${USER}" ] && [ ! -e "${HOME}/build/${USER}-home.tar.bz2" ]; then
	cd "${HOME}/build/"
	tar cjf "${USER}-home.tar.bz2" "${USER}/"
fi
#if [ -e "${HOME}/build/${USER}-home.tar.bz2" ] && [ ! -e "${NEWHOME}/${USER}" ]; then
if [ -e "${HOME}/build/${USER}-home.tar.bz2" ]; then
	cd "${NEWHOME}"
	sudo tar xjf ${HOME}/build/${USER}-home.tar.bz2
	sudo chown -R $USER:$GID "${NEWHOME}/${USER}"
fi

fix_dns_resolve
update_and_install_new_packages

echo "all good"
df --block-size=1000000 | grep "^Filesystem\|${loop_device}"
sync
sleep 1
unmount_unloop 0

echo "image is ready to burn (doublecheck the "of=" below!):"
echo "time nice sudo dd bs=1M if=$modified_image of="

# current issues:
#perl: warning: Setting locale failed.
#perl: warning: Please check that your locale settings:
#        LANGUAGE = (unset),
#        LC_ALL = (unset),
#        LANG = "en_US.UTF-8"
#    are supported and installed on your system.
#perl: warning: Falling back to the standard locale ("C").
#/usr/lib/raspi-config/init_resize.sh
#/etc/init.d/resizefs_once

