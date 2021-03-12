#!/bin/bash -e

#if [ -z "$list" ]; then
#	echo "nothing to do"
#	exit 0
#fi
#echo $(echo "$list")

declare dir="/root/passwords"
mkdir -p "$dir"

function passgen6416 {
	openssl rand -base64 16
}

for line in $(grep ":!!!:" /etc/shadow); do
	user=$(echo "$line" | sed -e "s,^\([a-zA-Z0-9]\+\):.*,\1,")
	filename="$dir/$user"
	echo "$user"
	passgen6416 > "$filename"
	cat "$filename" | sed -e "s,\(.*\),$user:\1," | chpasswd --crypt-method SHA512
done

