#!/usr/bin/env python3.5
# This python script is inspired by Nek5000's genbox tool for simple mesh generation
# I want to use it to create a simple mesh for roughness simulations 
# Therefore, periodic boundary conditions and internal BCs need to be prescribed in multiple boxes
#oooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo
# Steffen Straub
# 2016-10-11
#oooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo

# Import modules 
#----------------------------------------------------------------------
import pdb # for debugging

# xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
# Define some functions which we need later on
#----------------------------------------------------------------------

# Function for calculating x/y pts for a given 
# start, end and ratio
#----------------------------------------------------------------------
def calc_pts(start, end, ratio, nel):
    denominator = 0 # initialize
    pts = [start]
    for i in range(0,nel):
        denominator = denominator + ratio**(i)
    L0 = (end - start)/denominator # length of first element
    delta = L0
    for i in range(1, nel):
        pts.append(pts[-1] + delta)
        delta = delta*ratio
    pts.append(end)
    return pts


# Function for writing the mesh in a correct format into .rea file
#---------------------------------------------------------------------- 
def write_mesh(file_obj, xpts, ypts, \
        nelx, nely, n_tot, spatial_dim):
    # write header 
    file_obj.write('{0:10d} {1:10d} {2:10d}'.format(n_tot,spatial_dim,n_tot))
    file_obj.write(' NEL,NDIM,NELV\n')

    # write elements for all blocks
    n_prev = 0  # number of elements in all previous blocks
    for i in range(0,len(nelx)):    # loop through all blocks
        for ely in range(0,nely[i]):    # Loop through all elements
            for elx in range(0,nelx[i]):
                elem_number = elx + ely*nelx[i] + 1 + n_prev
                file_obj.write('{0:>19s} {1:10d} {2:6s}{3:1s}{4:12s}'.format\
                        ('ELEMENT',elem_number,'[    1','a',']  GROUP  0\n'))
                file_obj.write('{0: 10.6f}{1: 14.6f}{2: 14.6f}{3: 14.6f}   {4:s}'.format\
                        (xpts[i][elx],xpts[i][elx+1],xpts[i][elx+1],xpts[i][elx],'\n'))   # x coordinates
                file_obj.write('{0: 10.6f}{1: 14.6f}{2: 14.6f}{3: 14.6f}   {4:s}'.format\
                        (ypts[i][ely],ypts[i][ely],ypts[i][ely+1],ypts[i][ely+1],'\n'))  # y coordinates
        n_prev = n_prev + nelx[i]*nely[i]   # update n_prev


# Function for writing formated text for BCs similar to nek5000 genbox
# format specifications are tuned to mimic genbox.f's behaviour
#----------------------------------------------------------------------
def write_f(file_obj, bc, cur_el, dig_n_tot, f, conn_el, conn_face):
    file_obj.write(' {boundary:3s}{current_el:{digits_n_tot}d} {face:2d}   \
{con_el:<07.1f}{con_f:14.5f}{zero1:14.5f}{zero2:14.5f}{zero3:14.5f}    {newline:s}'\
        .format(boundary=bc, current_el=cur_el, digits_n_tot=dig_n_tot, face=f,\
        con_el=conn_el, con_f=conn_face,\
        zero1=0.0,zero2=0.0,zero3=0.0,newline='\n'))


# Function for finding the corresponding elements and faces to a certain face of
# a userspecified BC
#----------------------------------------------------------------------
def get_con_el_f(i, cor_el_dict, bctype, face, elx, ely, nelx, nely):
        # get number of connected boxes
        conn_boxes = cor_el_dict[bctype[i][1:3]]
        # choose the other box (different from i)
        # i is the current block
        if (conn_boxes[0] == i):
            conn_box = conn_boxes[1]
        else:
            conn_box = conn_boxes[0]
        # get number of elements in boxes previous to conn_box
        nel_pre_con = 0
        for k in range(0,conn_box):
            nel_pre_con = nel_pre_con + nelx[k]*nely[k]
        if (face == 1): 
            # south face: connected element is on top row in the conn box
            # and conn face is on north
            conn_el = nel_pre_con + (elx+1) + (nely[conn_box]-1)*nelx[conn_box]
            conn_face = 3
        elif(face == 2):  # east face: connected element is on the first column in the conn box
            # and conn face is west
            conn_el = nel_pre_con + (0+1) + ely*nelx[i]
            conn_face = 4
        elif(face == 3):  # north face: connected element is on the first row in the conn box
            # and conn face is south
            conn_el = nel_pre_con + (elx+1) + 0*nelx[i]
            conn_face = 1
        elif(face == 4):  # west face: connected element is on the last colum and conn face is east
            conn_el = nel_pre_con + nelx[conn_box] + ely*nelx[i]
            conn_face = 2
        return conn_el, conn_face


# Function for repetetive tasks while writing the fluid BCs
#----------------------------------------------------------------------
# Set appropriate connecting elements and faces depending on type of boundary conditions
def set_bc(file_obj, i, bctype, face, elx, ely, nelx, nely, n_tot, cor_int_el, cor_per_el):
    zero=float(0.0)
#    pdb.set_trace()
    n_prev = 0 # number of elements in all previous boxes
    for k in range(0,i):
        n_prev = n_prev + nelx[k]*nely[k]
    cur_el = elx+1 + ely*nelx[i] + n_prev
    dig_n_tot = len(str(n_tot)) # digits of n_tot
    # No parameters needed
    if (bctype[i] == 'W  ' or bctype[i] == 'SYM' or bctype[i] == 'v  '):
        write_f(file_obj, bctype[i], cur_el, dig_n_tot, face, 0.0, 0.0)
    # Connected element and face is needed
    elif (bctype[i] == 'E  '): # Internal
        if (face == 1): # south face: connected element is on row lower and conn face is on north
            conn_el = n_prev + (elx+1) + (ely-1)*nelx[i]
            conn_face = 3
        elif(face == 2):  # east face: connected element is on next column and conn face is west
            conn_el = n_prev + (elx+1) + 1 + ely*nelx[i]
            conn_face = 4
        elif(face == 3):  # north face: connected element is on row higher and conn face is south
            conn_el = n_prev + (elx+1) + (ely+1)*nelx[i]
            conn_face = 1
        elif(face == 4):  # west face: connected element is on previous colum and conn face is east
            conn_el = n_prev + (elx+1)-1 + ely*nelx[i]
            conn_face = 2
        write_f(file_obj, bctype[i], cur_el, dig_n_tot, face, conn_el, conn_face)
    elif (bctype[i] == 'P  '): # Periodic
        if (face == 1): # south side: conn el and face are on north side
            conn_el = n_prev + (elx+1) + (nely[i]-1)*nelx[i]
            conn_face = 3
        elif (face == 2): # east side: conn el and face are on west side
            conn_el = n_prev + 1 + ely*nelx[i]
            conn_face = 4
        elif (face == 3): # north side: conn el and face are on south side
            conn_el = n_prev + (elx+1) + 0*nelx[i]
            conn_face = 1
        elif (face == 4): # west side: conn el and face are on east side
            conn_el = n_prev + nelx[i] + ely*nelx[i]
            conn_face = 2
        write_f(file_obj, bctype[i], cur_el, dig_n_tot, face, conn_el, conn_face)
    # internal or periodic BC specified by the user between two boxes
    elif ( 'E' in bctype[i]  and bctype[i][1:3] != '  '):    
        # get the corresponding connected element and face
        [conn_el, conn_face] = get_con_el_f(i, cor_int_el, bctype, face, elx, ely, nelx, nely)
        write_f(file_obj, 'E  ', cur_el, dig_n_tot, face, conn_el, conn_face)
    
    # periodic BC specified by the user between two boxes
    elif ('P' in bctype[i] and bctype[i][1:3] != '  '):    
        # get the corresponding connected element and face
        [conn_el, conn_face] = get_con_el_f(i, cor_per_el, bctype, face, elx, ely, nelx, nely)
        write_f(file_obj, 'P  ', cur_el, dig_n_tot, face, conn_el, conn_face)


# Function for adding a value to a key in a dictionary for internal and periodic BCs 
# defined over multiple elements
#----------------------------------------------------------------------
def add_value(cor_block, key, dicti):
    # check if key is already there
    if (key in list(dicti.keys())):
        # append second block number to the key
        dicti[key] = [dicti[key], cor_block]
    else:
        dicti[key] = cor_block    # save number of this block


# Function for finding the corresponding user specified internal and periodic BCs between different blocks
#----------------------------------------------------------------------
def find_cor_el(nelx, nely, bcx0, bcx1, bcy0, bcy1):
    # Find corresponding user specified internal and periodic BCs between different blocks  
    cor_intern_el = {}  # dictionary of corresponding internal BCs (each as a pair of the two block numbers)
    cor_period_el = {}  # example {'01':[0, 5]} means that BC01 is found in blocks 0 and 5
    key = 0  # key to this BC; they should be numbered: E01, E02, E03; P01, P02, P03
    for i in range(0,len(nelx)):
        if ('E' in bcx0[i] and bcx0[i][1:3] != '  '):
            key = bcx0[i][1:3]
            add_value(i, key, cor_intern_el)
        elif ('P' in bcx0[i] and bcx0[i][1:3] != '  '):
            key = bcx0[i][1:3]
            add_value(i, key, cor_period_el)
        if ('E' in bcx1[i] and bcx1[i][1:3] != '  '):
            key = bcx1[i][1:3]
            add_value(i, key, cor_intern_el)
        elif ('P' in bcx1[i] and bcx1[i][1:3] != '  '):
            key = bcx1[i][1:3]
            add_value(i, key, cor_period_el)
        if ('E' in bcy0[i] and bcy0[i][1:3] != '  '):
            key = bcy0[i][1:3]
            add_value(i, key, cor_intern_el)
        elif ('P' in bcy0[i] and bcy0[i][1:3] != '  '):
            key = bcy0[i][1:3]
            add_value(i, key, cor_period_el)
        if ('E' in bcy1[i] and bcy1[i][1:3] != '  '):
            key = bcy1[i][1:3]
            add_value(i, key, cor_intern_el) 
        elif ('P' in bcy1[i] and bcy1[i][1:3] != '  '):
            key = bcy1[i][1:3]
            add_value(i, key, cor_period_el) 
    return cor_intern_el, cor_period_el


# Function for writing the fluid BCs in a correct format into .rea file
#----------------------------------------------------------------------
def write_bcs(file_obj, nelx, nely, n_total, bcx0, bcx1, bcy0, bcy1, bcz0, bcz1):
    # find the corresponding elements for internal or periodic BCs
    [cor_intern_el, cor_period_el] = find_cor_el(nelx, nely, bcx0, bcx1, bcy0, bcy1)
    # Loop through all blocks
    n_prev = 0
    for i in range(0,len(nelx)):
        # Loop through all elements:
        for ely in range(0,nely[i]):
            for elx in range(0,nelx[i]):
                # Loop over all faces
                for face in range(1,5):
                    # check if we are at the boundary
                    if (elx == 0 and face == 4):  # west side
                        bc = bcx0
                        f = 4
                    elif (elx == nelx[i]-1 and face == 2):  # east side
                        bc = bcx1
                        f = 2
                    elif (ely == 0 and face == 1):  # south side
                        bc = bcy0
                        f = 1
                    elif (ely == nely[i]-1 and face == 3):  # north side
                        bc = bcy1
                        f = 3
                    # This is the inside
                    else: 
                        # populate list for internal bctype
                        bc_int = []
                        for k in range(0,len(nelx)):
                            bc_int.append('E  ')
                        bc = bc_int
                        f = face
                    # Set the BC for current element and face
                    set_bc(file_obj, i, bc, f, elx, ely, nelx, nely, n_total, \
                            cor_intern_el, cor_period_el)
        n_prev = n_prev + nelx[i]*nely[i]


# End of function definitions
# xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx        
# xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx        

# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# MAIN PART OF THE PROGRAM
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------

# Read the .box file
#----------------------------------------------------------------------
#boxfile = input('--> ')
#boxfile = 'stream_005_dist.box1'
boxfile = 'rough_block.box5'
f = open(boxfile, 'r') # open for read
lines = f.readlines() # everything is saved in variable "lines"
f.close()

# remove all comments
num_lines = len(lines)
i = 0
while (i < num_lines): 
    if (lines[i][0] == '#'):
        del lines[i]
        num_lines = num_lines-1
    else:
        i = i + 1

# read first three lines
reafile = lines[0].strip()
spatial_dim = int(lines[1].split()[0])
num_fields = int(lines[2].split()[0])

# everything that follows is defining one or multiple boxes
box_lines = lines[3:len(lines)]

# Define some variables
j = 0 # counter for number of boxes
num_box = []
nel = []
nelx = []
nely = []
n_total = 0
x_coor = []
xpts = []
xstart = []
xend = []
xratio = []
y_coor = []
ypts = []
ystart = []
yend = []
yratio = []
bcs = []
bcx0 = []
bcx1 = []
bcy0 = []
bcy1 = []
bcz0 = []
bcz1 = []
if (spatial_dim == 2):
    box_params = box_lines
    while (len(box_params) >= 5):
        # 5 lines defining the 2d box
        num_box.append(box_params[0].strip())    # e. g. "Box 1"
        nel.append(box_params[1].split())
        nelx.append(int(nel[j][0]))
        nely.append(int(nel[j][1]))
        x_coor.append(box_params[2].split())
        multi_x = 0
        if (nelx[j] < 0):
            nelx[j] = nelx[j]*(-1)
            xstart.append(float(x_coor[j][0]))
            xend.append(float(x_coor[j][1]))
            xratio.append(float(x_coor[j][2]))
            xpts.append(calc_pts(xstart[j], xend[j], xratio[j], nelx[j]))
        else:
            xstart.append(0) # dummy values to fill them for this block
            xend.append(0)
            xratio.append(0)
            # check for multiple lines
            while (len(x_coor[j]) < nelx[j]+1):
                multi_x = multi_x + 1
                x_coor[j].extend(box_params[2+multi_x].split())
            xpts.append([float(x) for x in x_coor[j][0:nelx[j]+1]])
        y_coor.append(box_params[3+multi_x].split())
        multi_y = 0
        if (nely[j] < 0):
            nely[j] = nely[j]*(-1)
            ystart.append(float(y_coor[j][0]))
            yend.append(float(y_coor[j][1]))
            yratio.append(float(y_coor[j][2]))
            ypts.append(calc_pts(ystart[j], yend[j], yratio[j], nely[j]))
        else:
            ystart.append(0) # dummy values to fill them for this block
            yend.append(0)
            yratio.append(0)
            # check for multiple lines
            while (len(y_coor[j]) < nely[j]+1):
                multi_y = multi_y + 1
                y_coor[j].extend(box_params[3+multi_x+multi_y].split())
            ypts.append([float(x) for x in y_coor[j][0:nely[j]+1]])
        bcs.append(box_params[4+multi_x+multi_y].split(','))
        bcx0.append(bcs[j][0])
        bcx1.append(bcs[j][1])
        bcy0.append(bcs[j][2])
        bcy1.append(bcs[j][3])
        bcz0.append(bcs[j][4])
        bcz1.append(bcs[j][5][0:2])
        # remove first box lines
        del box_params[0:5+multi_x+multi_y]
        j = j+1
    # get total number of elements
    for h in range(0, len(nelx)):
        n_total = n_total + nelx[h]*nely[h]
elif (spatial_dim == 3):
    # 6 lines defining the 3d box
    n=3


# Now read the corresponding .rea file
#----------------------------------------------------------------------
f = open(reafile.strip(), 'r') # open for read
lines = f.readlines()
f.close()

# Write a new box.rea file which contains the mesh
#----------------------------------------------------------------------
f = open('box.rea', 'w') # open for write
skip = False
for i in lines:
    if('MESH DATA' in i):
        f.write(i)
#        pdb.set_trace()
        write_mesh(f, xpts, ypts, \
                nelx, nely, n_total, spatial_dim)
        skip = True
    if('CURVED SIDE DATA' in i):
        skip = False
    if('FLUID   BOUNDARY' in i):
        f.write(i)
        write_bcs(f, nelx, nely, n_total, bcx0, bcx1, bcy0, bcy1, bcz0, bcz1)
        skip = True
    if('NO THERMAL BOUNDARY' in i):
        skip = False
    if(not skip):
        f.write(i)
f.close()
