#!/usr/bin/env python
import os
import gdal
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from mpl_toolkits.axes_grid1 import make_axes_locatable
import zlib # to prevent segmentation fault when saving pdf
from matplotlib.backends.backend_pdf import PdfPages
from optparse import OptionParser,IndentedHelpFormatter

# Constants
OBJECTS = ['BLB','Blast','Borer','Rat','Hopper','Drought']

# Default values
Y_PARAM = ['BLB']
SMAX = [9]
RMAX = 0.01

# Read options
parser = OptionParser(formatter=IndentedHelpFormatter(max_help_position=200,width=200))
parser.add_option('-i','--shp_fnam',default=None,help='Input Shapefile name (%default)')
parser.add_option('-I','--src_geotiff',default=None,help='Source GeoTIFF name (%default)')
parser.add_option('-M','--mask_geotiff',default=None,help='Mask GeoTIFF name (%default)')
parser.add_option('-O','--out_csv',default=None,help='Output CSV name (%default)')
parser.add_option('-o','--out_shp',default=None,help='Output Shapefile name (%default)')
parser.add_option('-y','--y_param',default=None,action='append',help='Objective variable ({})'.format(Y_PARAM))
parser.add_option('-S','--smax',default=None,type='int',action='append',help='Max score ({})'.format(SMAX))
parser.add_option('-r','--rmax',default=RMAX,type='float',help='Maximum exclusion ratio (%default)')
parser.add_option('-F','--fignam',default=None,help='Output figure name for debug (%default)')
parser.add_option('-z','--ax1_zmin',default=None,type='float',action='append',help='Axis1 Z min for debug (%default)')
parser.add_option('-Z','--ax1_zmax',default=None,type='float',action='append',help='Axis1 Z max for debug (%default)')
parser.add_option('-s','--ax1_zstp',default=None,type='float',action='append',help='Axis1 Z stp for debug (%default)')
parser.add_option('-d','--debug',default=False,action='store_true',help='Debug mode (%default)')
parser.add_option('-b','--batch',default=False,action='store_true',help='Batch mode (%default)')
(opts,args) = parser.parse_args()
if opts.y_param is None:
    opts.y_param = Y_PARAM
for param in opts.y_param:
    if not param in OBJECTS:
        raise ValueError('Error, unknown objective variable for y_param >>> {}'.format(param))
if opts.smax is None:
    opts.smax = SMAX
while len(opts.smax) < len(opts.y_param):
    opts.smax.append(opts.smax[-1])
smax = {}
for i,param in enumerate(opts.y_param):
    smax[param] = opts.smax[i]
if opts.ax1_zmin is not None:
    while len(opts.ax1_zmin) < len(opts.y_param):
        opts.ax1_zmin.append(opts.ax1_zmin[-1])
    ax1_zmin = {}
    for i,param in enumerate(opts.y_param):
        ax1_zmin[param] = opts.ax1_zmin[i]
if opts.ax1_zmax is not None:
    while len(opts.ax1_zmax) < len(opts.y_param):
        opts.ax1_zmax.append(opts.ax1_zmax[-1])
    ax1_zmax = {}
    for i,param in enumerate(opts.y_param):
        ax1_zmax[param] = opts.ax1_zmax[i]
if opts.ax1_zstp is not None:
    while len(opts.ax1_zstp) < len(opts.y_param):
        opts.ax1_zstp.append(opts.ax1_zstp[-1])
    ax1_zstp = {}
    for i,param in enumerate(opts.y_param):
        ax1_zstp[param] = opts.ax1_zstp[i]
if opts.out_csv is None or opts.out_shp is None or opts.fignam is None:
    bnam,enam = os.path.splitext(opts.src_geotiff)
    if opts.out_csv is None:
        opts.out_csv = bnam+'_calculate.csv'
    if opts.out_shp is None:
        opts.out_shp = bnam+'_calculate.shp'
    if opts.fignam is None:
        opts.fignam = bnam+'_calculate.pdf'

# Read Source GeoTIFF
ds = gdal.Open(opts.src_geotiff)
src_nx = ds.RasterXSize
src_ny = ds.RasterYSize
src_nb = ds.RasterCount
src_shape = (src_ny,src_nx)
src_prj = ds.GetProjection()
src_trans = ds.GetGeoTransform()
if src_trans[2] != 0.0 or src_trans[4] != 0.0:
    raise ValueError('Error, src_trans={} >>> {}'.format(src_trans,opts.src_geotiff))
src_meta = ds.GetMetadata()
src_data = ds.ReadAsArray().astype(np.float64).reshape(src_nb,src_ny,src_nx)
src_band = []
for iband in range(src_nb):
    band = ds.GetRasterBand(iband+1)
    src_band.append(band.GetDescription())
src_dtype = band.DataType
src_nodata = band.GetNoDataValue()
src_xmin = src_trans[0]
src_xstp = src_trans[1]
src_xmax = src_xmin+src_nx*src_xstp
src_ymax = src_trans[3]
src_ystp = src_trans[5]
src_ymin = src_ymax+src_ny*src_ystp
ds = None
if src_nodata is not None and not np.isnan(src_nodata):
    src_data[src_data == src_nodata] = np.nan

# Read Mask GeoTIFF
ds = gdal.Open(opts.mask_geotiff)
mask_nx = ds.RasterXSize
mask_ny = ds.RasterYSize
mask_nb = ds.RasterCount
if mask_nb != 1:
    raise ValueError('Error, mask_nb={} >>> {}'.format(mask_nb,opts.mask_geotiff))
mask_shape = (mask_ny,mask_nx)
if mask_shape != src_shape:
    raise ValueError('Error, mask_shape={}, src_shape={} >>> {}'.format(mask_shape,src_shape,opts.mask_geotiff))
mask_data = ds.ReadAsArray().reshape(mask_ny,mask_nx)
ds = None

# 

dst_data = []
dst_data = np.array(dst_data)

"""
# For debug
if opts.debug:
    if not opts.batch:
        plt.interactive(True)
    fig = plt.figure(1,facecolor='w',figsize=(5,5))
    plt.subplots_adjust(top=0.9,bottom=0.1,left=0.05,right=0.85)
    pdf = PdfPages(opts.fignam)
    for i,param in enumerate(opts.param):
        fig.clear()
        ax1 = plt.subplot(111)
        ax1.set_xticks([])
        ax1.set_yticks([])
        if opts.ax1_zmin is not None and opts.ax1_zmax is not None:
            im = ax1.imshow(dst_data[i],extent=(src_xmin,src_xmax,src_ymin,src_ymax),vmin=opts.ax1_zmin[i],vmax=opts.ax1_zmax[i],cmap=cm.jet,interpolation='none')
        elif opts.ax1_zmin is not None:
            im = ax1.imshow(dst_data[i],extent=(src_xmin,src_xmax,src_ymin,src_ymax),vmin=opts.ax1_zmin[i],cmap=cm.jet,interpolation='none')
        elif opts.ax1_zmax is not None:
            im = ax1.imshow(dst_data[i],extent=(src_xmin,src_xmax,src_ymin,src_ymax),vmax=opts.ax1_zmax[i],cmap=cm.jet,interpolation='none')
        else:
            im = ax1.imshow(dst_data[i],extent=(src_xmin,src_xmax,src_ymin,src_ymax),cmap=cm.jet,interpolation='none')
        divider = make_axes_locatable(ax1)
        cax = divider.append_axes('right',size='5%',pad=0.05)
        if opts.ax1_zstp is not None:
            if opts.ax1_zmin is not None:
                zmin = min((np.floor(np.nanmin(dst_data[i])/opts.ax1_zstp[i])-1.0)*opts.ax1_zstp[i],opts.ax1_zmin[i])
            else:
                zmin = (np.floor(np.nanmin(dst_data[i])/opts.ax1_zstp[i])-1.0)*opts.ax1_zstp[i]
            if opts.ax1_zmax is not None:
                zmax = max(np.nanmax(dst_data[i]),opts.ax1_zmax[i]+0.1*opts.ax1_zstp[i])
            else:
                zmax = np.nanmax(dst_data[i])+0.1*opts.ax1_zstp[i]
            ax2 = plt.colorbar(im,cax=cax,ticks=np.arange(zmin,zmax,opts.ax1_zstp[i])).ax
        else:
            ax2 = plt.colorbar(im,cax=cax).ax
        ax2.minorticks_on()
        ax2.set_ylabel(pnams[i])
        ax2.yaxis.set_label_coords(3.5,0.5)
        if opts.remove_nan:
            src_indy,src_indx = np.indices(src_shape)
            src_xp = src_trans[0]+(src_indx+0.5)*src_trans[1]+(src_indy+0.5)*src_trans[2]
            src_yp = src_trans[3]+(src_indx+0.5)*src_trans[4]+(src_indy+0.5)*src_trans[5]
            cnd = ~np.isnan(dst_data[i])
            xp = src_xp[cnd]
            yp = src_yp[cnd]
            fig_xmin = xp.min()
            fig_xmax = xp.max()
            fig_ymin = yp.min()
            fig_ymax = yp.max()
        else:
            fig_xmin = src_xmin
            fig_xmax = src_xmax
            fig_ymin = src_ymin
            fig_ymax = src_ymax
        ax1.set_xlim(fig_xmin,fig_xmax)
        ax1.set_ylim(fig_ymin,fig_ymax)
        plt.savefig(pdf,format='pdf')
        if not opts.batch:
            plt.draw()
    pdf.close()
"""
