# This python script is inspired by Nek5000's genbox tool for simple mesh generation
# I want to use it to create a simple mesh for roughness simulations 

import pdb
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

j = 0 # counter for number of boxes
num_box = []
nel = []
nelx = []
nely = []
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
    while (len(box_lines) > 5):
        # 5 lines defining the 2d box
        num_box.append(box_lines[0].strip())    # e. g. "Box 1"
        nel.append(box_lines[1].split())
        nelx.append(int(nel[j][0])*(-1))
        nely.append(int(nel[j][1])*(-1))
        x_coor.append(box_lines[2].split())
        xstart.append(float(x_coor[j][0]))
        xend.append(float(x_coor[j][1]))
        xratio.append(float(x_coor[j][2]))
        x_len.append(abs(xend[j] - xstart[j]))
        dx.append(x_len[j]/nelx[j])
        y_coor.append(box_lines[3].split())
        ystart.append(float(y_coor[j][0]))
        yend.append(float(y_coor[j][1]))
        yratio.append(float(y_coor[j][2]))
        y_len.append(abs(yend[j] - ystart[j]))
        dy.append(y_len[j]/nely[j])
        bcs.append(box_lines[4].split(','))
        bcx0.append(bcs[j][0])
        bcx1.append(bcs[j][1])
        bcy0.append(bcs[j][2])
        bcy1.append(bcs[j][3])
        bcz0.append(bcs[j][4])
        bcz1.append(bcs[j][5][0:2])
        # remove first box lines
        del box_lines[0:4]
        j = j+1
elif (spatial_dim == 3):
    # 6 lines defining the 3d box
    n=3


## old style
#f = open(boxfile, 'r')
#reafile = f.readline()
#spatial_dim = int(f.readline().split()[0])
#num_fields = f.readline().split()[0]
#str = f.readline()
#while (str[0] is '#'):     # Skip comments
#    str = f.readline()
#num_box = str
#nel = f.readline().split()
#nelx = int(nel[0])*(-1)
#nely = int(nel[1])*(-1)
#x_coor = f.readline().split()
#xstart = float(x_coor[0])
#xend = float(x_coor[1])
#xratio = x_coor[2]
#x_len = abs(xend - xstart)
#dx = x_len/nelx
#y_coor = f.readline().split()
#ystart = float(y_coor[0])
#yend = float(y_coor[1])
#yratio = y_coor[2]
#y_len = abs(yend - ystart)
#dy = y_len/nely
#bcs = f.readline().split(',')
#bcx0 = bcs[0]
#bcx1 = bcs[1]
#bcy0 = bcs[2]
#bcy1 = bcs[3]
#bcz0 = bcs[4]
#bcz1 = bcs[5][0:2]

# Define some functions
#----------------------------------------------------------------------
def write_mesh(file_obj, xstart, xend, ystart, yend, nelx, nely, spatial_dim, dx, dy):
    # copy element locations
    x0 = xstart
    x1 = xend
    y0 = ystart
    y1 = yend
    file_obj.write('{0:10d} {1:10d} {2:10d}'.format(nelx*nely,spatial_dim,nelx*nely))
    file_obj.write(' NEL,NDIM,NELV\n')
    # Loop through all elements
    for ely in range(0,nely):
        for elx in range(0,nelx):
            file_obj.write('{0:>19s} {1:10d} {2:6s}{3:1s}{4:12s}'.format\
                    ('ELEMENT',elx+ely*nely+1,'[    1','a',']  GROUP  0\n'))
            file_obj.write('{0: 10.5f}{1: 14.5f}{2: 14.5f}{3: 14.5f} {4:s}'.format\
                    (x0,x0+dx,x0+dx,x0,'\n'))   # x coordinates
            file_obj.write('{0: 10.5f}{1: 14.5f}{2: 14.5f}{3: 14.5f} {4:s}'.format\
                    (y0,y0,y0+dy,y0+dy,'\n'))  # y coordinates
            # update element locations
            x0 = x0+dx
        x0 = xstart
        y0 = y0 +dy

# Set appropriate connecting elements and faces depending on type of boundary conditions
def set_bc(file_obj, bctype, face, elx, ely, nelx, nely):
    zero=float(0.0)
#    pdb.set_trace()
    # No parameter needed
    if (bctype == 'W  '): # Wall
        file_obj.write(' {0:3s} {1:2d} {2:2d}{3:10.5f}{4:14.5f}{5:14.5f}{6:14.5f}{7:14.5f}{8:s}'\
            .format('W  ',elx+ely*nely+1,face,zero,zero,zero,zero,zero,'\n'))
    if (bctype == 'SYM'): # Symmetry
        file_obj.write(' {0:3s} {1:2d} {2:2d}{3:10.5f}{4:14.5f}{5:14.5f}{6:14.5f}{7:14.5f}{8:s}'\
            .format('SYM',elx+ely*nely+1,face,zero,zero,zero,zero,zero,'\n'))
    if (bctype == 'v  '): # Dirichlet BC for velocity given in userbc
         file_obj.write(' {0:3s} {1:2d} {2:2d}{3:10.5f}{4:14.5f}{5:14.5f}{6:14.5f}{7:14.5f}{8:s}'\
            .format('v  ',elx+ely*nely+1,face,zero,zero,zero,zero,zero,'\n'))
    # Connected element and face is needed
    if (bctype == 'E  '): # Internal
        if (face == 1): # south face: connected element is on row lower and conn face is on north
            conn_el = elx + (ely-1)*nely+1
            conn_face = 3
        elif(face == 2):  # east face: connected element is on next column and conn face is west
            conn_el = elx + 1 + ely*nely+1
            conn_face = 4
        elif(face == 3):  # north face: connected element is on row higher and conn face is south
            conn_el = elx + (ely+1)*nely+1
            conn_face = 1
        elif(face == 4):  # west face: connected element is on previous colum and conn face is east
            conn_el = elx-1 + ely*nely+1
            conn_face = 2
        file_obj.write(' {0:3s} {1:2d} {2:2d}{3:10.5f}{4:14.5f}{5:14.5f}{6:14.5f}{7:14.5f}{8:s}'\
            .format('E  ',elx+ely*nely+1,face,conn_el,conn_face,zero,zero,zero,'\n'))
    if (bctype == 'P  '): # Periodic
        conn_el = 0
        conn_face = 0
        if (face == 1): # south side: conn el and face are on north side
            conn_el = elx+(nely-1)*nely+1
            conn_face = 3
        elif (face == 2): # east side: conn el and face are on west side
            conn_el = 1+ely*nely
            conn_face = 4
        elif (face == 3): # north side: conn el and face are on south side
            conn_el = elx+0*nely+1
            conn_face = 1
        elif (face == 4): # west side: conn el and face are on east side
            conn_el = nelx+ely*nely
            conn_face = 2
        file_obj.write(' {0:3s} {1:2d} {2:2d}{3:10.5f}{4:14.5f}{5:14.5f}{6:14.5f}{7:14.5f}{8:s}'\
            .format('P  ',elx+ely*nely+1,face,conn_el,conn_face,zero,zero,zero,'\n'))

def write_bcs(file_obj, nelx, nely, bcx0, bcx1, bcy0, bcy1, bcz0, bcz1):
    # Loop through all elements:
    for ely in range(0,nely):
        for elx in range(0,nelx):
            # Loop over all faces
            for face in range(1,5):
                # check if we are at the boundary
                if (elx == 0 and face == 4):  # west side
                    set_bc(file_obj, bcx0, face, elx, ely, nelx, nely)
                elif (elx == nelx-1 and face == 2):  # east side
                    set_bc(file_obj, bcx1, face, elx, ely, nelx, nely)
                elif (ely == 0 and face == 1):  # south side
                    set_bc(file_obj, bcy0, face, elx, ely, nelx, nely)
                elif (ely == nely-1 and face == 3):  # north side
                    set_bc(file_obj, bcy1, face, elx, ely, nelx, nely)
                # This is the inside
                else: 
                    set_bc(file_obj, 'E  ', face, elx, ely, nelx, nely)


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
        for h in range(0,j):
            write_mesh(f, xstart[h], xend[h], ystart[h], yend[h], \
                    nelx[h], nely[h], spatial_dim, dx[h], dy[h])
        skip = True
    if('CURVED SIDE DATA' in i):
        skip = False
    if('FLUID   BOUNDARY' in i):
        f.write(i)
        for h in range(0,j):
            write_bcs(f, nelx[h], nely[h], bcx0[h], bcx1[h], bcy0[h], bcy1[h], bcz0[h], bcz1[h])
        skip = True
    if('NO THERMAL BOUNDARY' in i):
        skip = False
    if(not skip):
        f.write(i)

        
f.close()
