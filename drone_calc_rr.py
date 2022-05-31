#!/usr/bin/env python
import os
import zlib # import zlib before gdal to prevent segmentation fault when saving pdf
import gdal
import numpy as np
from scipy.signal import convolve2d
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib.backends.backend_pdf import PdfPages
from argparse import ArgumentParser,RawTextHelpFormatter

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
parser = ArgumentParser(formatter_class=RawTextHelpFormatter)
parser.add_argument('-I','--src_geotiff',default=None,help='Source GeoTIFF name (%(default)s)')
parser.add_argument('-O','--dst_geotiff',default=None,help='Destination GeoTIFF name (%(default)s)')
parser.add_argument('-p','--param',default=None,action='append',help='Output parameter ({})'.format(PARAM))
parser.add_argument('--data_min',default=None,type=float,help='Minimum data value (%(default)s)')
parser.add_argument('--data_max',default=None,type=float,help='Maximum data value (%(default)s)')
parser.add_argument('-i','--inner_size',default=INNER_SIZE,type=int,help='Inner region size in pixel (%(default)s)')
parser.add_argument('-o','--outer_size',default=OUTER_SIZE,type=int,help='Outer region size in pixel (%(default)s)')
parser.add_argument('-F','--fignam',default=None,help='Output figure name for debug (%(default)s)')
parser.add_argument('-z','--ax1_zmin',default=None,type=float,action='append',help='Axis1 Z min for debug (%(default)s)')
parser.add_argument('-Z','--ax1_zmax',default=None,type=float,action='append',help='Axis1 Z max for debug (%(default)s)')
parser.add_argument('-s','--ax1_zstp',default=None,type=float,action='append',help='Axis1 Z stp for debug (%(default)s)')
parser.add_argument('-n','--remove_nan',default=False,action='store_true',help='Remove nan for debug (%(default)s)')
parser.add_argument('-d','--debug',default=False,action='store_true',help='Debug mode (%(default)s)')
parser.add_argument('-b','--batch',default=False,action='store_true',help='Batch mode (%(default)s)')
args = parser.parse_args()
if args.param is None:
    args.param = PARAM
if args.ax1_zmin is not None:
    while len(args.ax1_zmin) < len(args.param):
        args.ax1_zmin.append(args.ax1_zmin[-1])
if args.ax1_zmax is not None:
    while len(args.ax1_zmax) < len(args.param):
        args.ax1_zmax.append(args.ax1_zmax[-1])
if args.ax1_zstp is not None:
    while len(args.ax1_zstp) < len(args.param):
        args.ax1_zstp.append(args.ax1_zstp[-1])
for param in args.param:
    if not param in PARAMS:
        raise ValueError('Error, unknown parameter >>> {}'.format(param))
if args.dst_geotiff is None or args.fignam is None:
    bnam,enam = os.path.splitext(args.src_geotiff)
    if args.dst_geotiff is None:
        args.dst_geotiff = bnam+'_rr'+enam
    if args.fignam is None:
        args.fignam = bnam+'_rr.pdf'

filt1 = np.ones((args.outer_size,args.outer_size))
norm = filt1.sum()
filt1 *= 1.0/norm

filt2 = np.ones((args.inner_size,args.inner_size))
norm = filt2.sum()
filt2 *= 1.0/norm

def calc_vpix(data,band):
    vpix = data[band_index[band]].copy()
    if args.data_min is not None:
        vpix[vpix < args.data_min] = np.nan
    if args.data_max is not None:
        vpix[vpix > args.data_max] = np.nan
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
ds = gdal.Open(args.src_geotiff)
src_nx = ds.RasterXSize
src_ny = ds.RasterYSize
src_nb = ds.RasterCount
if src_nb != len(bands):
    raise ValueError('Error, src_nb={}, len(bands)={} >>> {}'.format(src_nb,len(bands),args.src_geotiff))
src_prj = ds.GetProjection()
src_trans = ds.GetGeoTransform()
if src_trans[2] != 0.0 or src_trans[4] != 0.0:
    raise ValueError('Error, src_trans={} >>> {}'.format(src_trans,args.src_geotiff))
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

fnam = args.src_geotiff
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
rr = []
pnams = []
for param in args.param:
    if param[0] == 'L':
        if len(param) == 2:
            band1 = param[1]
            pnams.append('Redness Ratio (Local {})'.format(bands[band1]))
            if not band1 in value_pix:
                value_pix[band1] = calc_vpix(src_data,band1)
            if not band1 in value_out:
                value_out[band1] = calc_vout(value_pix[band1])
            norm = value_out[band1]
            if norm.shape != data_shape:
                raise ValueError('Error, norm.shape={}, data_shape={} >>> {}'.format(norm.shape,data_shape,fnam))
        elif len(param) == 3:
            band1 = param[1]
            band2 = param[2]
            pnams.append('Redness Ratio (Local {} + {})'.format(bands[band1],bands[band2]))
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
            raise ValueError('Error, len(param)={} >>> {}'.format(len(param),param))
    elif param[0] == 'G':
        if len(param) == 2:
            band1 = param[1]
            pnams.append('Redness Ratio (Global {})'.format(bands[band1]))
            if not band1 in value_pix:
                value_pix[band1] = calc_vpix(src_data,band1)
            norm1 = value_pix[band1]
            if norm1.shape != data_shape:
                raise ValueError('Error, norm1.shape={}, data_shape={} >>> {}'.format(norm1.shape,data_shape,fnam))
            norm = norm1[cnd_all].mean()
        elif len(param) == 3:
            band1 = param[1]
            band2 = param[2]
            pnams.append('Redness Ratio (Global {} + {})'.format(bands[band1],bands[band2]))
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
            raise ValueError('Error, len(param)={} >>> {}'.format(len(param),param))
    elif param[0] == 'S':
        if len(param) == 2:
            band1 = param[1]
            pnams.append('Redness Ratio ({})'.format(bands[band1]))
            if not band1 in value_pix:
                value_pix[band1] = calc_vpix(src_data,band1)
            norm = value_pix[band1]
            if norm.shape != data_shape:
                raise ValueError('Error, norm.shape={}, data_shape={} >>> {}'.format(norm.shape,data_shape,fnam))
        elif len(param) == 3:
            band1 = param[1]
            band2 = param[2]
            pnams.append('Redness Ratio ({} + {})'.format(bands[band1],bands[band2]))
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
            raise ValueError('Error, len(param)={} >>> {}'.format(len(param),param))
    elif param[0] == 'N':
        if len(param) == 2:
            band1 = param[1]
            pnams.append('S/N Ratio ({})'.format(bands[band1]))
            if not band1 in value_pix:
                value_pix[band1] = calc_vpix(src_data,band1)
            if not band1 in value_out:
                value_out[band1] = calc_vout(value_pix[band1])
            sr = calc_sn(value_pix[band1],value_out[band1])
            if sr.shape != data_shape:
                raise ValueError('Error, sr.shape={}, data_shape={} >>> {}'.format(sr.shape,data_shape,fnam))
        else:
            raise ValueError('Error, len(param)={} >>> {}'.format(len(param),param))
    elif param[0] == 'B':
        if len(param) == 2:
            band1 = param[1]
            pnams.append('S/B Ratio ({})'.format(bands[band1]))
            if not band1 in value_pix:
                value_pix[band1] = calc_vpix(src_data,band1)
            if not band1 in value_out:
                value_out[band1] = calc_vout(value_pix[band1])
            sr = calc_sb(value_pix[band1],value_out[band1])
            if sr.shape != data_shape:
                raise ValueError('Error, sr.shape={}, data_shape={} >>> {}'.format(sr.shape,data_shape,fnam))
        else:
            raise ValueError('Error, len(param)={} >>> {}'.format(len(param),param))
    else:
        raise ValueError('Error, param={}'.format(param))
    if param[0] == 'N' or param[0] == 'B':
        rr.append(sr)
    else:
        rr.append((red-green)/norm)
rr = np.array(rr)

# Write Destination GeoTIFF
dst_nx = src_nx
dst_ny = src_ny
dst_nb = len(args.param)
dst_prj = src_prj
dst_trans = src_trans
dst_meta = src_meta
dst_dtype = gdal.GDT_Float32
dst_nodata = np.nan
dst_data = rr
dst_band = args.param
drv = gdal.GetDriverByName('GTiff')
ds = drv.Create(args.dst_geotiff,dst_nx,dst_ny,dst_nb,dst_dtype)
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
if args.debug:
    if not args.batch:
        plt.interactive(True)
    fig = plt.figure(1,facecolor='w',figsize=(5,5))
    plt.subplots_adjust(top=0.9,bottom=0.1,left=0.05,right=0.85)
    pdf = PdfPages(args.fignam)
    for i,param in enumerate(args.param):
        fig.clear()
        ax1 = plt.subplot(111)
        ax1.set_xticks([])
        ax1.set_yticks([])
        if args.ax1_zmin is not None and args.ax1_zmax is not None:
            im = ax1.imshow(rr[i],extent=(src_xmin,src_xmax,src_ymin,src_ymax),vmin=args.ax1_zmin[i],vmax=args.ax1_zmax[i],cmap=cm.jet,interpolation='none')
        elif args.ax1_zmin is not None:
            im = ax1.imshow(rr[i],extent=(src_xmin,src_xmax,src_ymin,src_ymax),vmin=args.ax1_zmin[i],cmap=cm.jet,interpolation='none')
        elif args.ax1_zmax is not None:
            im = ax1.imshow(rr[i],extent=(src_xmin,src_xmax,src_ymin,src_ymax),vmax=args.ax1_zmax[i],cmap=cm.jet,interpolation='none')
        else:
            im = ax1.imshow(rr[i],extent=(src_xmin,src_xmax,src_ymin,src_ymax),cmap=cm.jet,interpolation='none')
        divider = make_axes_locatable(ax1)
        cax = divider.append_axes('right',size='5%',pad=0.05)
        if args.ax1_zstp is not None:
            if args.ax1_zmin is not None:
                zmin = min((np.floor(np.nanmin(rr[i])/args.ax1_zstp[i])-1.0)*args.ax1_zstp[i],args.ax1_zmin[i])
            else:
                zmin = (np.floor(np.nanmin(rr[i])/args.ax1_zstp[i])-1.0)*args.ax1_zstp[i]
            if args.ax1_zmax is not None:
                zmax = max(np.nanmax(rr[i]),args.ax1_zmax[i]+0.1*args.ax1_zstp[i])
            else:
                zmax = np.nanmax(rr[i])+0.1*args.ax1_zstp[i]
            ax2 = plt.colorbar(im,cax=cax,ticks=np.arange(zmin,zmax,args.ax1_zstp[i])).ax
        else:
            ax2 = plt.colorbar(im,cax=cax).ax
        ax2.minorticks_on()
        ax2.set_ylabel(pnams[i])
        ax2.yaxis.set_label_coords(3.5,0.5)
        if args.remove_nan:
            src_indy,src_indx = np.indices(data_shape)
            src_xp = src_trans[0]+(src_indx+0.5)*src_trans[1]+(src_indy+0.5)*src_trans[2]
            src_yp = src_trans[3]+(src_indx+0.5)*src_trans[4]+(src_indy+0.5)*src_trans[5]
            cnd = ~np.isnan(rr[i])
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
        if not args.batch:
            plt.draw()
            plt.pause(0.1)
    pdf.close()
