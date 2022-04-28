#!/usr/bin/env python
import os
import sys
import shutil
import gdal
import numpy as np
from scipy.signal import convolve2d
from subprocess import call
from shapely.geometry import Point,Polygon
from matplotlib.path import Path
import matplotlib.patches as patches
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib.backends.backend_pdf import PdfPages
from optparse import OptionParser,IndentedHelpFormatter

# Default values
GPS_FNAM = 'gps_points.dat'
FIGNAM = 'drone_extract_points.pdf'

# Read options
parser = OptionParser(formatter=IndentedHelpFormatter(max_help_position=200,width=200))
parser.add_option('-I','--src_geotiff',default=None,help='Source GeoTIFF name (%default)')
parser.add_option('-O','--dst_geotiff',default=None,help='Destination GeoTIFF name (%default)')
parser.add_option('-g','--gps_fnam',default=GPS_FNAM,help='GPS file name (%default)')
parser.add_option('-F','--fignam',default=FIGNAM,help='Output figure name (%default)')
(opts,args) = parser.parse_args()

blocks = []
numbers = []
gpss = []
xs = []
ys = []
with open(opts.gps_fnam,'r') as fp:
    # 11A    1  845 751014.955484 9242939.164135
    # 11A    2  846 751016.734576 9242941.257759
    for line in fp:
        item = line.split()
        if len(item) != 5:
            continue
        blocks.append(item[0].upper())
        numbers.append(int(item[1]))
        gpss.append(int(item[2]))
        xs.append(float(item[3]))
        ys.append(float(item[4]))
blocks = np.array(blocks)
numbers = np.array(numbers)
gpss = np.array(gpss)
xs = np.array(xs)
ys = np.array(ys)

plt.interactive(True)
fig = plt.figure(1,facecolor='w',figsize=(5,5))
pdf = PdfPages(opts.fignam)
bnam,enam = os.path.splitext(opts.dst_geotiff)
for i_group in range(3):
    onam = bnam+'_{}'.format(i_group+1)+enam
    # Read subset image
    ds = gdal.Open(onam)
    tmp_nx = ds.RasterXSize
    tmp_ny = ds.RasterYSize
    tmp_nb = ds.RasterCount
    tmp_trans = ds.GetGeoTransform()
    if tmp_trans[2] != 0.0 or tmp_trans[4] != 0.0:
        raise ValueError('Error, tmp_trans={}'.format(tmp_trans))
    tmp_nodata = ds.GetRasterBand(1).GetNoDataValue()
    tmp_data = ds.ReadAsArray().reshape(tmp_nb,tmp_ny,tmp_nx)
    tmp_xmin = tmp_trans[0]
    tmp_xstp = tmp_trans[1]
    tmp_ymax = tmp_trans[3]
    tmp_ystp = tmp_trans[5]
    tmp_xmax = tmp_xmin+tmp_nx*tmp_xstp
    tmp_ymin = tmp_ymax+tmp_ny*tmp_ystp
    tmp_xgrd = tmp_xmin+(np.arange(tmp_nx)+0.5)*tmp_xstp
    tmp_ygrd = tmp_ymax+(np.arange(tmp_ny)+0.5)*tmp_ystp
    ds = None
    tmp_shape = (tmp_ny,tmp_nx)
    tmp_indy,tmp_indx = np.indices(tmp_shape)
    tmp_xp = tmp_trans[0]+(tmp_indx+0.5)*tmp_trans[1]+(tmp_indy+0.5)*tmp_trans[2]
    tmp_yp = tmp_trans[3]+(tmp_indx+0.5)*tmp_trans[4]+(tmp_indy+0.5)*tmp_trans[5]

    ri = (tmp_data[2]-tmp_data[1])/(tmp_data[2]+tmp_data[1])
    filt1 = np.ones((7,7))
    norm = filt1.sum()
    filt1 *= 1.0/norm
    filt2 = np.ones((3,3))
    norm = filt2.sum()
    filt2 *= 1.0/norm
    res = []
    for i in [0,2]:
        cnv1 = convolve2d(tmp_data[i],filt1,mode='same')
        cnv2 = convolve2d(tmp_data[i],filt2,mode='same')
        vout = (cnv1*filt1.size-cnv2*filt2.size)/(filt1.size-filt2.size)
        res.append(tmp_data[i]-vout)
    re = res[1]
    cnd = (res[0] < 0.0) & (res[1] > 0.0)
    re[cnd] *= -1.0
    cnd = (tmp_data[1] == tmp_nodata) | (tmp_data[2] == tmp_nodata)
    ri[cnd] = np.nan
    re[cnd] = np.nan
    cnd = (re > 250.0) & (ri > 0.05)# & (xp > fig_xmin) & (xp < fig_xmax) & (yp > fig_ymin) & (yp < fig_ymax)
    xps = tmp_xp[cnd]
    yps = tmp_yp[cnd]
    zps = ri[cnd]
    order = np.argsort(zps)
    xps = xps[order]
    yps = yps[order]
    zps = zps[order]

    b = tmp_data[0].astype(np.float32)
    g = tmp_data[1].astype(np.float32)
    r = tmp_data[2].astype(np.float32)
    fact = 10.0
    b = (b*fact/32768.0).clip(0,1)
    g = (g*fact/32768.0).clip(0,1)
    r = (r*fact/32768.0).clip(0,1)
    rgb = np.power(np.dstack((r,g,b)),1.0/2.2)
    fig.clear()
    if tmp_ny > tmp_nx:
        ax1_xw = tmp_nx/tmp_ny
        ax1_yw = 1.0
        ax1_x1 = 0.5-0.5*ax1_xw
        ax1_y1 = 0.0
    else:
        ax1_xw = 1.0
        ax1_yw = tmp_ny/tmp_nx
        ax1_x1 = 0.0
        ax1_y1 = 0.5-0.5*ax1_yw
    ax1 = fig.add_axes((ax1_x1,ax1_y1,ax1_xw,ax1_yw))
    ax1.set_xticks([])
    ax1.set_yticks([])
    #ax1.plot(tmp_xp[::100,::100],tmp_yp[::100,::100],'k.')
    #ax1.imshow(rgb,extent=(tmp_xmin,tmp_xmax,tmp_ymin,tmp_ymax),interpolation='none')
    #ax1.imshow(re,extent=(tmp_xmin,tmp_xmax,tmp_ymin,tmp_ymax),vmin=0,vmax=10,cmap=cm.jet,interpolation='none')
    #"""
    im = ax1.imshow(ri,extent=(tmp_xmin,tmp_xmax,tmp_ymin,tmp_ymax),vmin=0.0,vmax=0.5,cmap=cm.jet,interpolation='none')
    if i_group < -2:
        ax2 = fig.add_axes((ax1_x1+0.05*ax1_xw,ax1_y1+0.02*ax1_yw,0.05,0.4))
    else:
        ax2 = fig.add_axes((ax1_x1+0.84*ax1_xw,ax1_y1+0.02*ax1_yw,0.05,0.4))
    #ax2 = fig.add_axes((0.75,0.55,0.05,0.4))
    ax3 = plt.colorbar(im,cax=ax2,ticks=np.arange(0.0,0.51,0.1))
    ax2.minorticks_on()
    ax2.set_ylabel(r'RI')
    #ax3.outline.set_edgecolor('w')
    #ax2.tick_params(axis='x',which='both',colors='w')
    #ax2.tick_params(axis='y',which='both',colors='w')
    #ax2.yaxis.label.set_color('w')
    #ax2.xaxis.label.set_color('w')
    ax1.scatter(xps,yps,c=zps,vmin=0.0,vmax=0.5,marker='.',cmap=cm.jet)
    ax1.plot(xs,ys,'o',mfc='none',mec='w',ms=10)
    #"""
    #ax1.plot(xg,yg,'ko')
    #ax1.plot(xf,yf,'k:')
    ax1.set_xlim(tmp_xmin,tmp_xmax)
    ax1.set_ylim(tmp_ymin,tmp_ymax)
    plt.savefig(pdf,format='pdf')
    plt.draw()
    plt.pause(0.1)

    #break
pdf.close()
