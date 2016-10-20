#!/usr/bin/env python3.5
# This python script can be used to approximate the total memory requirements 
# for a nek5000 simulation.
# See chapter 3.2.1 of the nek5000 user guide
# Steffen Straub
# 2016-10-20

import numpy as np
import sys
import pdb
if (len(sys.argv) < 3):
    print('Usage:' + sys.argv[0] + ' <number of elements> <polynomial order>')
    sys.exit
else:
    nel = int(sys.argv[1]) # number of elements
    p = int(sys.argv[2]) # polynomial order
    mem_mb = (nel*(p+1)**3*400*8)/1e6 # memory requirements per processor in MB
    print('Memory Requirements [MB]: {:f}'.format(mem_mb))

