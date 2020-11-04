#!/bin/bash -e

# written 2020-10-28 by mza
# last updated 2020-11-04 by mza

declare hostname="pi#7-rpi0w"
declare device="/dev/sdd"
declare wpa_supplicant="/root/wpa_supplicant.conf"

sudo mkdir -p /media/boot
sudo mount ${device}1 /media/boot

sudo mkdir -p /media/root
sudo mount ${device}2 /media/root

# enable ssh (warning: change default password for user "pi"):
sudo touch /media/boot/SSH

sudo mkdir /media/root/root/build
#sudo git clone https://github.com/mzandrew/eink-clock.git /media/root/root/build/eink-clock

#function rc_local_insert {
	#sudo sed -ie '/'$1'/{h;s/.*/'$2'/};${x;/^$/{s/.*/'$2'/;H};x}' /media/root/etc/rc.local
#	sudo sed -ie 's/^exit 0$//;' /media/root/etc/rc.local
#}
#rc_local_insert 'eink-clock' 'nice /root/build/eink-clock/clock.py \&'
#nice /root/build/led-matrix-clock/clock.py &

sudo cp -a $wpa_supplicant /media/root/etc/wpa_supplicant/wpa_supplicant.conf || /bin/true

echo "$hostname" | sudo tee /media/root/etc/hostname

sudo mkdir -p /etc/NetworkManager/conf.d
echo "[connection]
wifi.mac-address-randomization=1
[device]
wifi.scan-rand-mac-address=no
" | sudo tee /etc/NetworkManager/conf.d/100-disable-wifi-mac-randomization.conf

sync

sudo umount /media/boot
sudo umount /media/root

