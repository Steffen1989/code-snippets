#!/usr/bin/env python3.5
# Script to calculate the mean of an array of numbers
#xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
# Author: Steffen Straub
# Date: 2017/07/04
#xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
import numpy as np
import sys


# Check if logfile is given
if (len(sys.argv) != 2):
	print('Usage: {0:s} <path to logfile>'.format(sys.argv[0]))
	sys.exit(1)


# Read logfile
step = []
f = open(sys.argv[1], 'r')
for line in f:
	# only lines containing "Step"
	if ("Step" in line):
		step.append(line)
f.close()

# Convert to numpy array
ar = np.asarray(step)
# Only from steps 30 to 95
ar = ar[30:-8]
# Split string
ar = np.core.defchararray.rsplit(ar)
# Keep only the time/timestep
times = np.zeros(len(ar))
for i in range(0,len(ar)):
	times[i] = ar[i][-1]

# Average over all 65 
mean = np.mean(times)
print('The mean time/timestep is {0:10.5f}s'.format(mean))

f = open('mean_t.dat', 'w')
# Convert to string
#s = str(mean)
f.write('{0:10.5f}\n'.format(mean))
f.close()

## read data file
#
#f = open('timestats.out', 'r')
#numbers = f.readlines()
#f.close()
#
## convert to numpy array
#num_ar = np.asarray(numbers)
#
## number of elements in array
#n_total = len(num_ar)
#
## create empty numpy array
#ar = np.zeros(n_total)
#
## loop over all elements and cut of trailing '\n'
#for i in range(0, n_total):
#	ar[i] = num_ar[i][:-1]
#
## calculate the mean
#mean = np.mean(ar)
#
#print('The mean time/timestep is {0:10.5f}s'.format(mean)):wq
