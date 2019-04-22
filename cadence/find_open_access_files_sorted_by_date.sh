#!/bin/bash -e

find -type f -name "*.oa" -printf "%TY-%Tm-%Td+%TH:%TM %12s %p\n" | sort -n

