#!/bin/bash -e

for each in * .*; do
	if [ "$each" == ".." ]; then continue; fi
	if [ "$each" == "." ]; then continue; fi
	#echo "$each"
	if [ -d "$each" ]; then
		echo $each
		tar cf "$each.tar" "$each" && touch --reference="$each" "$each.tar" && rm -rf "$each"
		ls -lart "$each.tar"
	fi
done

