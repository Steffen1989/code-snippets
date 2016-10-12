#!/usr/bin/env python3.5
# This script is intended to give a distribution for points in wall-normal direction
# Steffen Straub
# 2016-10-12

import numpy as np
import sys

if (len(sys.argv) < 4):
    print('Usage:' + sys.argv[0] + ' <start> <end> <number of ELEMENTS> [shrink=0 (default), enlarge=1]')
    sys.exit
else:
    # User input
    start = float(sys.argv[1])
    end = float(sys.argv[2])
    n_el = int(sys.argv[3])  # note that n_pts = n_el + 1
    if (len(sys.argv) == 5):
        shrink = int(sys.argv[4])    # check if elements are getting smaller or larger from start to end
    else:
        shrink = 0


    # Calculations
    n_pts = n_el + 1
    pts = np.zeros(n_pts)
    pts_ref = pts.copy()
    k = 0
    for i in np.linspace(0,1,n_pts):
        if (shrink == 0):
            pts_ref[k] = np.sin(np.pi/2*i)
        else:
            pts_ref[k] = -(np.sin(np.pi/2*(1+i)) - 1)
        k = k+1
    delta = end - start
    # shift and stretch
    pts = pts_ref*delta + start


    # Output
    # concatenate all pts with ' ' separator
    print(' '.join('{:f}'.format(p) for p in pts))
