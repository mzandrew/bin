#!/bin/bash -e

declare portlist=$(netstat -an --inet | grep LISTEN | grep -v 127.0.0.1 | awk '{ print $4 }' | sed -e "s,[^:]\+:\(.*\),\1,")
#echo "$portlist"
for port in $portlist; do
	echo "$port"
	grep " $port/" /etc/services || /bin/true
done

