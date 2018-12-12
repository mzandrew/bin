#!/bin/bash -e

#for i in $(seq 2 253); do sleep 1; ping -c1 -w1 192.168.10.$i >/dev/null; echo "$i $?"; done

declare baseip="192.168.10"
declare device="${1:-eth6}"
declare self=$(ifconfig $device | grep 'inet addr' | sed -e "s,[ ]\+inet addr:$baseip.\([0-9]\+\) .*,\1,")

function go {
	local ip="$1"
	#echo "ip=$1"
	if [ ! "$ip" == "$baseip.$self" ]; then
		arping -c1 -w1 $ip -I$device >/dev/null && echo > "$dir/$ip" || /bin/true
	fi
}

declare dir=$(mktemp -d)
for i in $(seq 1 254); do
	go "$baseip.$i" &
done
sleep 2
ls -lart "$dir/$baseip"*
rm -rf "$dir"

