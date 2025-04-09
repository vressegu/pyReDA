#!/usr/bin/env python3

import matplotlib.pyplot as plt
import numpy as np
import sys
import re

from matplotlib import colormaps

from decimal import Decimal

from itertools import cycle

print ( "\nNumber of arguments : "+ str(len(sys.argv))+ " arguments." )
print ( "  Argument List:"+ str(sys.argv) )

nbCols = 2
fic_npy = "ITHACAoutput/CovMatrices/covMatrixU.npy"

if ( len(sys.argv) >1 ):
  fic_npy = sys.argv[1]

# ascii file name for gnuplot
if ( len(sys.argv) >2 ):
  fic_txt = sys.argv[2]

fic_txt = re.sub('.npy', r'.txt', fic_npy)
data = np.load(fic_npy)

print_info=False
print_info=True

if print_info:
  print ( "\n  file "+str(fic_npy)+" : type(data)="+str(type(data)) )
  print ( "  file "+str(fic_npy)+" : len(data)="+str(len(data))  )
  print ( "  file "+str(fic_npy)+" : data.dim="+str(data.ndim)+"D"  )
  print ( "  file "+str(fic_npy)+" : data.shape="+str(data.shape)  )

nbRows = data.shape[0]
nbCols = data.shape[1]
#np.savetxt(fic_txt, data)

#print ( "  -> Cf. file "+str(fic_txt)+str("\n"))

fig = plt.figure(1)
plt.title(fic_npy)

# unrealValue -> change to value with COLOR=white
data_tmp = np.zeros((nbRows, nbCols))

for i in range(nbRows):
  for j in range(nbCols):
    data_tmp[i][j]=data[i][j]
    if data[i][j] == 999999.999999:
      data_tmp[i][j] = 0
mid_value = (data_tmp.min()+data_tmp.max())/2.
min_value = data_tmp.min()
max_value = data_tmp.max()
print("\nmid value="+str(mid_value)+" in ["+str(min_value)+":"+str(max_value)+"]\n")

# color bar centered on value=0
lim = max (np.abs(min_value), np.abs(max_value))

# change value=unrealValue to value=0
for i in range(nbRows):
  for j in range(nbCols):
    if data[i][j] == 999999.999999:
      data[i][j] = 0

# Cf. https://matplotlib.org/stable/gallery/color/colormap_reference.html
#plt.imshow(data, interpolation='nearest', origin='lower', cmap='nipy_spectral')
#plt.imshow(data, interpolation='nearest', origin='lower', cmap='gist_rainbow')
#plt.imshow(data, interpolation='nearest', origin='lower', cmap='jet')
#plt.imshow(data, interpolation='nearest', origin='lower', cmap='prism')
#plt.imshow(data, interpolation='nearest', origin='lower', cmap='gray')
#plt.imshow(data, interpolation='nearest', origin='lower', cmap='PiYG')
#plt.imshow(data, interpolation='nearest', origin='lower', cmap='seismic')
#plt.imshow(data, interpolation='nearest', origin='lower', cmap='Spectral')
#plt.imshow(data, interpolation='nearest', origin='lower', cmap='gist_ncar')
plt.imshow(data, interpolation='nearest', origin='lower', cmap='PuOr_r', vmin=-lim, vmax=lim)
plt.colorbar()

plt.show()

fic_png = re.sub('.npy', r'.png', fic_npy)
dpi_value = 800
dpi_value = int(np.floor(nbRows/2))
fig.savefig(fic_png, dpi=dpi_value, transparent=False, bbox_inches='tight')
plt.close()

print ( "  -> Cf. file "+str(fic_png)+str("\n"))
