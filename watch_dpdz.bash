#!/bin/bash
# This script plots the pressure gradient that enforces U_b=1 over time

# HEADER
out=dpdz
search=volflow
log="$1"

# check correct usage
if [ $# -ne 1 ]
then
	echo "Usage: $0 <logfile>"
	exit 1
fi

# MAIN PROGRAM
# extract only lines with volflow
# and substitute multiple whitespaces with only on
grep "$search" "$log" | sed 's/  */ /g' > "$out"


# plot with gnuplot
gnuplot -e "set terminal dumb; plot '$out' using 2:4 with lines; pause -1 'Hit Return to continue'" 
