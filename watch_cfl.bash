#!/bin/bash
# This script reads the the Nek5000 logfiles,
# extracts only the cfl number and step number 
# so that they can be plotted with gnuplot
# Input1: path to original logfile
# Input2: path to stripped logfile
#xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
# Author: Steffen Straub
# Date: 2016-11-28
#xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
#set -x

scriptname=$(basename "$0")

# check if both input arguments are given
if [ $# -ne 2 ]
	then
		echo "Usage: $scriptname <path to original logfile> <path to stripped logfile>"
		exit 1
	else
		input="$1"
		output="$2"
		# skip first lines until "Starting time"
		# only lines containing tep
		# make all whitespaces ' '
		# only show 8th field
		sed '1,/Starting\stime/d' "$input" | grep tep | sed 's/\s\s*/ /g' | cut -d ' ' -f 8 > "$output"

		gnuplot -e "plot'$output'; pause -1 'Hit return to continue'"
fi	
