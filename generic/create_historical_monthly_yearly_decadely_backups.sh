#!/bin/bash -e

# written 2018-06-15 by mza
# last updated 2018-06-26 by mza

declare destination source

if [ $UID -gt 0 ]; then
	echo "use sudo to run this script:"
	echo "sudo $0"
	exit 1
fi

declare configfile="/root/.historical_backups"
if [ ! -e "${configfile}" ]; then
	echo "
destination=\"/$hostname-backup-drive\"
source=\"/home\"

" >"${configfile}"
	echo "check contents of file $configfile and run this script again"
	exit 0
fi

. "${configfile}"

declare userlist=""
declare userlist_temp=$(ls -1 "$source")
for each in $userlist_temp; do
	if [ $each = "lost+found" ]; then continue; fi
	if [ -e "$source/$each" ] && [ -d "$source/$each" ]; then
		userlist="$userlist $each"
	fi
done
echo "operating on: $userlist"
declare -i num count maxcount=150
declare fulllistingfile listingfile startyear endyear datestamp
declare temporarylistingfile="$destination/temporary.lf-r"

function lf {
	#nice find -name "simulation" -prune -o -name ".git" -prune -o -name ".svn" -prune -o -type f -printf "%TY-%Tm-%Td+%TH:%TM %12s %p\n" | sort -n -k 1
	nice find -name ".git" -prune -o -name ".svn" -prune -o -type f -printf "%TY-%Tm-%Td+%TH:%TM %12s %p\n" | sort -n -k 1
}

function decadely {
	num=0
	count=0
	for yyy in $(seq $((startyear/10)) $((endyear/10))); do
		nice grep "^$yyy" "$fulllistingfile" > "$temporarylistingfile" || /bin/true
		num=$(wc "$temporarylistingfile" | awk '{print $1}')
		if [ $num -gt 0 ]; then
			tarfilename="${destination}/${yyy}0s.${user}.tar"
			if [ ! -e "$tarfilename" ] && [ ! -e "${tarfilename}.bz2" ]; then
				echo "$tarfilename $num"
				listingfile="${tarfilename}.lf-r"
				mv "$temporarylistingfile" "$listingfile" 
				nice cat "$listingfile" | sed -e "s,\([^ ]*\)[ ]*\([^ ]*\)[ ]*,," > "$temporarylistingfile"
				datestamp=$(tail -n1 "$listingfile" | awk '{print $1}' | sed -e "s,+, ,")
				nice tar -cf "$tarfilename" --files-from="$temporarylistingfile" || rm -f "$tarfilename"
				if [ -e "$tarfilename" ]; then
					touch "$tarfilename" "$listingfile" --date="$datestamp"
				fi
				count=$((count+1))
			fi
			if [ $count -ge $maxcount ]; then
				exit 0
			fi
		fi
	done
}

function yearly {
	num=0
	count=0
	for year in $(seq $startyear $endyear); do
		nice grep "^$year" "$fulllistingfile" > "$temporarylistingfile" || /bin/true
		num=$(wc "$temporarylistingfile" | awk '{print $1}')
		if [ $num -gt 0 ]; then
			tarfilename="${destination}/$year/${year}.${user}.tar"
			if [ ! -e "$tarfilename" ] && [ ! -e "${tarfilename}.bz2" ]; then
				echo "$tarfilename $num"
				listingfile="${tarfilename}.lf-r"
				mv "$temporarylistingfile" "$listingfile" 
				nice cat "$listingfile" | sed -e "s,\([^ ]*\)[ ]*\([^ ]*\)[ ]*,," > "$temporarylistingfile"
				datestamp=$(tail -n1 "$listingfile" | awk '{print $1}' | sed -e "s,+, ,")
				nice tar -cf "$tarfilename" --files-from="$temporarylistingfile" || rm -f "$tarfilename"
				if [ -e "$tarfilename" ]; then
					touch "$tarfilename" "$listingfile" --date="$datestamp"
				fi
				count=$((count+1))
			fi
			if [ $count -ge $maxcount ]; then
				exit 0
			fi
		fi
	done
}

declare THISMONTH=$(date +"%Y-%m")
function monthly {
	num=0
	count=0
	for year in $(seq $startyear $endyear); do
		for month in $(seq 01 12); do
			month=$(printf "%02d" $month)
			yyyymm="$year-$month"
			if [ $yyyymm == $THISMONTH ]; then
				continue
			fi
			nice grep "^$yyyymm" "$fulllistingfile" > "$temporarylistingfile" || /bin/true
			num=$(wc "$temporarylistingfile" | awk '{print $1}')
			if [ $num -gt 0 ]; then
				mkdir -p "${destination}/$year"
				tarfilename="${destination}/$year/${yyyymm}.${user}.tar"
				if [ ! -e "$tarfilename" ] && [ ! -e "${tarfilename}.bz2" ]; then
					echo "$tarfilename $num"
					listingfile="${tarfilename}.lf-r"
					mv "$temporarylistingfile" "$listingfile" 
					nice cat "$listingfile" | sed -e "s,\([^ ]*\)[ ]*\([^ ]*\)[ ]*,," > "$temporarylistingfile"
					datestamp=$(tail -n1 "$listingfile" | awk '{print $1}' | sed -e "s,+, ,")
					nice tar -cf "$tarfilename" --files-from="$temporarylistingfile" || rm -f "$tarfilename"
					if [ -e "$tarfilename" ]; then
						touch "$tarfilename" "$listingfile" --date="$datestamp"
					fi
					count=$((count+1))
				fi
				if [ $count -ge $maxcount ]; then
					exit 0
				fi
			fi
		done
	done
}

for user in $userlist; do
	cd "$source/$user"
	pwd
	mkdir -p "$destination/files-lists"
	fulllistingfile="$destination/files-lists/${user}.lf-r"
	if [ -e "$fulllistingfile" ]; then
		rm "$fulllistingfile"
	fi
	if [ ! -e "$fulllistingfile" ]; then
		lf > "$fulllistingfile"
	fi
	startyear=$(head -n1 "$fulllistingfile" | colrm 5)
	endyear=$(tail -n1 "$fulllistingfile" | colrm 5)
	#echo "$startyear $endyear"
	
	#startyear=1970
	#endyear=2008
	#decadely
	
	#startyear=2009
	#endyear=2017
	#yearly
	
	#startyear=2015
	#endyear=2100
	monthly
	
	rm -f "$temporarylistingfile"
done

