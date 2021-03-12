#!/bin/bash -e

# written 2020-11-21 by mza
# last updated 2020-11-26 by mza

declare desired_locale="en_US.UTF-8"
declare desired_keyboard="us"
declare desired_timezone="Pacific/Honolulu"

# helpful stuff on resizing loop-mounted partitions, etc here:
# https://superuser.com/questions/1373289/how-do-i-shrink-the-partition-of-an-img-file-made-from-dd
# https://www.raspberrypi.org/forums/posting.php?mode=quote&f=66&p=977050&sid=a026d0f0528381944d4716cb0793d6a9
# https://raspberrypi.stackexchange.com/a/56623/38978
# https://unix.stackexchange.com/a/215354/150012

function unmount_unloop {
	sudo umount /media/boot/ 2>/dev/null || /bin/true
	sudo umount /media/root/ 2>/dev/null || /bin/true
	sudo umount /media/home/ 2>/dev/null || /bin/true
	sudo losetup --detach /dev/loop0 2>/dev/null || /bin/true
}

function update_and_install_new_packages {
	sudo chroot /media/root apt update
#	sudo chroot /media/root apt upgrade -y
	sudo chroot /media/root apt install -y vim git ntp tmux mlocate subversion rsync nfs-common
#	sudo chroot /media/root apt install -y raspinfo rpi.gpio-common raspi-gpio python-rpi.gpio python3-rpi.gpio python3-gpiozero python-gpiozero python3-spidev python-spidev i2c-tools spi-tools python3-picamera python-picamera u-boot-rpi rpiboot lm-sensors lshw wiringpi libpigpio-dev pigpio-tools python-pigpio python3-pigpio
#	sudo chroot /media/root apt-get clean
#	sudo chroot /media/root apt-get -y autoremove
}

if [ $# -lt 2 ]; then
	echo "usage:"
	echo "$0 2020-08-20-raspios-buster-armhf-lite.img hostname"
	echo "and it will generate a custom image \"2020-08-20-raspios-buster-armhf-lite.hostname.img\" from that"
	exit 1
fi
sudo mkdir -p /media/boot /media/root /media/home
declare original_image="$1"
declare hostname="$2"
declare modified_image=$(echo $original_image | sed -e "s,\.img$,.$hostname.img,")
#echo "$modified_image"
declare -i GID=$(getent passwd $USER | sed -e "s,$USER:x:\([0-9]\+\):\([0-9]\+\):.*,\2,")

set -x
declare -i wholeimagesize_intended=4000000000
declare -i partition2size_intended=3500000000
unmount_unloop
if [ ! -e $modified_image ]; then
	echo "copying original..."
	cp $original_image $modified_image
fi
#ls -lart $modified_image
declare -i imagesize=$(du --bytes $modified_image | awk '{ print $1 }')
if [ $imagesize -lt $wholeimagesize_intended ]; then
	echo "expanding image..."
	sudo dd bs=1M seek=$((wholeimagesize_intended/1000000)) of=$modified_image </dev/null
fi
#ls -lart $modified_image
sudo losetup --partscan /dev/loop0 $modified_image
lsblk /dev/loop0
declare -i partitioncount=$(lsblk /dev/loop0 | grep -c loop0p)
if [ $partitioncount -lt 3 ]; then
	declare -i partition1size_current=$(lsblk /dev/loop0 --bytes | grep loop0p1 | awk '{ print $4 }')
	declare -i partition2size_current=$(lsblk /dev/loop0 --bytes | grep loop0p2 | awk '{ print $4 }')
	if [ $partition2size_current -lt $((partition2size_intended)) ]; then
		echo "resizing partition..."
		declare -i partition2end=$(( (partition2size_intended+partition1size_current)/1000000))
		sudo parted /dev/loop0 resizepart 2 $partition2end
		sudo e2fsck -f /dev/loop0p2
		sudo resize2fs /dev/loop0p2
	fi
	echo "adding home partition..."
	sudo parted /dev/loop0 mkpart primary $partition2end 100%
	lsblk /dev/loop0
	echo "creating ext4 filesystem for /home partition..."
	sudo mkfs.ext4 /dev/loop0p3
fi
echo "mounting boot, root, home..."
sudo mount /dev/loop0p1 /media/boot/
sudo mount /dev/loop0p2 /media/root/
sudo mount /dev/loop0p3 /media/home/
if [ -e /media/root/home/pi ]; then
	#echo "moving pi to home..."
	#sudo mv /media/root/home/pi /media/home/
	echo "removing pi account's files..."
	sudo rm -rf /media/root/home/pi
fi
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
	sudo chroot /media/root/ ln -fs "/usr/share/zoneinfo/$desired_timezone" /etc/localtime
fi
declare -i hostnamecount=$(grep -c $hostname /media/root/etc/hostname)
if [ $hostnamecount -eq 0 ]; then
	echo "setting hostname..."
	echo "$hostname" | sudo tee /media/root/etc/hostname >/dev/null
fi
declare -i ssidcount=$(sudo grep -c ssid /media/root/etc/wpa_supplicant/wpa_supplicant.conf)
if [ $ssidcount -lt 1 ]; then
	sudo bash -c "if [ -e /root/wpa_supplicant.conf ]; then cp -a /root/wpa_supplicant.conf /media/root/etc/wpa_supplicant/; fi"
fi

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
declare piusercount=$(grep -c "^pi" /media/root/etc/passwd)
if [ $piusercount -gt 0 ]; then
	sudo chroot /media/root deluser pi
fi
declare pigroupcount=$(grep -c ":pi\|,pi" /media/root/etc/group)
if [ $pigroupcount -gt 0 ]; then
	sudo chroot /media/root delgroup pi
fi
declare -i usercount=$(grep -c $USER /media/root/etc/passwd)
if [ $usercount -lt 1 ]; then
	echo "adding user $USER..."
	sudo chroot /media/root useradd --uid $UID --gid $GID --no-user-group --groups adm,sudo,dialout,cdrom,video,plugdev,staff,games,input,netdev,audio,users,spi,i2c,gpio $USER
fi
declare -i shadowcount=$(sudo grep -c "^${USER}:\\!:" /media/root/etc/shadow)
if [ $shadowcount -gt 0 ]; then
	sudo sed -i "s/^${USER}:.*//" /media/root/etc/shadow
fi
sudo sh -c 'grep "^'${USER}':" /etc/shadow >> /media/root/etc/shadow'
declare -i hostscount=$(grep -c nas /media/root/etc/hosts)
if [ $hostscount -lt 1 ]; then
	grep "nas\|192.168" /etc/hosts | sudo tee -a /media/root/etc/hosts 1>/dev/null
	#cat /media/root/etc/hosts
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
		sudo chroot /media/root mkdir -p $(grep nas /media/root/etc/fstab | awk '{ print $2 }')
	fi
fi
update_and_install_new_packages

if [ -e ~/build/${USER}-home.tar.bz2 ] && [ ! -e /media/home/${USER} ]; then
	cd /media/home
	sudo tar xjf ~/build/${USER}-home.tar.bz2
	sudo chown -R $USER:$GID "/media/home/${USER}"
fi

echo "all good"
df --block-size=1000000 | grep "^Filesystem\|loop0"
echo "unmounting boot, root, home..."
unmount_unloop

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

