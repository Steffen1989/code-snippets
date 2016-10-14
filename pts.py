#!/usr/bin/env python3.5
# This script is intended to give a distribution for points in wall-normal direction
# Steffen Straub
# 2016-10-12

import numpy as np
import sys
import pdb

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
    # use one more point for now and remove one later
    pts = np.zeros(n_pts+1)
    pts_ref = pts.copy()
    k = 0
    for i in np.linspace(0,1,n_pts+1): 
        if (shrink == 0):
            pts_ref[k] = np.sin(np.pi/2*(i))
        else:
            pts_ref[k] = np.cos(np.pi/2*(i))
        k = k+1
    
    delta = end - start
    if (shrink == 0):
        # remove 1 point in the clustering region
        pts_ref = np.delete(pts_ref, -2)
        pts = pts_ref*delta + start
    else:
        # remove 1 point in the clustering region
        pts_ref = np.delete(pts_ref, 1)
        pts = end - pts_ref*delta



    # Output
    # concatenate all pts with ' ' separator
    print(' '.join('{:f}'.format(p) for p in pts))
