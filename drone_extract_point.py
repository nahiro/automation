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
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib.backends.backend_pdf import PdfPages
from optparse import OptionParser,IndentedHelpFormatter

# Constants
RR_PARAMS = ['Grg','Lrg','Lb','Lg','Lr','Le','Ln','Srg','Sb','Sg','Sr','Se','Sn']
SN_PARAMS = ['Nr','Br']

# Default values
GPS_FNAM = 'gps_points.dat'
FIGNAM = 'drone_extract_points.pdf'
RMAX = 10.0 # m
NMIN = 5
RR_PARAM = 'Lrg'
SN_PARAM = 'Nr'
RTHR = 0.1
STHR = 2.0
RSTP = 0.01

# Read options
parser = OptionParser(formatter=IndentedHelpFormatter(max_help_position=200,width=200))
parser.add_option('-I','--src_geotiff',default=None,help='Source GeoTIFF name (%default)')
parser.add_option('-O','--dst_geotiff',default=None,help='Destination GeoTIFF name (%default)')
parser.add_option('-g','--gps_fnam',default=GPS_FNAM,help='GPS file name (%default)')
parser.add_option('-e','--ext_fnam',default=None,help='Extract file name (%default)')
parser.add_option('-R','--rmax',default=RMAX,type='float',help='Maximum distance in m (%default)')
parser.add_option('-N','--nmin',default=NMIN,type='int',help='Minimum number (%default)')
parser.add_option('-p','--rr_param',default=RR_PARAM,help='Redness ratio parameter (%default)')
parser.add_option('-P','--sn_param',default=SN_PARAM,help='Signal ratio parameter (%default)')
parser.add_option('-t','--rthr',default=RTHR,type='float',help='Threshold of redness ratio (%default)')
parser.add_option('-T','--sthr',default=STHR,type='float',help='Threshold of signal ratio (%default)')
parser.add_option('-r','--rstp',default=RSTP,type='float',help='Threshold step of redness ratio (%default)')
parser.add_option('-F','--fignam',default=FIGNAM,help='Output figure name (%default)')
parser.add_option('-z','--ax1_zmin',default=None,type='float',help='Axis1 Z min for debug (%default)')
parser.add_option('-Z','--ax1_zmax',default=None,type='float',help='Axis1 Z max for debug (%default)')
parser.add_option('-s','--ax1_zstp',default=None,type='float',help='Axis1 Z stp for debug (%default)')
parser.add_option('-n','--remove_nan',default=False,action='store_true',help='Remove nan for debug (%default)')
parser.add_option('-d','--debug',default=False,action='store_true',help='Debug mode (%default)')
(opts,args) = parser.parse_args()
if not opts.rr_param in RR_PARAMS:
    raise ValueError('Error, unknown redness ratio parameter >>> {}'.format(opts.rr_param))
if not opts.sn_param in SN_PARAMS:
    raise ValueError('Error, unknown signal to noise parameter >>> {}'.format(opts.sn_param))

number_bunch = []
plot_bunch = []
x_bunch = []
y_bunch = []
with open(opts.gps_fnam,'r') as fp:
    #BunchNumber, PlotPaddy, Easting, Northing, DamagedByBLB
    #  1,  1, 751739.0086, 9243034.0783,  1
    line = fp.readline() # skip header
    for line in fp:
        item = line.split(sep=',')
        if len(item) < 4:
            continue
        number_bunch.append(int(item[0]))
        plot_bunch.append(int(item[1]))
        x_bunch.append(float(item[2]))
        y_bunch.append(float(item[3]))
number_bunch = np.array(number_bunch)
plot_bunch = np.array(plot_bunch)
x_bunch = np.array(x_bunch)
y_bunch = np.array(y_bunch)
index_bunch = np.arange(len(number_bunch))

plots = np.unique(plot_bunch)
groups = {}
groups_removed = {}
for plot in plots:
    cnd = (plot_bunch == plot)
    if cnd.sum() < opts.nmin:
        raise ValueError('Error, plot={}, cnd.sum()={} >>> {}'.format(plot,cnd.sum(),opts.gps_fnam))
    indx = index_bunch[cnd]
    ng = len(indx)
    xg = x_bunch[indx]
    yg = y_bunch[indx]
    index_member = np.arange(ng)
    flag = []
    for i_temp in index_member:
        cnd = (index_member != i_temp)
        r = np.sqrt(np.square(xg[cnd]-xg[i_temp])+np.square(yg[cnd]-yg[i_temp]))
        if r.min() > opts.rmax:
            flag.append(False)
        else:
            flag.append(True)
    flag = np.array(flag)
    groups[plot] = indx[flag]
    groups_removed[plot] = indx[~flag]
    if len(groups[plot]) < opts.nmin:
        raise ValueError('Error, plot={}, len(groups[{}])={} >>> {}'.format(plot,len(groups[plot]),opts.gps_fnam))

if opts.debug:
    plt.interactive(True)
    fig = plt.figure(1,facecolor='w',figsize=(5,5))
    plt.subplots_adjust(top=0.9,bottom=0.1,left=0.05,right=0.85)
    pdf = PdfPages(opts.fignam)
bnam,enam = os.path.splitext(opts.src_geotiff)
for plot in plots:
    # Read redness ratio image
    onam = bnam+'_plot{}_{}'.format(plot,opts.rr_param)+enam
    ds = gdal.Open(onam)
    rr_nx = ds.RasterXSize
    rr_ny = ds.RasterYSize
    rr_nb = ds.RasterCount
    if rr_nb != 1:
        raise ValueError('Error, rr_nb={} >>> {}'.format(rr_nb,onam))
    rr_shape = (rr_ny,rr_nx)
    rr_trans = ds.GetGeoTransform()
    if rr_trans[2] != 0.0 or rr_trans[4] != 0.0:
        raise ValueError('Error, rr_trans={}'.format(rr_trans))
    rr = ds.ReadAsArray().reshape(rr_ny,rr_nx)
    rr_xmin = rr_trans[0]
    rr_xstp = rr_trans[1]
    rr_ymax = rr_trans[3]
    rr_ystp = rr_trans[5]
    rr_xmax = rr_xmin+rr_nx*rr_xstp
    rr_ymin = rr_ymax+rr_ny*rr_ystp
    rr_xgrd = rr_xmin+(np.arange(rr_nx)+0.5)*rr_xstp
    rr_ygrd = rr_ymax+(np.arange(rr_ny)+0.5)*rr_ystp
    ds = None
    rr_indy,rr_indx = np.indices(rr_shape)
    rr_xp = rr_trans[0]+(rr_indx+0.5)*rr_trans[1]+(rr_indy+0.5)*rr_trans[2]
    rr_yp = rr_trans[3]+(rr_indx+0.5)*rr_trans[4]+(rr_indy+0.5)*rr_trans[5]
    # Read signal ratio image
    onam = bnam+'_plot{}_{}'.format(plot,opts.sn_param)+enam
    ds = gdal.Open(onam)
    sn_nx = ds.RasterXSize
    sn_ny = ds.RasterYSize
    sn_nb = ds.RasterCount
    if sn_nb != 1:
        raise ValueError('Error, sn_nb={} >>> {}'.format(sn_nb,onam))
    sn_shape = (sn_ny,sn_nx)
    if sn_shape != rr_shape:
        raise ValueError('Error, sn_shape={}, rr_shape={} >>> {}'.format(sn_shape,rr_shape,onam))
    sn = ds.ReadAsArray().reshape(sn_ny,sn_nx)
    # Fit line
    xg_bunch = x_bunch[groups[plot]]
    yg_bunch = y_bunch[groups[plot]]
    xc_bunch = xg_bunch.copy()
    yc_bunch = yg_bunch.copy()
    coef = np.polyfit(xc_bunch,yc_bunch,1)
    dist = np.abs(coef[0]*xc_bunch-yc_bunch+coef[1])/np.sqrt(coef[0]*coef[0]+1)
    cnd = np.abs(dist-dist.mean()) < 2.0*dist.std()
    if not np.all(cnd):
        xc_bunch = xc_bunch[cnd]
        yc_bunch = yc_bunch[cnd]
        coef = np.polyfit(xc_bunch,yc_bunch,1)
        dist = np.abs(coef[0]*xc_bunch-yc_bunch+coef[1])/np.sqrt(coef[0]*coef[0]+1)
        cnd = np.abs(dist-dist.mean()) < 2.0*dist.std()
        if not np.all(cnd):
            xc_bunch = xc_bunch[cnd]
            yc_bunch = yc_bunch[cnd]
            coef = np.polyfit(xc_bunch,yc_bunch,1)
    xf_bunch = rr_xgrd.copy()
    yf_bunch = np.polyval(coef,xf_bunch)
    # Origin
    xo_bunch = xf_bunch[0]
    yo_bunch = yf_bunch[0]
    # Unit direction vector
    xd_bunch = xf_bunch[-1]-xo_bunch
    yd_bunch = yf_bunch[-1]-yo_bunch
    norm = 1.0/np.sqrt(xd_bunch*xd_bunch+yd_bunch*yd_bunch)
    xd_bunch *= norm
    yd_bunch *= norm
    #
    rr_point = rr.copy()
    cnd = (rr < opts.rthr) | (sn < opts.sthr)
    rr_point[cnd] = np.nan

    if opts.debug:
        fig.clear()
        ax1 = plt.subplot(111)
        ax1.set_xticks([])
        ax1.set_yticks([])
        if opts.ax1_zmin is not None and opts.ax1_zmax is not None:
            im = ax1.imshow(rr_point,extent=(rr_xmin,rr_xmax,rr_ymin,rr_ymax),vmin=opts.ax1_zmin,vmax=opts.ax1_zmax,cmap=cm.jet,interpolation='none')
        elif opts.ax1_zmin is not None:
            im = ax1.imshow(rr_point,extent=(rr_xmin,rr_xmax,rr_ymin,rr_ymax),vmin=opts.ax1_zmin,cmap=cm.jet,interpolation='none')
        elif opts.ax1_zmax is not None:
            im = ax1.imshow(rr_point,extent=(rr_xmin,rr_xmax,rr_ymin,rr_ymax),vmax=opts.ax1_zmax,cmap=cm.jet,interpolation='none')
        else:
            im = ax1.imshow(rr_point,extent=(rr_xmin,rr_xmax,rr_ymin,rr_ymax),cmap=cm.jet,interpolation='none')
        divider = make_axes_locatable(ax1)
        cax = divider.append_axes('right',size='5%',pad=0.05)
        if opts.ax1_zstp is not None:
            if opts.ax1_zmin is not None:
                zmin = min((np.floor(np.nanmin(rr)/opts.ax1_zstp)-1.0)*opts.ax1_zstp,opts.ax1_zmin)
            else:
                zmin = (np.floor(np.nanmin(rr)/opts.ax1_zstp)-1.0)*opts.ax1_zstp
            if opts.ax1_zmax is not None:
                zmax = max(np.nanmax(rr),opts.ax1_zmax+0.1*opts.ax1_zstp)
            else:
                zmax = np.nanmax(rr)+0.1*opts.ax1_zstp
            ax2 = plt.colorbar(im,cax=cax,ticks=np.arange(zmin,zmax,opts.ax1_zstp)).ax
        else:
            ax2 = plt.colorbar(im,cax=cax).ax
        ax2.minorticks_on()
        ax2.set_ylabel(opts.rr_param)
        ax2.yaxis.set_label_coords(3.5,0.5)
        #ax1.plot(xg_bunch,yg_bunch,'o',mfc='none',mec='k')
        #ax1.plot(xf_bunch,yf_bunch,'k:')
        #ng = number_bunch[groups[plot]]
        #for ntmp,xtmp,ytmp in zip(ng,xg_bunch,yg_bunch):
        #    ax1.text(xtmp,ytmp,'{}'.format(ntmp))
        if opts.remove_nan:
            cnd = ~np.isnan(rr)
            xp = rr_xp[cnd]
            yp = rr_yp[cnd]
            fig_xmin = xp.min()
            fig_xmax = xp.max()
            fig_ymin = yp.min()
            fig_ymax = yp.max()
        else:
            fig_xmin = rr_xmin
            fig_xmax = rr_xmax
            fig_ymin = rr_ymin
            fig_ymax = rr_ymax
        ax1.set_xlim(fig_xmin,fig_xmax)
        ax1.set_ylim(fig_ymin,fig_ymax)
        plt.savefig(pdf,format='pdf')
        plt.draw()
        plt.pause(0.1)
if opts.debug:
    pdf.close()
