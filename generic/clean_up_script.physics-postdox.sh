#!/bin/bash -e

find -type f -name "*rawdata.[0-9][0-9][0-9][0-9][0-9]" -exec rm {} \;
find -type f -name "*rawdata.[0-9][0-9][0-9][0-9]" -exec rm {} \;
find -type f -name "*.rawdata[0-9][0-9][0-9]" -exec rm {} \;
find -type f -name "*.pyc" -exec rm {} \;
find -type f -name "*.so" -exec rm {} \;
find -type f -name "*.o" -exec rm {} \;
find -type f -name "*.rawdata" -exec rm {} \;
find -type f -name "*.log" -exec rm {} \;
find -type f -name "*.dat" -exec rm {} \;
find -type f -name "*.camac" -exec rm {} \;
find -type f -name "*.status" -exec rm {} \;
find -type f -name "*~" -exec rm {} \;
find -type f -name "ccc" -exec rm {} \;
find -depth -type d -empty -exec rmdir {} \;

