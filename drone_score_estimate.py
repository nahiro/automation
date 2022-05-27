#!/usr/bin/env python
import os
import zlib # import zlib before gdal to prevent segmentation fault when saving pdf
import gdal
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib.backends.backend_pdf import PdfPages
from optparse import OptionParser,IndentedHelpFormatter

# Constants
OBJECTS = ['BLB','Blast','Borer','Rat','Hopper','Drought']

# Default values
Y_PARAM = ['BLB']
Y_NUMBER = [1]
SMAX = [9]
SINT = [2]

# Read options
parser = OptionParser(formatter=IndentedHelpFormatter(max_help_position=200,width=200))
parser.add_option('-i','--inp_fnam',default=None,help='Input formula file name (%default)')
parser.add_option('-I','--src_geotiff',default=None,help='Source GeoTIFF name (%default)')
parser.add_option('-O','--dst_geotiff',default=None,help='Destination GeoTIFF name (%default)')
parser.add_option('-y','--y_param',default=None,action='append',help='Objective variable ({})'.format(Y_PARAM))
parser.add_option('--y_number',default=None,type='int',action='append',help='Formula number ({})'.format(Y_NUMBER))
parser.add_option('-M','--smax',default=None,type='int',action='append',help='Max score ({})'.format(SMAX))
parser.add_option('-S','--sint',default=None,type='int',action='append',help='Sampling interval for digitizing score ({})'.format(SINT))
parser.add_option('-F','--fignam',default=None,help='Output figure name for debug (%default)')
parser.add_option('-z','--ax1_zmin',default=None,type='float',action='append',help='Axis1 Z min for debug (%default)')
parser.add_option('-Z','--ax1_zmax',default=None,type='float',action='append',help='Axis1 Z max for debug (%default)')
parser.add_option('-s','--ax1_zstp',default=None,type='float',action='append',help='Axis1 Z stp for debug (%default)')
parser.add_option('-n','--remove_nan',default=False,action='store_true',help='Remove nan for debug (%default)')
parser.add_option('-D','--digitize',default=False,action='store_true',help='Digitize score (%default)')
parser.add_option('-d','--debug',default=False,action='store_true',help='Debug mode (%default)')
parser.add_option('-b','--batch',default=False,action='store_true',help='Batch mode (%default)')
(opts,args) = parser.parse_args()
if opts.y_param is None:
    opts.y_param = Y_PARAM
for param in opts.y_param:
    if not param in OBJECTS:
        raise ValueError('Error, unknown objective variable for y_param >>> {}'.format(param))
if opts.y_number is None:
    opts.y_number = Y_NUMBER
while len(opts.y_number) < len(opts.y_param):
    opts.y_number.append(opts.y_number[-1])
y_number = {}
for i,param in enumerate(opts.y_param):
    y_number[param] = opts.y_number[i]
if opts.smax is None:
    opts.smax = SMAX
while len(opts.smax) < len(opts.y_param):
    opts.smax.append(opts.smax[-1])
smax = {}
for i,param in enumerate(opts.y_param):
    smax[param] = opts.smax[i]
if opts.sint is None:
    opts.sint = SINT
while len(opts.sint) < len(opts.y_param):
    opts.sint.append(opts.sint[-1])
sint = {}
for i,param in enumerate(opts.y_param):
    sint[param] = opts.sint[i]
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
if opts.dst_geotiff is None or opts.fignam is None:
    bnam,enam = os.path.splitext(opts.src_geotiff)
    if opts.dst_geotiff is None:
        opts.dst_geotiff = bnam+'_estimate'+enam
    if opts.fignam is None:
        opts.fignam = bnam+'_estimate.pdf'

df = pd.read_csv(opts.inp_fnam,comment='#')
df.columns = df.columns.str.strip()
df['Y'] = df['Y'].str.strip()
nmax = df['N'].max()+1
for n in range(nmax):
    p = 'P{}_param'.format(n)
    if not p in df.columns:
        raise ValueError('Error in finding column for {} >>> {}'.format(p,opts.inp_fnam))
    df[p] = df[p].str.strip()
    p = 'P{}_value'.format(n)
    if not p in df.columns:
        raise ValueError('Error in finding column for {} >>> {}'.format(p,opts.inp_fnam))
    df[p] = df[p].astype(float)

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

# Calculate damage intensity
dst_nx = src_nx
dst_ny = src_ny
dst_nb = len(opts.y_param)
dst_shape = (dst_ny,dst_nx)
dst_data = np.full((dst_nb,dst_ny,dst_nx),0.0)
dst_band = opts.y_param
for y_param in opts.y_param:
    dst_iband = dst_band.index(y_param)
    cnd = (df['Y'] == y_param)
    if cnd.sum() < y_number[y_param]:
        raise ValueError('Error in finding formula for {} >>> {}'.format(y_param,opts.inp_fnam))
    formula = df[cnd].iloc[y_number[y_param]-1]
    for n in range(nmax):
        p = 'P{}_param'.format(n)
        param = formula[p]
        param_low = param.lower()
        p = 'P{}_value'.format(n)
        coef = formula[p]
        if param_low == 'none':
            continue
        elif param_low == 'const':
            dst_data[dst_iband] += coef
        else:
            if not param in src_band:
                raise ValueError('Error in finding {} in {}'.format(param,opts.src_geotiff))
            src_iband = src_band.index(param)
            dst_data[dst_iband] += coef*src_data[src_iband]

# Convert damage intensity to score
for y_param in opts.y_param:
    if smax[y_param] != 1:
        iband = dst_band.index(y_param)
        dst_data[iband] *= smax[y_param]

# Digitize score
if opts.digitize:
    data = np.full(dst_data.shape,-1).astype(np.int16)
    for y_param in opts.y_param:
        iband = dst_band.index(y_param)
        cnd1 = np.full(dst_shape,True)
        for score in range(smax[y_param],0,-sint[y_param]):
            s_next = score-sint[y_param]
            if s_next < 0:
                s_next = 0
            s = 0.5*(score+s_next)
            cnd2 = dst_data[iband] > s
            data[iband,(cnd1 & cnd2)] = score
            cnd1[cnd2] = False
        data[iband,cnd1] = 0
        data[iband,np.isnan(dst_data[iband])] = -1
    dst_data = data

# Write Destination GeoTIFF
dst_prj = src_prj
dst_trans = src_trans
dst_meta = src_meta
if opts.digitize:
    dst_dtype = gdal.GDT_Int16
    dst_nodata = -1
else:
    dst_dtype = gdal.GDT_Float32
    dst_nodata = np.nan
drv = gdal.GetDriverByName('GTiff')
ds = drv.Create(opts.dst_geotiff,dst_nx,dst_ny,dst_nb,dst_dtype)
ds.SetProjection(dst_prj)
ds.SetGeoTransform(dst_trans)
ds.SetMetadata(dst_meta)
for iband in range(dst_nb):
    band = ds.GetRasterBand(iband+1)
    band.WriteArray(dst_data[iband])
    band.SetDescription(dst_band[iband])
band.SetNoDataValue(dst_nodata) # The TIFFTAG_GDAL_NODATA only support one value per dataset
ds.FlushCache()
ds = None # close dataset

# For debug
if opts.debug:
    if not opts.batch:
        plt.interactive(True)
    fig = plt.figure(1,facecolor='w',figsize=(5,5))
    plt.subplots_adjust(top=0.9,bottom=0.1,left=0.05,right=0.80)
    pdf = PdfPages(opts.fignam)
    for param in opts.y_param:
        iband = dst_band.index(param)
        if smax[param] == 1:
            data = dst_data[iband]*100.0
            title = '{} Intensity (%)'.format(param)
        else:
            data = dst_data[iband].astype(np.float32)
            title = '{} Score'.format(param)
        if opts.digitize:
            data[dst_data[iband] == -1] = np.nan
        fig.clear()
        ax1 = plt.subplot(111)
        ax1.set_xticks([])
        ax1.set_yticks([])
        if opts.ax1_zmin is not None and opts.ax1_zmax is not None:
            im = ax1.imshow(data,extent=(src_xmin,src_xmax,src_ymin,src_ymax),vmin=ax1_zmin[param],vmax=ax1_zmax[param],cmap=cm.jet,interpolation='none')
        elif opts.ax1_zmin is not None:
            im = ax1.imshow(data,extent=(src_xmin,src_xmax,src_ymin,src_ymax),vmin=ax1_zmin[param],cmap=cm.jet,interpolation='none')
        elif opts.ax1_zmax is not None:
            im = ax1.imshow(data,extent=(src_xmin,src_xmax,src_ymin,src_ymax),vmax=ax1_zmax[param],cmap=cm.jet,interpolation='none')
        else:
            im = ax1.imshow(data,extent=(src_xmin,src_xmax,src_ymin,src_ymax),cmap=cm.jet,interpolation='none')
        divider = make_axes_locatable(ax1)
        cax = divider.append_axes('right',size='5%',pad=0.05)
        if opts.ax1_zstp is not None:
            if opts.ax1_zmin is not None:
                zmin = min((np.floor(np.nanmin(data)/ax1_zstp[param])-1.0)*ax1_zstp[param],ax1_zmin[param])
            else:
                zmin = (np.floor(np.nanmin(data)/ax1_zstp[param])-1.0)*ax1_zstp[param]
            if opts.ax1_zmax is not None:
                zmax = max(np.nanmax(data),ax1_zmax[param]+0.1*ax1_zstp[param])
            else:
                zmax = np.nanmax(data)+0.1*ax1_zstp[param]
            ax2 = plt.colorbar(im,cax=cax,ticks=np.arange(zmin,zmax,ax1_zstp[param])).ax
        else:
            ax2 = plt.colorbar(im,cax=cax).ax
        ax2.minorticks_on()
        ax2.set_ylabel(title)
        ax2.yaxis.set_label_coords(4.5,0.5)
        if opts.remove_nan:
            src_indy,src_indx = np.indices(src_shape)
            src_xp = src_trans[0]+(src_indx+0.5)*src_trans[1]+(src_indy+0.5)*src_trans[2]
            src_yp = src_trans[3]+(src_indx+0.5)*src_trans[4]+(src_indy+0.5)*src_trans[5]
            cnd = ~np.isnan(data)
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
