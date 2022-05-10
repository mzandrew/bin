#!/bin/bash -e

# written by mza
# last updated 2022-05-10 by mza

#for i in $(seq 2 253); do sleep 1; ping -c1 -w1 192.168.10.$i >/dev/null; echo "$i $?"; done

declare baseip="192.168"

declare devices=$(ifconfig  | grep "inet " -B 1 | grep $baseip -B 1 | grep -v inet | awk '{ print $1 }' | sed -e "s,:$,," | grep -v "\-\-")
declare device=$(echo "$devices" | head -n1)
echo "using device \"$device\""
declare self=$(ifconfig $device | grep "inet $baseip" | sed -e "s,[ ]\+inet \([0-9.]\+\) .*,\1,")
echo "I am \"${self}\""
baseip=$(ifconfig $device | grep "inet $baseip" | sed -e "s,[ ]\+inet \([0-9.]\+\)\.[0-9]\+ .*,\1,")
echo "baseip is \"${baseip}\""
declare dir="/tmp"

which arping >/dev/null || echo -e "arping not found.  try:\n  sudo apt install -y arping" && exit 1

# this lets it update the arp table:
echo 1 | sudo tee /proc/sys/net/ipv4/conf/${device}/arp_accept >/dev/null

function go {
	local ip="$1"
	#echo "ip=$1"
	if [ ! "$ip" == "$self" ]; then
		arping -c1 -w1 $ip -I$device > "${dir}/${ip}" || rm "${dir}/${ip}"
	fi
}

declare default_range="1 254"
declare range=$default_range
if [ $# -eq 2 ]; then
	range="$1 $2"
	echo "custom range: ${baseip}.${1} to ${baseip}.${2}"
#"${1:-$default_range}"
#range="40 50"
fi
dir=$(mktemp -d)

for i in $(seq $range); do
	sleep 0.01
	go "${baseip}.${i}" &
	#echo -n "$i "
done
sleep 2
sync
sleep 1
find "$dir" -type f | sed -e "s,.*/\(${baseip}\.\)\([0-9]\+\).*,\2 \1\2," | sort -n  | awk '{ print $2 }'
echo "$dir"
arp | sort
#rm -rf "$dir"

