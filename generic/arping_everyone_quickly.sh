#!/bin/bash -e

# written by mza
# last updated 2020-03-16 by mza

#for i in $(seq 2 253); do sleep 1; ping -c1 -w1 192.168.10.$i >/dev/null; echo "$i $?"; done

declare baseip="192.168.10"
declare device=$(ifconfig  | grep "inet " -B 1 | grep $baseip -B 1 | grep -v inet | awk '{ print $1 }' | sed -e "s,:$,,")
#echo "using $device"
declare self=$(ifconfig $device | grep "inet " | sed -e "s,[ ]\+inet $baseip.\([0-9]\+\) .*,\1,")
#echo "I am ${baseip}.${self}"
declare dir="/tmp"

function go {
	local ip="$1"
	#echo "ip=$1"
	if [ ! "$ip" == "$baseip.$self" ]; then
		arping -c1 -w1 $ip -I$device >/dev/null && echo > "$dir/$ip" || /bin/true
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
	go "$baseip.$i" &
	#echo -n "$i "
done
sleep 2
ls -lart "$dir/$baseip"*
rm -rf "$dir"

