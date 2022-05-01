#!/usr/bin/env python
import os
import sys
import shutil
import re
import gdal
import numpy as np
from scipy.signal import convolve2d
from subprocess import call
from shapely.geometry import Point,Polygon
from skimage.measure import label,regionprops
from matplotlib.path import Path
import matplotlib.patches as patches
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.patches as mpatches
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib.backends.backend_pdf import PdfPages
from optparse import OptionParser,IndentedHelpFormatter

# Constants
RR_PARAMS = ['Grg','Lrg','Lb','Lg','Lr','Le','Ln','Srg','Sb','Sg','Sr','Se','Sn']
SN_PARAMS = ['Nr','Br']

# Default values
GPS_FNAM = 'gps_points.dat'
FIGNAM = 'drone_extract_points.pdf'
PIXEL_RMAX = 1.0  # m
POINT_SMIN = 0.08 # m
POINT_SMAX = 0.45 # m
POINT_EMAX = 2.0  # sigma
POINT_DMAX = 1.0  # m
POINT_AREA = 0.05 # m2
POINT_NMIN = 5
BUNCH_RMAX = 10.0 # m
BUNCH_EMAX = 2.0  # sigma
BUNCH_NMIN = 5
RR_PARAM = 'Lrg'
SN_PARAM = 'Nr'
RTHR = 1.0
RSTP = 0.01
STHR = 2.0

# Read options
parser = OptionParser(formatter=IndentedHelpFormatter(max_help_position=200,width=200))
parser.add_option('-I','--src_geotiff',default=None,help='Source GeoTIFF name (%default)')
parser.add_option('-O','--dst_geotiff',default=None,help='Destination GeoTIFF name (%default)')
parser.add_option('-g','--gps_fnam',default=GPS_FNAM,help='GPS file name (%default)')
parser.add_option('-e','--ext_fnam',default=None,help='Extract file name (%default)')
parser.add_option('-R','--pixel_rmax',default=PIXEL_RMAX,type='float',help='Maximum pixel distance of a point in m (%default)')
parser.add_option('-m','--point_smin',default=POINT_SMIN,type='float',help='Minimum point size in m (%default)')
parser.add_option('-M','--point_smax',default=POINT_SMAX,type='float',help='Maximum point size in m (%default)')
parser.add_option('-E','--point_emax',default=POINT_EMAX,type='float',help='Maximum distance of a point from the fit line in sigma (%default)')
parser.add_option('-D','--point_dmax',default=POINT_DMAX,type='float',help='Maximum distance of a point from the fit line in m (%default)')
parser.add_option('-a','--point_area',default=POINT_AREA,type='float',help='Standard point area in m2 (%default)')
parser.add_option('-N','--point_nmin',default=POINT_NMIN,type='int',help='Minimum point number in a plot (%default)')
parser.add_option('--bunch_rmax',default=BUNCH_RMAX,type='float',help='Maximum bunch distance in a plot in m (%default)')
parser.add_option('--bunch_emax',default=BUNCH_EMAX,type='float',help='Maximum distance of a bunch from the fit line in sigma (%default)')
parser.add_option('--bunch_nmin',default=BUNCH_NMIN,type='int',help='Minimum bunch number in a plot (%default)')
parser.add_option('-p','--rr_param',default=RR_PARAM,help='Redness ratio parameter (%default)')
parser.add_option('-P','--sn_param',default=SN_PARAM,help='Signal ratio parameter (%default)')
parser.add_option('-t','--rthr',default=RTHR,type='float',help='Max threshold of redness ratio (%default)')
parser.add_option('-r','--rstp',default=RSTP,type='float',help='Threshold step of redness ratio (%default)')
parser.add_option('-T','--sthr',default=STHR,type='float',help='Threshold of signal ratio (%default)')
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

header = None
number_bunch = []
plot_bunch = []
x_bunch = []
y_bunch = []
with open(opts.gps_fnam,'r') as fp:
    #BunchNumber, PlotPaddy, Easting, Northing, DamagedByBLB
    #  1,  1, 751739.0086, 9243034.0783,  1
    for line in fp:
        if len(line) < 1:
            continue
        elif line[0] == '#':
            continue
        elif re.search('[a-zA-Z]',line):
            if header is None:
                header = line # skip header
                continue
            else:
                raise ValueError('Error in reading {} >>> {}'.format(opts.gps_fnam,line))
        item = line.split(sep=',')
        if len(item) < 4:
            continue
        number_bunch.append(int(item[0]))
        plot_bunch.append(int(item[1]))
        x_bunch.append(float(item[2]))
        y_bunch.append(float(item[3]))
number_bunch = np.array(number_bunch)
indx_bunch = np.arange(len(number_bunch))
plot_bunch = np.array(plot_bunch)
x_bunch = np.array(x_bunch)
y_bunch = np.array(y_bunch)

plots = np.unique(plot_bunch)
size_plot = {}
number_plot = {}
inside_plot = {}
removed_plot = {}
for plot in plots:
    cnd = (plot_bunch == plot)
    indx = indx_bunch[cnd]
    size_plot[plot] = len(indx)
    if size_plot[plot] < opts.bunch_nmin:
        raise ValueError('Error, plot={}, size_plot[{}]={} >>> {}'.format(plot,plot,size_plot[plot],opts.gps_fnam))
    number_plot[plot] = number_bunch[indx]
    xg = x_bunch[indx]
    yg = y_bunch[indx]
    indx_member = np.arange(size_plot[plot])
    flag = []
    for i_temp in indx_member:
        cnd = (indx_member != i_temp)
        r = np.sqrt(np.square(xg[cnd]-xg[i_temp])+np.square(yg[cnd]-yg[i_temp]))
        if r.min() > opts.bunch_rmax:
            flag.append(False)
        else:
            flag.append(True)
    flag = np.array(flag)
    inside_plot[plot] = indx[flag]
    removed_plot[plot] = indx[~flag]
    if len(inside_plot[plot]) < opts.bunch_nmin:
        raise ValueError('Error, plot={}, len(inside_plot[{}])={} >>> {}'.format(plot,plot,len(inside_plot[plot]),opts.gps_fnam))

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
    cnd_sn = (sn > opts.sthr)
    # Fit line
    xg_bunch = x_bunch[inside_plot[plot]]
    yg_bunch = y_bunch[inside_plot[plot]]
    xc_bunch = xg_bunch.copy()
    yc_bunch = yg_bunch.copy()
    coef = np.polyfit(xc_bunch,yc_bunch,1)
    dist = np.abs(coef[0]*xc_bunch-yc_bunch+coef[1])/np.sqrt(coef[0]*coef[0]+1)
    cnd = np.abs(dist-dist.mean()) < opts.bunch_emax*dist.std()
    if not np.all(cnd):
        xc_bunch = xc_bunch[cnd]
        yc_bunch = yc_bunch[cnd]
        coef = np.polyfit(xc_bunch,yc_bunch,1)
        dist = np.abs(coef[0]*xc_bunch-yc_bunch+coef[1])/np.sqrt(coef[0]*coef[0]+1)
        cnd = np.abs(dist-dist.mean()) < opts.bunch_emax*dist.std()
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
    prod = (xg_bunch-xo_bunch)*xd_bunch+(yg_bunch-yo_bunch)*yd_bunch
    cnd = (np.diff(prod) < 0.0)
    if cnd.sum() > (~cnd).sum(): # opposite direction
        xd_bunch,yd_bunch = np.negative([xd_bunch,yd_bunch])
    # Search points
    cnd_dist = None
    rthr = opts.rthr
    while True:
        if cnd_dist is None:
            cnd_all = cnd_sn & (rr > rthr)
        else:
            cnd_all = cnd_sn & cnd_dist & (rr > rthr)
        rthr -= opts.rstp
        if cnd_all.sum() < 1:
            continue
        labels,num = label(cnd_all,return_num=True)
        if num < opts.point_nmin:
            continue
        number_point = []
        xmin_point = []
        xmax_point = []
        ymin_point = []
        ymax_point = []
        x_point = []
        y_point = []
        for region in regionprops(labels):
            minr,minc,maxr,maxc = region.bbox
            xmin = rr_xmin+(minc+0.5)*rr_xstp
            xmax = rr_xmin+(maxc-0.5)*rr_xstp
            ymax = rr_ymax+(minr+0.5)*rr_ystp
            ymin = rr_ymax+(maxr-0.5)*rr_ystp
            indy = region.coords[:,0]
            indx = region.coords[:,1]
            x = rr_xmin+(indx+0.5)*rr_xstp
            y = rr_ymax+(indy+0.5)*rr_ystp
            flag = False
            for i_point in range(len(number_point)):
                if (xmax < xmin_point[i_point]-opts.pixel_rmax) or (xmin > xmax_point[i_point]+opts.pixel_rmax) \
                or (ymax < ymin_point[i_point]-opts.pixel_rmax) or (ymin > ymax_point[i_point]+opts.pixel_rmax):
                    continue
                for xtmp,ytmp in zip(x,y):
                    r = np.sqrt(np.square(xtmp-x_point[i_point])+np.square(ytmp-y_point[i_point]))
                    if r.min() < opts.pixel_rmax:
                        number_point[i_point] += region.area
                        xmin_point[i_point] = min(xmin_point[i_point],xmin)
                        xmax_point[i_point] = max(xmax_point[i_point],xmax)
                        ymin_point[i_point] = min(ymin_point[i_point],ymin)
                        ymax_point[i_point] = max(ymax_point[i_point],ymax)
                        x_point[i_point] = np.append(x_point[i_point],x)
                        y_point[i_point] = np.append(y_point[i_point],y)
                        flag = True
                        break
                if flag:
                    break
            if not flag:
                number_point.append(region.area)
                xmin_point.append(xmin)
                xmax_point.append(xmax)
                ymin_point.append(ymin)
                ymax_point.append(ymax)
                x_point.append(x)
                y_point.append(y)
        num = len(number_point)
        if num < opts.point_nmin:
            continue
        indexes_to_be_removed = []
        for i_point in range(len(number_point)):
            xwid = xmax_point[i_point]-xmin_point[i_point]
            ywid = ymax_point[i_point]-ymin_point[i_point]
            if (xwid < opts.point_smin) or (xwid > opts.point_smax) or (ywid < opts.point_smin) or (ywid > opts.point_smax):
                indexes_to_be_removed.append(i_point)
        for indx in sorted(indexes_to_be_removed,reverse=True):
            del number_point[indx]
            del xmin_point[indx]
            del xmax_point[indx]
            del ymin_point[indx]
            del ymax_point[indx]
            del x_point[indx]
            del y_point[indx]
        num = len(number_point)
        if num < opts.point_nmin:
            continue
        xctr_point = np.array([x.mean() for x in x_point])
        yctr_point = np.array([y.mean() for y in y_point])
        xc_point = xctr_point.copy()
        yc_point = yctr_point.copy()
        coef = np.polyfit(xc_point,yc_point,1)
        dist = np.abs(coef[0]*xc_point-yc_point+coef[1])/np.sqrt(coef[0]*coef[0]+1)
        cnd = np.abs(dist-dist.mean()) < opts.point_emax*dist.std()
        if not np.all(cnd):
            xc_point = xc_point[cnd]
            yc_point = yc_point[cnd]
            coef = np.polyfit(xc_point,yc_point,1)
            dist = np.abs(coef[0]*xc_point-yc_point+coef[1])/np.sqrt(coef[0]*coef[0]+1)
            cnd = np.abs(dist-dist.mean()) < opts.point_emax*dist.std()
            if not np.all(cnd):
                xc_point = xc_point[cnd]
                yc_point = yc_point[cnd]
                coef = np.polyfit(xc_point,yc_point,1)
        xf_point = rr_xgrd.copy()
        yf_point = np.polyval(coef,xf_point)
        # Origin
        xo_point = xf_point[0]
        yo_point = yf_point[0]
        # Unit direction vector
        xd_point = xf_point[-1]-xo_point
        yd_point = yf_point[-1]-yo_point
        norm = 1.0/np.sqrt(xd_point*xd_point+yd_point*yd_point)
        xd_point *= norm
        yd_point *= norm
        if (xd_bunch*xd_point+yd_bunch*yd_point) < 0.0: # opposite direction
            xo_point = xf_point[-1]
            yo_point = yf_point[-1]
            xd_point,yd_point = np.negative([xd_point,yd_point])
        indexes_to_be_removed = []
        for i_point in range(len(number_point)):
            dist = np.abs(coef[0]*xctr_point[i_point]-yctr_point[i_point]+coef[1])/np.sqrt(coef[0]*coef[0]+1)
            if dist > opts.point_dmax:
                indexes_to_be_removed.append(i_point)
        for indx in sorted(indexes_to_be_removed,reverse=True):
            del number_point[indx]
            del xmin_point[indx]
            del xmax_point[indx]
            del ymin_point[indx]
            del ymax_point[indx]
            del x_point[indx]
            del y_point[indx]
            xctr_point = np.delete(xctr_point,indx)
            yctr_point = np.delete(yctr_point,indx)
        num = len(number_point)
        if num >= size_plot[plot]:
            if num > size_plot[plot]:
                area_point = np.array(number_point)*np.abs(rr_xstp*rr_ystp)
                indexes_to_be_removed = np.argsort(np.abs(area_point-opts.point_area))[size_plot[plot]:]
                for indx in sorted(indexes_to_be_removed,reverse=True):
                    del number_point[indx]
                    del xmin_point[indx]
                    del xmax_point[indx]
                    del ymin_point[indx]
                    del ymax_point[indx]
                    del x_point[indx]
                    del y_point[indx]
                    xctr_point = np.delete(xctr_point,indx)
                    yctr_point = np.delete(yctr_point,indx)
            break
        else:
            dist = np.abs(coef[0]*rr_xp-rr_yp+coef[1])/np.sqrt(coef[0]*coef[0]+1)
            cnd_dist = (dist < opts.point_dmax)
    rr_copy = rr.copy()
    cnd = cnd_sn & cnd_dist
    rr_copy[~cnd] = np.nan

    if opts.debug:
        fig.clear()
        ax1 = plt.subplot(111)
        ax1.set_xticks([])
        ax1.set_yticks([])
        if opts.ax1_zmin is not None and opts.ax1_zmax is not None:
            im = ax1.imshow(rr_copy,extent=(rr_xmin,rr_xmax,rr_ymin,rr_ymax),vmin=opts.ax1_zmin,vmax=opts.ax1_zmax,cmap=cm.jet,interpolation='none')
        elif opts.ax1_zmin is not None:
            im = ax1.imshow(rr_copy,extent=(rr_xmin,rr_xmax,rr_ymin,rr_ymax),vmin=opts.ax1_zmin,cmap=cm.jet,interpolation='none')
        elif opts.ax1_zmax is not None:
            im = ax1.imshow(rr_copy,extent=(rr_xmin,rr_xmax,rr_ymin,rr_ymax),vmax=opts.ax1_zmax,cmap=cm.jet,interpolation='none')
        else:
            im = ax1.imshow(rr_copy,extent=(rr_xmin,rr_xmax,rr_ymin,rr_ymax),cmap=cm.jet,interpolation='none')
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

        #for i_point in range(len(number_point)):
        #    rect = mpatches.Rectangle((xmin_point[i_point],ymin_point[i_point]),
        #                               xmax_point[i_point]-xmin_point[i_point],
        #                               ymax_point[i_point]-ymin_point[i_point],fill=False,edgecolor='red',linewidth=2)
            #ax1.add_patch(rect)

        ax1.plot(xctr_point,yctr_point,'o',mfc='none',mec='k')
        ax1.plot(xf_point,yf_point,'k:')
        ng = number_plot[plot]
        for ntmp,xtmp,ytmp in zip(ng,xctr_point,yctr_point):
            ax1.text(xtmp,ytmp,'{}'.format(ntmp))
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
    #if plot == 2:
    #    break
if opts.debug:
    pdf.close()
