#!/bin/bash -e

#for i in $(seq 2 253); do sleep 1; ping -c1 -w1 192.168.10.$i >/dev/null; echo "$i $?"; done

declare baseip="192.168.10"

function go {
	local ip="$1"
	#echo "ip=$1"
	ping -c1 -w1 $ip >/dev/null && echo > "$dir/$ip" || /bin/true
}

declare dir=$(mktemp -d)
for i in $(seq 1 254); do
	go "$baseip.$i" &
done
sleep 2
ls -lart "$dir/$baseip"*
rm -rf "$dir"

