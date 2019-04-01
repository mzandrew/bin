#!/bin/bash -e

declare u=$1
declare g=${2:-idlab}

if [ -z "$u" ]; then
	echo "usage:"
	echo "$0 user [group]"
	exit 1
fi

echo "creating user $u with primary group $g..."
sudo adduser --no-user-group -g $g -m $u 2>/dev/null || sudo adduser -g $g -m $u
id $u
ls -lartd /home/$u

echo; echo "sudo passwd $u"

