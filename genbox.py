# This python script is inspired by Nek5000's genbox tool for simple mesh generation
# I want to use it to create a simple mesh for roughness simulations 

import pdb # for debugging
# Define some functions
#----------------------------------------------------------------------
def write_mesh(file_obj, xstart, xend, ystart, yend, nelx, nely, spatial_dim, dx, dy):
    n_tot = 0   # total number of elements in all blocks
    for i in range(0,len(nelx)):
        n_tot = n_tot + nelx[i]*nely[i]
    # write header 
    file_obj.write('{0:10d} {1:10d} {2:10d}'.format(n_tot,spatial_dim,n_tot))
    file_obj.write(' NEL,NDIM,NELV\n')

    # write elements for all blocks
    n_prev = 0  # number of elements in all previous blocks
    for i in range(0,len(nelx)):    # loop through all blocks
        # copy element locations
#        pdb.set_trace()
        x0 = xstart[i]
        x1 = xend[i]
        deltax = dx[i]
        y0 = ystart[i]
        y1 = yend[i]
        deltay = dy[i]
        for ely in range(0,nely[i]):    # Loop through all elements
            for elx in range(0,nelx[i]):
                elem_number = elx + ely*nely[i] + 1 + n_prev
                file_obj.write('{0:>19s} {1:10d} {2:6s}{3:1s}{4:12s}'.format\
                        ('ELEMENT',elem_number,'[    1','a',']  GROUP  0\n'))
                file_obj.write('{0: 10.5f}{1: 14.5f}{2: 14.5f}{3: 14.5f} {4:s}'.format\
                        (x0,x0+deltax,x0+deltax,x0,'\n'))   # x coordinates
                file_obj.write('{0: 10.5f}{1: 14.5f}{2: 14.5f}{3: 14.5f} {4:s}'.format\
                        (y0,y0,y0+deltay,y0+deltay,'\n'))  # y coordinates
                # update element locations
                x0 = x0+deltax
            x0 = xstart[i]
            y0 = y0 +deltay
        n_prev = n_prev + nelx[i]*nely[i]   # update n_prev

# Set appropriate connecting elements and faces depending on type of boundary conditions
def set_bc(file_obj, i, bctype, face, elx, ely, nelx, nely, cor_int_el):
    zero=float(0.0)
#    pdb.set_trace()
    n_prev = 0 # number of elements in all previous boxes
    for k in range(0,i):
        n_prev = n_prev + nelx[i]*nely[i]
    cur_el = elx+1 + ely*nely[i] + n_prev
    # No parameters needed
    if (bctype[i] == 'W  '): # Wall
        file_obj.write(' {0:3s} {1:2d} {2:2d}{3:10.5f}{4:14.5f}{5:14.5f}{6:14.5f}{7:14.5f}{8:s}'\
            .format('W  ',cur_el,face,zero,zero,zero,zero,zero,'\n'))
    if (bctype[i] == 'SYM'): # Symmetry
        file_obj.write(' {0:3s} {1:2d} {2:2d}{3:10.5f}{4:14.5f}{5:14.5f}{6:14.5f}{7:14.5f}{8:s}'\
            .format('SYM',cur_el,face,zero,zero,zero,zero,zero,'\n'))
    if (bctype[i] == 'v  '): # Dirichlet BC for velocity given in userbc
         file_obj.write(' {0:3s} {1:2d} {2:2d}{3:10.5f}{4:14.5f}{5:14.5f}{6:14.5f}{7:14.5f}{8:s}'\
            .format('v  ',cur_el,face,zero,zero,zero,zero,zero,'\n'))
    # Connected element and face is needed
    if (bctype[i] == 'E  '): # Internal
        if (face == 1): # south face: connected element is on row lower and conn face is on north
            conn_el = n_prev + elx + (ely-1)*nely[i]+1
            conn_face = 3
        elif(face == 2):  # east face: connected element is on next column and conn face is west
            conn_el = n_prev + elx + 1 + ely*nely[i]+1
            conn_face = 4
        elif(face == 3):  # north face: connected element is on row higher and conn face is south
            conn_el = n_prev + elx + (ely+1)*nely[i]+1
            conn_face = 1
        elif(face == 4):  # west face: connected element is on previous colum and conn face is east
            conn_el = n_prev + elx-1 + ely*nely[i]+1
            conn_face = 2
        file_obj.write(' {0:3s} {1:2d} {2:2d}{3:10.5f}{4:14.5f}{5:14.5f}{6:14.5f}{7:14.5f}{8:s}'\
            .format('E  ',cur_el,face,conn_el,conn_face,zero,zero,zero,'\n'))
    elif (bctype[i] == 'P  '): # Periodic
        conn_el = n_prev + 0
        conn_face = 0
        if (face == 1): # south side: conn el and face are on north side
            conn_el = n_prev + elx+(nely[i]-1)*nely[i]+1
            conn_face = 3
        elif (face == 2): # east side: conn el and face are on west side
            conn_el = n_prev + 1+ely*nely[i]
            conn_face = 4
        elif (face == 3): # north side: conn el and face are on south side
            conn_el = n_prev + elx+0*nely[i]+1
            conn_face = 1
        elif (face == 4): # west side: conn el and face are on east side
            conn_el = n_prev + nelx[i]+ely*nely[i]
            conn_face = 2
        file_obj.write(' {0:3s} {1:2d} {2:2d}{3:10.5f}{4:14.5f}{5:14.5f}{6:14.5f}{7:14.5f}{8:s}'\
            .format('P  ',cur_el,face,conn_el,conn_face,zero,zero,zero,'\n'))
    # internal BC specified by the user between two boxes
    elif ('E' in bctype[i] and bctype[i][1:3] != '  '):    
        # get number of connected boxes
#        pdb.set_trace()
        conn_boxes = cor_int_el[bctype[i][1:3]]
        # choose the other box (different from i)
        if (conn_boxes[0] == i):
            conn_box = conn_boxes[1]
        else:
            conn_box = conn_boxes[0]
        # get number of elements in boxes previous to conn_box
        nel_pre_con = 0
        for k in range(0,conn_box):
            nel_pre_con = nel_pre_con + nelx[k]*nely[k]
##        pdb.set_trace()
        if (face == 1): 
            # south face: connected element is on top row in the conn box
            # and conn face is on north
            conn_el = nel_pre_con + elx + (nely-1)*nely[conn_box]+1
            conn_face = 3
        elif(face == 2):  # east face: connected element is on the first column in the conn box
            # and conn face is west
            conn_el = nel_pre_con + 0 + ely*nely[i]+1
            conn_face = 4
        elif(face == 3):  # north face: connected element is on the first row in the conn box
            # and conn face is south
            conn_el = nel_pre_con + elx + 0*nely[i]+1
            conn_face = 1
        elif(face == 4):  # west face: connected element is on  colum and conn face is east
            conn_el = n_prev + nelx[conn_box] + ely*nely[i]+1
            conn_face = 2
        file_obj.write(' {0:3s} {1:2d} {2:2d}{3:10.5f}{4:14.5f}{5:14.5f}{6:14.5f}{7:14.5f}{8:s}'\
            .format('E  ',cur_el,face,conn_el,conn_face,zero,zero,zero,'\n'))


def write_bcs(file_obj, nelx, nely, bcx0, bcx1, bcy0, bcy1, bcz0, bcz1):
    # Find corresponding user specified internal and periodic BCs between different blocks  
    cor_intern_el = {}  # dictionary of corresponding internal BCs (each as a pair of the two block numbers)
    key_intern = 0  # key to this internal BC; they should be numbered: E01, E02, E03
    for i in range(0,len(nelx)):
        if ('E' in bcx0[i] and bcx0[i][1:3] != '  '):
            key_intern = bcx0[i][1:3]
            # check if key is already there
            if (key_intern in list(cor_intern_el.keys())):
                # append second block number to the key
                cor_intern_el[key_intern] = [cor_intern_el[key_intern], i]
            else:
                cor_intern_el[key_intern] = i    # save number of this block
        if ('E' in bcx1[i] and bcx1[i][1:3] != '  '):
            key_intern = bcx1[i][1:3]
            # check if key is already there
            if (key_intern in list(cor_intern_el.keys())):
                # append second block number to the key
                cor_intern_el[key_intern] = [cor_intern_el[key_intern], i]
            else:
                cor_intern_el[key_intern] = i    # save number of this block
        if ('E' in bcy0[i] and bcy0[i][1:3] != '  '):
            key_intern = bcy0[i][1:3]
            # check if key is already there
            if (key_intern in list(cor_intern_el.keys())):
                # append second block number to the key
                cor_intern_el[key_intern] = [cor_intern_el[key_intern], i]
            else:
                cor_intern_el[key_intern] = i    # save number of this block
        if ('E' in bcy1[i] and bcy1[i][1:3] != '  '):
            key_intern = bcy1[i][1:3]
            # check if key is already there
            if (key_intern in list(cor_intern_el.keys())):
                # append second block number to the key
                cor_intern_el[key_intern] = [cor_intern_el[key_intern], i]
            else:
                cor_intern_el[key_intern] = i    # save number of this block

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
                        set_bc(file_obj, i, bcx0, face, elx, ely, nelx, nely, \
                                cor_intern_el)
                    elif (elx == nelx[i]-1 and face == 2):  # east side
                        set_bc(file_obj, i, bcx1, face, elx, ely, nelx, nely, \
                                cor_intern_el)
                    elif (ely == 0 and face == 1):  # south side
                        set_bc(file_obj, i, bcy0, face, elx, ely, nelx, nely, \
                                cor_intern_el)
                    elif (ely == nely[i]-1 and face == 3):  # north side
                        set_bc(file_obj, i, bcy1, face, elx, ely, nelx, nely, \
                                cor_intern_el)
                    # This is the inside
                    else: 
                        # populate list for internal bctype
                        bc_int = []
                        for k in range(0,len(nelx)):
                            bc_int.append('E  ')
                        set_bc(file_obj, i, bc_int, face, elx, ely, nelx, nely, \
                                cor_intern_el)
        n_prev = n_prev + nelx[i]*nely[i]

# Read the .box file
#----------------------------------------------------------------------
#boxfile = input('--> ')
boxfile = 'stream_005.box'
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
xstart = []
xend = []
xratio = []
x_len = []
dx = []
y_coor = []
ystart = []
yend = []
yratio = []
y_len = []
dy = []
bcs = []
bcx0 = []
bcx1 = []
bcy0 = []
bcy1 = []
bcz0 = []
bcz1 = []
if (spatial_dim == 2):
#    pdb.set_trace()
    box_params = box_lines
    while (len(box_params) >= 5):
        # 5 lines defining the 2d box
        num_box.append(box_params[0].strip())    # e. g. "Box 1"
        nel.append(box_params[1].split())
        nelx.append(int(nel[j][0])*(-1))
        nely.append(int(nel[j][1])*(-1))
        x_coor.append(box_params[2].split())
        xstart.append(float(x_coor[j][0]))
        xend.append(float(x_coor[j][1]))
        xratio.append(float(x_coor[j][2]))
        x_len.append(abs(xend[j] - xstart[j]))
        dx.append(x_len[j]/nelx[j])
        y_coor.append(box_params[3].split())
        ystart.append(float(y_coor[j][0]))
        yend.append(float(y_coor[j][1]))
        yratio.append(float(y_coor[j][2]))
        y_len.append(abs(yend[j] - ystart[j]))
        dy.append(y_len[j]/nely[j])
        bcs.append(box_params[4].split(','))
        bcx0.append(bcs[j][0])
        bcx1.append(bcs[j][1])
        bcy0.append(bcs[j][2])
        bcy1.append(bcs[j][3])
        bcz0.append(bcs[j][4])
        bcz1.append(bcs[j][5][0:2])
        # remove first box lines
        del box_params[0:5]
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
        write_mesh(f, xstart, xend, ystart, yend, \
                nelx, nely, spatial_dim, dx, dy)
        skip = True
    if('CURVED SIDE DATA' in i):
        skip = False
    if('FLUID   BOUNDARY' in i):
        f.write(i)
        write_bcs(f, nelx, nely, bcx0, bcx1, bcy0, bcy1, bcz0, bcz1)
        skip = True
    if('NO THERMAL BOUNDARY' in i):
        skip = False
    if(not skip):
        f.write(i)

        
f.close()
