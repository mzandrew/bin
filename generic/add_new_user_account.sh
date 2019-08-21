#!/bin/bash -e

declare name=$1
declare group=$2
#declare group=${2:-idlab}
declare uid=$3

if [ -z "$name" ]; then
	echo "usage:"
	echo "$0 user group uid"
	exit 1
fi

echo "creating user $name with primary group $group and uid=$uid..."
sudo adduser --no-user-group --gid $group --create-home $name --uid $uid
# 2>/dev/null || sudo adduser -g $g -m $u
id $name
ls -lartd /home/$name

echo; echo "sudo passwd $name"

