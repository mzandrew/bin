#!/bin/bash -e

# last updated 2025-01-26 by mza

declare tarfilebase="$1"
if [ -z "$tarfilebase" ]; then
	echo "ERROR:  must specify a base filename for the tarfiles on the command line"
	exit 1
fi

declare -i count
declare tarfile

tarfile="$tarfilebase.modified.tar"
count=0
if [ -e "$tarfile" ]; then
	echo "ERROR:  file \"$tarfile\" already exists"
	exit 2
fi
svn status | grep ^M | sed -e "s,^M       ,," | while read file; do
	#echo "$file"
	ls -lartd "$file"
	if [ $count -eq 0 ]; then
		tar cf "$tarfile" "$file"
	else
		tar rf "$tarfile" "$file"
	fi
	count=$((count+1))
done
oldtarfile="$tarfile"

tarfile="$tarfilebase.question-mark.tar"
count=0
if [ -e "$tarfile" ]; then
	echo "ERROR:  file \"$tarfile\" already exists"
	exit 2
fi
svn status | grep ^? | sed -e "s,^?       ,," | while read file; do
	#echo "$file"
	if [ "$file" = "$oldtarfile" ]; then
		continue
	fi
	ls -lartd "$file"
	if [ $count -eq 0 ]; then
		tar cf "$tarfile" "$file"
	else
		tar rf "$tarfile" "$file"
	fi
	count=$((count+1))
done

