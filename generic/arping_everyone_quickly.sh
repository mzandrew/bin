#!/bin/bash -e

# written by mza
# last updated 2022-05-10 by mza

#for i in $(seq 2 253); do sleep 1; ping -c1 -w1 192.168.10.$i >/dev/null; echo "$i $?"; done

declare rootip="192.168"
declare fake_it=0

which arping >/dev/null || { echo -e "arping not found.  try:\n  sudo apt install -y arping" && exit 1; }
sudo which arping >/dev/null || { echo -e "must run as sudo" && exit 2; }

declare default_range="1 254"
declare range=$default_range
if [ $# -eq 2 ]; then
	range="$1 $2"
	echo "custom range: .${1} to .${2}"
	#echo "custom range: ${baseip}.${1} to ${baseip}.${2}"
#"${1:-$default_range}"
#range="40 50"
fi
declare dir=$(mktemp -d)
declare self="1.1.1.1"

function go {
	local ip="$1"
	#echo "ip=$1"
	if [ ! "$ip" == "$self" ]; then
		sudo arping -c1 -w1 $ip -I${device} > "${dir}/${ip}" || rm "${dir}/${ip}"
	fi
}

declare devices=$(ifconfig  | grep "inet " -B 1 | grep $rootip -B 1 | grep -v inet | awk '{ print $1 }' | sed -e "s,:$,," | grep -v "\-\-")
for device in $devices; do
	echo "using device \"$device\""
	self=$(ifconfig $device | grep "inet $rootip" | sed -e "s,[ ]\+inet \([0-9.]\+\) .*,\1,")
	echo "I am \"${self}\""
	declare baseip=$(ifconfig $device | grep "inet $rootip" | sed -e "s,[ ]\+inet \([0-9.]\+\)\.[0-9]\+ .*,\1,")
	echo "baseip is \"${baseip}\""
	if [ $fake_it -eq 0 ]; then
		# this lets it update the arp table:
		echo 1 | sudo tee /proc/sys/net/ipv4/conf/${device}/arp_accept >/dev/null
		echo -n "sending arping(s)..."
		for i in $(seq $range); do
			sleep 0.01
			go "${baseip}.${i}" &
			#echo -n "$i "
		done
		echo " done"
	fi
done

if [ $fake_it -eq 0 ]; then
	sleep 2
	sync
	sleep 1
	find "$dir" -type f | sort
	#| sed -e "s,.*/\(${baseip}\.\)\([0-9]\+\).*,\2 \1\2," | sort -n  | awk '{ print $2 }'
	echo "$dir"
	arp | sort
	#rm -rf "$dir"
fi

