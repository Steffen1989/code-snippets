# This python script is inspired by Nek5000's genbox tool for simple mesh generation
# I want to use it to create a simple mesh for roughness simulations 

# Read the .box file
#----------------------------------------------------------------------
#boxfile = input('--> ')
boxfile = 'stream_005.box'
f = open(boxfile, 'r')
reafile = f.readline()
spatial_dim = int(f.readline().split()[0])
num_fields = f.readline().split()[0]
str = f.readline()
while (str[0] is '#'):     # Skip comments
    str = f.readline()
num_box = str
nel = f.readline().split()
nelx = int(nel[0])*(-1)
nely = int(nel[1])*(-1)
x_coor = f.readline().split()
xstart = float(x_coor[0])
xend = float(x_coor[1])
xratio = x_coor[2]
x_len = abs(xend - xstart)
dx = x_len/nelx
y_coor = f.readline().split()
ystart = float(y_coor[0])
yend = float(y_coor[1])
yratio = y_coor[2]
y_len = abs(yend - ystart)
dy = y_len/nely
bcs = f.readline().split(',')
bcx0 = bcs[0]
bcx1 = bcs[1]
bcy0 = bcs[2]
bcy1 = bcs[3]
bcz0 = bcs[4]
bcz1 = bcs[5][0:2]
f.close()

# Now read the corresponding .rea file
#----------------------------------------------------------------------
def write_mesh(file_obj):
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

def write_bcs(file_obj):
    zero=float(0.0)
    # Loop through all elements:
    for ely in range(0,nely):
        for elx in range(0,nelx):
            # Loop over all faces
            for face in range(1,5):
                # check if we are at the boundary
                if (elx == 0 and face == 4):  # west side
                    if(bcx0 == 'P  '):   # periodic BCs: connecting element and face is on east side
                        file_obj.write(' {0:3s} {1:2d} {2:2d}{3:10.5f}{4:14.5f}{5:14.5f}{6:14.5f}{7:14.5f}{8:s}'\
                            .format('P  ',elx+ely*nely+1,face,nelx+ely*nely,2,zero,zero,zero,'\n'))
                elif (elx == nelx-1 and face == 2):  # east side
                    if(bcx1 == 'P  '):  # periodic BCs: connectin element and face is on west side
                        file_obj.write(' {0:3s} {1:2d} {2:2d}{3:10.5f}{4:14.5f}{5:14.5f}{6:14.5f}{7:14.5f}{8:s}'\
                            .format('P  ',elx+ely*nely+1,face,1+ely*nely,4,zero,zero,zero,'\n'))
                elif (ely == 0 and face == 1):  # south side
                    if(bcy0 == 'W  '):  # wall BCs
                        file_obj.write(' {0:3s} {1:2d} {2:2d}{3:10.5f}{4:14.5f}{5:14.5f}{6:14.5f}{7:14.5f}{8:s}'\
                            .format('W  ',elx+ely*nely+1,face,zero,zero,zero,zero,zero,'\n'))
                elif (ely == nely-1 and face == 3):  # north side
                    if(bcx1 == 'SYM'):  # symmetry BCs
                        file_obj.write(' {0:3s} {1:2d} {2:2d}{3:10.5f}{4:14.5f}{5:14.5f}{6:14.5f}{7:14.5f}{8:s}'\
                            .format('SYM',elx+ely*nely+1,face,zero,zero,zero,zero,zero,'\n'))
                else: 
                    if(face == 1):  # south face: connected element is on row lower and conn face is north
                        file_obj.write(' {0:3s} {1:2d} {2:2d}{3:10.5f}{4:14.5f}{5:14.5f}{6:14.5f}{7:14.5f}{8:s}'\
                            .format('E  ',elx+ely*nely+1,face,elx+(ely-1)*nely+1,3,zero,zero,zero,'\n'))
                    elif(face == 2):  # east face: connected element is on next column and conn face is west
                        file_obj.write(' {0:3s} {1:2d} {2:2d}{3:10.5f}{4:14.5f}{5:14.5f}{6:14.5f}{7:14.5f}{8:s}'\
                            .format('E  ',elx+ely*nely+1,face,elx+1+ely*nely+1,4,zero,zero,zero,'\n'))
                    elif(face == 3):  # north face: connected element is on row higher and conn face is south
                        file_obj.write(' {0:3s} {1:2d} {2:2d}{3:10.5f}{4:14.5f}{5:14.5f}{6:14.5f}{7:14.5f}{8:s}'\
                            .format('E  ',elx+ely*nely+1,face,elx+(ely+1)*nely+1,1,zero,zero,zero,'\n'))
                    elif(face == 4):  # west face: connected element is on previous colum and conn face is east
                        file_obj.write(' {0:3s} {1:2d} {2:2d}{3:10.5f}{4:14.5f}{5:14.5f}{6:14.5f}{7:14.5f}{8:s}'\
                            .format('E  ',elx+ely*nely+1,face,elx-1+ely*nely+1,2,zero,zero,zero,'\n'))

                    else:
                        file_obj.write(' {0:3s} {1:2d} {2:2d}{3:10.5f}{4:14.5f}{5:14.5f}{6:14.5f}{7:14.5f}{8:s}'\
                            .format('E  ',elx+ely*nely+1,face,zero,zero,zero,zero,zero,'\n'))



f = open(reafile.strip(), 'r') # open for read
lines = f.readlines()
f.close()

f = open('box.rea', 'w') # open for write
skip = False
for i in lines:
    if('MESH DATA' in i):
        f.write(i)
        write_mesh(f)
        skip = True
    if('CURVED SIDE DATA' in i):
        skip = False
    if('FLUID   BOUNDARY' in i):
        f.write(i)
        write_bcs(f)
        skip = True
    if('NO THERMAL BOUNDARY' in i):
        skip = False
    if(not skip):
        f.write(i)

        
f.close()



## Skip parameter part
#f.readline()
#f.readline()
#f.readline()
#lineparams = f.readline()
#print(lineparams)
#str = lineparams.split(' ')
#nparams = str[9]
#for i in range(1, int(nparams)+1):
#    f.readline()
#
## Skip passive scalars
#lineparams = f.readline()
#print(lineparams)
#str = lineparams.split(' ')
#nparams = str[6]
#for i in range(1, int(nparams)+1):
#    f.readline()
#
## Skip logical switches
#lineparams = f.readline()
#print(lineparams)
#str = lineparams.split(' ')
#nparams = str[10]
#for i in range(1, int(nparams)+1):
#    f.readline()
#
## Skip mesh header
#str = f.readline()
#print(str)
#str = f.readline()
#print(str)
#
#
##f.write('This is a test\n')
##f.close()
