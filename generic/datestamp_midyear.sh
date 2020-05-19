#/bin/bash -e

declare date="${1}-07-01"
shift
declare target="${@}"
target=$(echo "$target" | sed -e "s,/$,,g")
#echo $date
#echo $target
if [ -e /etc/synoinfo.conf ]; then
	# this is a workaround for a synology diskstation which reverts timestamp changes about 1 second after you make them
	if [ -d "$target" ]; then
		dirname=$(mktemp -d /tmp/BLAMBLAM.XXXXXX)
		rsync -rlpgo "$target/" $dirname/
		find $dirname -name "@eaDir" -prune -o -exec touch --date=$date "{}" \;
		#ls -lart $dirname/
		#sleep 2
		#ls -lart $dirname/
		if [ ! -e "${target}.old" ]; then
			rm -rf "$target"
			#mv "$target" "${target}.old"
			#ls -lart $dirname "${target}.old"
			sleep 1
			mv $dirname "$target"
			#ls -lart "${target}.old" "$target"
			#ls -lart "$target"
			#sleep 1
			#ls -lart "${target}.old" "$target"
			#ls -lart "$target"
		fi
#	elif [ -e "$target" ]; then
		# unfinished
#		filename=$(mktemp /tmp/BLAMBLAM.XXXXXX.tar)
		#tar cf $filename "$target"
	else
		echo "using date=$date"
		echo "can't find $target"
		exit 1
	fi
else
	if [ -d "$target" ]; then
		find "$target" -name "@eaDir" -prune -o -exec touch --date=$date "{}" \;
	elif [ -e "$target" ]; then
		touch --date=$date "$target"
	else
		echo "using date=$date"
		echo "can't find $target"
		exit 1
	fi
fi

#ls -lart "$target"

