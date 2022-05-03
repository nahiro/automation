#!/usr/bin/env python
import os
import gdal
import numpy as np
from scipy.signal import convolve2d
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from mpl_toolkits.axes_grid1 import make_axes_locatable
from optparse import OptionParser,IndentedHelpFormatter

# Constants
PARAMS = ['Grg','Lrg','Lb','Lg','Lr','Le','Ln','Srg','Sb','Sg','Sr','Se','Sn','Nr','Br']
bands = {}
bands['b'] = 'Blue'
bands['g'] = 'Green'
bands['r'] = 'Red'
bands['e'] = 'RedEdge'
bands['n'] = 'NIR'
band_index = {}
band_index['b'] = 0
band_index['g'] = 1
band_index['r'] = 2
band_index['e'] = 3
band_index['n'] = 4

# Default values
PARAM = ['Lrg','Nr']
INNER_SIZE = 29 # pixel
OUTER_SIZE = 35 # pixel

# Read options
parser = OptionParser(formatter=IndentedHelpFormatter(max_help_position=200,width=200))
parser.add_option('-I','--src_geotiff',default=None,help='Source GeoTIFF name (%default)')
parser.add_option('-O','--dst_geotiff',default=None,help='Destination GeoTIFF name (%default)')
parser.add_option('-p','--param',default=None,help='Output parameter ({})'.format(PARAM))
parser.add_option('--data_min',default=None,type='float',help='Minimum data value (%default)')
parser.add_option('--data_max',default=None,type='float',help='Maximum data value (%default)')
parser.add_option('-i','--inner_size',default=INNER_SIZE,type='int',help='Inner region size in pixel (%default)')
parser.add_option('-o','--outer_size',default=OUTER_SIZE,type='int',help='Outer region size in pixel (%default)')
parser.add_option('-F','--fignam',default=None,help='Output figure name for debug (%default)')
parser.add_option('-z','--ax1_zmin',default=None,type='float',help='Axis1 Z min for debug (%default)')
parser.add_option('-Z','--ax1_zmax',default=None,type='float',help='Axis1 Z max for debug (%default)')
parser.add_option('-s','--ax1_zstp',default=None,type='float',help='Axis1 Z stp for debug (%default)')
parser.add_option('-n','--remove_nan',default=False,action='store_true',help='Remove nan for debug (%default)')
parser.add_option('-d','--debug',default=False,action='store_true',help='Debug mode (%default)')
(opts,args) = parser.parse_args()
if opts.param is None:
    opts.param = PARAM
if not opts.param in PARAMS:
    raise ValueError('Error, unknown parameter >>> {}'.format(opts.param))
if opts.dst_geotiff is None or opts.fignam is None:
    bnam,enam = os.path.splitext(opts.src_geotiff)
    if opts.dst_geotiff is None:
        opts.dst_geotiff = bnam+'_{}'.format(opts.param)+enam
    if opts.fignam is None:
        opts.fignam = bnam+'_{}'.format(opts.param)+'.pdf'

filt1 = np.ones((opts.outer_size,opts.outer_size))
norm = filt1.sum()
filt1 *= 1.0/norm

filt2 = np.ones((opts.inner_size,opts.inner_size))
norm = filt2.sum()
filt2 *= 1.0/norm

def calc_vpix(data,band):
    vpix = data[band_index[band]].copy()
    if opts.data_min is not None:
        vpix[vpix < opts.data_min] = np.nan
    return vpix

def calc_vout(vpix):
    cnv1 = convolve2d(vpix,filt1,mode='same')
    cnv2 = convolve2d(vpix,filt2,mode='same')
    vout = (cnv1*filt1.size-cnv2*filt2.size)/(filt1.size-filt2.size)
    return vout

def calc_sn(vpix,vout):
    vpix2 = np.square(vpix)
    cnv1 = convolve2d(vpix2,filt1,mode='same')
    cnv2 = convolve2d(vpix2,filt2,mode='same')
    vout2 = (cnv1*filt1.size-cnv2*filt2.size)/(filt1.size-filt2.size)
    sn = (vpix-vout)/np.sqrt(vout2-vout*vout)
    return sn

def calc_sb(vpix,vout):
    sb = (vpix-vout)/vout
    return sb

# Read Source GeoTIFF
ds = gdal.Open(opts.src_geotiff)
src_nx = ds.RasterXSize
src_ny = ds.RasterYSize
src_nb = ds.RasterCount
if src_nb != len(bands):
    raise ValueError('Error, src_nb={}, len(bands)={} >>> {}'.format(src_nb,len(bands),opts.src_geotiff))
src_prj = ds.GetProjection()
src_trans = ds.GetGeoTransform()
if src_trans[2] != 0.0 or src_trans[4] != 0.0:
    raise ValueError('Error, src_trans={} >>> {}'.format(src_trans,opts.src_geotiff))
src_meta = ds.GetMetadata()
src_data = ds.ReadAsArray().astype(np.float64).reshape(src_nb,src_ny,src_nx)
if opts.data_min is not None:
    cnd = src_data < opts.data_min
    src_data[cnd] = np.nan
if opts.data_max is not None:
    cnd = src_data > opts.data_max
    src_data[cnd] = np.nan
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

fnam = opts.src_geotiff
data_shape = (src_ny,src_nx)
value_pix = {}
value_out = {}
band1 = 'r'
band2 = 'g'
if not band1 in value_pix:
    value_pix[band1] = calc_vpix(src_data,band1)
red = value_pix[band1]
if red.shape != data_shape:
    raise ValueError('Error, red.shape={}, data_shape={} >>> {}'.format(red.shape,data_shape,fnam))
if not band2 in value_pix:
    value_pix[band2] = calc_vpix(src_data,band2)
green = value_pix[band2]
if green.shape != data_shape:
    raise ValueError('Error, green.shape={}, data_shape={} >>> {}'.format(green.shape,data_shape,fnam))
if opts.param[0] == 'L':
    if len(opts.param) == 2:
        band1 = opts.param[1]
        pnam = 'Redness Ratio (Local {})'.format(bands[band1])
        if not band1 in value_pix:
            value_pix[band1] = calc_vpix(src_data,band1)
        if not band1 in value_out:
            value_out[band1] = calc_vout(value_pix[band1])
        norm = value_out[band1]
        if norm.shape != data_shape:
            raise ValueError('Error, norm.shape={}, data_shape={} >>> {}'.format(norm.shape,data_shape,fnam))
    elif len(opts.param) == 3:
        band1 = opts.param[1]
        band2 = opts.param[2]
        pnam = 'Redness Ratio (Local {} + {})'.format(bands[band1],bands[band2])
        if not band1 in value_pix:
            value_pix[band1] = calc_vpix(src_data,band1)
        if not band1 in value_out:
            value_out[band1] = calc_vout(value_pix[band1])
        norm1 = value_out[band1]
        if norm1.shape != data_shape:
            raise ValueError('Error, norm1.shape={}, data_shape={} >>> {}'.format(norm1.shape,data_shape,fnam))
        if not band2 in value_pix:
            value_pix[band2] = calc_vpix(src_data,band2)
        if not band2 in value_out:
            value_out[band2] = calc_vout(value_pix[band2])
        norm2 = value_out[band2]
        if norm2.shape != data_shape:
            raise ValueError('Error, norm2.shape={}, data_shape={} >>> {}'.format(norm2.shape,data_shape,fnam))
        norm = norm1+norm2
    else:
        raise ValueError('Error, len(opts.param)={} >>> {}'.format(len(opts.param),opts.param))
elif opts.param[0] == 'G':
    if len(opts.param) == 2:
        band1 = opts.param[1]
        pnam = 'Redness Ratio (Global {})'.format(bands[band1])
        if not band1 in value_pix:
            value_pix[band1] = calc_vpix(src_data,band1)
        norm1 = value_pix[band1]
        if norm1.shape != data_shape:
            raise ValueError('Error, norm1.shape={}, data_shape={} >>> {}'.format(norm1.shape,data_shape,fnam))
        norm = norm1[cnd_all].mean()
    elif len(opts.param) == 3:
        band1 = opts.param[1]
        band2 = opts.param[2]
        pnam = 'Redness Ratio (Global {} + {})'.format(bands[band1],bands[band2])
        if not band1 in value_pix:
            value_pix[band1] = calc_vpix(src_data,band1)
        norm1 = value_pix[band1]
        if norm1.shape != data_shape:
            raise ValueError('Error, norm1.shape={}, data_shape={} >>> {}'.format(norm1.shape,data_shape,fnam))
        if not band2 in value_pix:
            value_pix[band2] = calc_vpix(src_data,band2)
        norm2 = value_pix[band2]
        if norm2.shape != data_shape:
            raise ValueError('Error, norm2.shape={}, data_shape={} >>> {}'.format(norm2.shape,data_shape,fnam))
        norm = norm1[cnd_all].mean()+norm2[cnd_all].mean()
    else:
        raise ValueError('Error, len(opts.param)={} >>> {}'.format(len(opts.param),opts.param))
elif opts.param[0] == 'S':
    if len(opts.param) == 2:
        band1 = opts.param[1]
        pnam = 'Redness Ratio ({})'.format(bands[band1])
        if not band1 in value_pix:
            value_pix[band1] = calc_vpix(src_data,band1)
        norm = value_pix[band1]
        if norm.shape != data_shape:
            raise ValueError('Error, norm.shape={}, data_shape={} >>> {}'.format(norm.shape,data_shape,fnam))
    elif len(opts.param) == 3:
        band1 = opts.param[1]
        band2 = opts.param[2]
        pnam = 'Redness Ratio ({} + {})'.format(bands[band1],bands[band2])
        if not band1 in value_pix:
            value_pix[band1] = calc_vpix(src_data,band1)
        norm1 = value_pix[band1]
        if norm1.shape != data_shape:
            raise ValueError('Error, norm1.shape={}, data_shape={} >>> {}'.format(norm1.shape,data_shape,fnam))
        if not band2 in value_pix:
            value_pix[band2] = calc_vpix(src_data,band2)
        norm2 = value_pix[band2]
        if norm2.shape != data_shape:
            raise ValueError('Error, norm2.shape={}, data_shape={} >>> {}'.format(norm2.shape,data_shape,fnam))
        norm = norm1+norm2
    else:
        raise ValueError('Error, len(opts.param)={} >>> {}'.format(len(opts.param),opts.param))
elif opts.param[0] == 'N':
    if len(opts.param) == 2:
        band1 = opts.param[1]
        pnam = 'S/N Ratio ({})'.format(bands[band1])
        if not band1 in value_pix:
            value_pix[band1] = calc_vpix(src_data,band1)
        if not band1 in value_out:
            value_out[band1] = calc_vout(value_pix[band1])
        sn = calc_sn(value_pix[band1],value_out[band1])
        if sn.shape != data_shape:
            raise ValueError('Error, sn.shape={}, data_shape={} >>> {}'.format(sn.shape,data_shape,fnam))
    else:
        raise ValueError('Error, len(opts.param)={} >>> {}'.format(len(opts.param),opts.param))
elif opts.param[0] == 'B':
    if len(opts.param) == 2:
        band1 = opts.param[1]
        pnam = 'S/B Ratio ({})'.format(bands[band1])
        if not band1 in value_pix:
            value_pix[band1] = calc_vpix(src_data,band1)
        if not band1 in value_out:
            value_out[band1] = calc_vout(value_pix[band1])
        sn = calc_sb(value_pix[band1],value_out[band1])
        if sn.shape != data_shape:
            raise ValueError('Error, sn.shape={}, data_shape={} >>> {}'.format(sn.shape,data_shape,fnam))
    else:
        raise ValueError('Error, len(opts.param)={} >>> {}'.format(len(opts.param),opts.param))
else:
    raise ValueError('Error, opts.param={}'.format(opts.param))
if opts.param[0] == 'N' or opts.param[0] == 'B':
    rr = sn
else:
    rr = (red-green)/norm

# Write Destination GeoTIFF
dst_nx = src_nx
dst_ny = src_ny
dst_nb = 1
dst_prj = src_prj
dst_trans = src_trans
dst_meta = src_meta
dst_dtype = gdal.GDT_Float32
dst_nodata = np.nan
dst_data = [rr]
dst_band = ['{}'.format(opts.param)]
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
    plt.interactive(True)
    fig = plt.figure(1,facecolor='w',figsize=(5,5))
    plt.subplots_adjust(top=0.9,bottom=0.1,left=0.05,right=0.85)
    fig.clear()
    ax1 = plt.subplot(111)
    ax1.set_xticks([])
    ax1.set_yticks([])
    if opts.ax1_zmin is not None and opts.ax1_zmax is not None:
        im = ax1.imshow(rr,extent=(src_xmin,src_xmax,src_ymin,src_ymax),vmin=opts.ax1_zmin,vmax=opts.ax1_zmax,cmap=cm.jet,interpolation='none')
    elif opts.ax1_zmin is not None:
        im = ax1.imshow(rr,extent=(src_xmin,src_xmax,src_ymin,src_ymax),vmin=opts.ax1_zmin,cmap=cm.jet,interpolation='none')
    elif opts.ax1_zmax is not None:
        im = ax1.imshow(rr,extent=(src_xmin,src_xmax,src_ymin,src_ymax),vmax=opts.ax1_zmax,cmap=cm.jet,interpolation='none')
    else:
        im = ax1.imshow(rr,extent=(src_xmin,src_xmax,src_ymin,src_ymax),cmap=cm.jet,interpolation='none')
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
    ax2.set_ylabel(pnam)
    ax2.yaxis.set_label_coords(3.5,0.5)
    if opts.remove_nan:
        src_indy,src_indx = np.indices(data_shape)
        src_xp = src_trans[0]+(src_indx+0.5)*src_trans[1]+(src_indy+0.5)*src_trans[2]
        src_yp = src_trans[3]+(src_indx+0.5)*src_trans[4]+(src_indy+0.5)*src_trans[5]
        cnd = ~np.isnan(rr)
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
    plt.savefig(opts.fignam)
    plt.draw()
