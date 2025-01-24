#!/bin/bash -e

# written 2025-01-24 by mza

# to semi-automatically re-datestamp files that already have a year in their filename:
# find -type f -name "*2017*" -exec rough_touch.sh 2017 "{}" +

# to automatically re-datestamp files that already have a year in their filename:
# for year in $(seq 2010 2025); do find -type f -name "*${year}*" -exec rough_touch.sh $year "{}" +; done

# to automatically re-datestamp files that already have a year in their dirname:
# for year in $(seq 2010 2025); do find -type d -name "*${year}*" -exec rough_touch.sh $year "{}" +; done

declare -i early_year=1900
declare -i current_year=$(date +"%Y")

if [ $# -eq 0 ]; then
	echo "usage: "
	echo "$0 1989 \"file1989.csv\""
	echo "$0 2007 \"taxes (2007)\""
	echo "$0 2020"
	echo "for year in \$(seq 1900 $current_year); do find -type f -name \"*\${year}*\" -exec rough_touch.sh \$year \"{}\" +; done"
	echo "for year in \$(seq 1900 $current_year); do find -type d -name \"*\${year}*\" -exec rough_touch.sh \$year \"{}\" +; done"
	echo "for year in \$(seq 1900 $current_year); do find -name \"*\${year}*\" -exec rough_touch.sh \$year \"{}\" +; done"
	exit 1
fi

declare -i year=$1
if [ $year -lt $early_year ]; then year=$early_year; fi
if [ $year -gt $current_year ]; then year=$current_year; fi
declare year_month_day="${year}-07-01"
#echo "$year_month_day"
shift

if [ $# -gt 0 ]; then
	for each; do
		if [ -d "${each}" ]; then
			#echo "dir $each"
			find "$each" -type f -exec $0 $year "{}" \;
		elif [ -f "${each}" ]; then
			echo "$each"
			touch --date=$year_month_day "$each"
		fi
	done
else
	find . -type f -exec $0 $year "{}" \;
fi

