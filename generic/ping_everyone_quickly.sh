#!/bin/bash -e

#for i in $(seq 2 253); do sleep 1; ping -c1 -w1 192.168.10.$i >/dev/null; echo "$i $?"; done

# last updated 2020-12-11 by mza

#declare baseip="192.168.10"
declare baseip=$(ifconfig | grep inet | grep 192.168 | awk '{ print $2 }' | sed -e "s,addr:,," | sed -e "s,\.[0-9]\+$,," | head -n1)
echo "using $baseip"
declare dir=$(mktemp -d)

function go {
	local ip="$1"
	#echo "ip=$1"
	ping -c1 -w1 $ip >/dev/null && echo > "$dir/$ip" || /bin/true
}

declare -i first=1
declare -i last=254
if [ $# -gt 1 ]; then
	first=$1
	last=$2
fi
#echo "$first $last"
for i in $(seq $first $last); do
	go "$baseip.$i" &
done
sleep 2
#ls -la "$dir/$baseip"* | sort -k9n
ls -la "$dir/$baseip"*
rm -rf "$dir"

