#!/bin/bash -e

if [ $UID -gt 0 ]; then
	echo "use sudo to run this script:"
	echo "sudo $0"
	exit 1
fi
declare localdir=$(cd $(dirname $(readlink -f $0)); pwd)

declare date=$(date +"%Y-%m-%d")
declare hostname=$(hostname)
declare configfile="/root/.backup-home-dirs"
if [ ! -e "${configfile}" ]; then
	echo "
destination=\"/$hostname-backup-drive\"

whole_backup \"/home\" \"$hostname\"
#whole_backup \"/opt/shared\" \"$hostname-opt-shared\"

#incremental_backup \"/home\" \"$hostname\"

" >"${configfile}"
	echo "check contents of file $configfile and run this script again"
	exit 0
fi

function whole_backup {
	local sdir="$1"
	local name="$2"
	local ddir="$destination/$name-backup"
	mkdir -p "$ddir"
	cd $sdir
	#du --ma=1 > du-ma1
	for each in *; do
		if [ -d $each ]; then
			file="$ddir/$date.$each.tar"
			if [ -e $file ]; then
				echo "file $file already exists; skipping"
			else
				echo "creating file $file..."
				nice tar cf $file $each
				$localdir/extract-lf-listing-from-tar-file $file
			fi
		fi
	done
}

function incremental_backup {
	local sdir="$1"
	local name="$2"
	local ddir="$destination/$name-backup"
	mkdir -p "$ddir"
	cd $sdir
	#du --ma=1 > du-ma1
	for each in *; do
		if [ -d $each ]; then
			local oldfile=$(find $destination -type f -name "20[0-9][0-9]-[0-9][0-9]-[0-9][0-9].$each.tar" | sort | tail -n1)
			#echo $oldfile
			local newfile="$ddir/$date.$each.tar"
			if [ -e $newfile ]; then
				echo "file $newfile already exists; skipping"
			else
				if [ -e $oldfile ]; then
					echo "creating file $newfile (as an incremental backup relative to $oldfile)..."
					nice tar -c --newer=$oldfile -f $newfile $each
				else
					echo "creating file $newfile..."
					nice tar -c -f $newfile $each
				fi
			fi
			if [ ! -e "${newfile}.lf-r" ]; then
				echo -n "generating listing file for "
				$localdir/extract-lf-listing-from-tar-file $newfile
			fi
		fi
	done
}

. "${configfile}"

