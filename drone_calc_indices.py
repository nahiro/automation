#!/usr/bin/env python
import os
import zlib # import zlib before gdal to prevent segmentation fault when saving pdf
import gdal
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib.backends.backend_pdf import PdfPages
from argparse import ArgumentParser,RawTextHelpFormatter

# Constants
PARAMS = ['Sb','Sg','Sr','Se','Sn','Nb','Ng','Nr','Ne','Nn','NDVI','GNDVI','RGI','NRGI']
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
PARAM = ['Nb','Ng','Nr','Ne','Nn','NDVI','GNDVI','NRGI']
NORM_BAND = ['b','g','r','e','n']
RGI_RED_BAND = 'e'

# Read options
parser = ArgumentParser(formatter_class=lambda prog:RawTextHelpFormatter(prog,max_help_position=200,width=200))
parser.add_argument('-I','--src_geotiff',default=None,help='Source GeoTIFF name (%(default)s)')
parser.add_argument('-O','--dst_geotiff',default=None,help='Destination GeoTIFF name (%(default)s)')
parser.add_argument('-M','--mask_geotiff',default=None,help='Mask GeoTIFF name (%(default)s)')
parser.add_argument('-p','--param',default=None,action='append',help='Output parameter ({})'.format(PARAM))
parser.add_argument('-N','--norm_band',default=None,action='append',help='Wavelength band for normalization ({})'.format(NORM_BAND))
parser.add_argument('-r','--rgi_red_band',default=RGI_RED_BAND,help='Wavelength band for RGI (%(default)s)')
parser.add_argument('--data_min',default=None,type=float,help='Minimum data value (%(default)s)')
parser.add_argument('--data_max',default=None,type=float,help='Maximum data value (%(default)s)')
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
for param in args.param:
    if not param in PARAMS:
        raise ValueError('Error, unknown parameter >>> {}'.format(param))
if args.norm_band is None:
    args.norm_band = NORM_BAND
for band in args.norm_band:
    if not band in bands:
        raise ValueError('Error, unknown band for normalization >>> {}'.format(band))
if not args.rgi_red_band in bands:
    raise ValueError('Error, unknown band for rgi >>> {}'.format(args.rgi_red_band))
if args.ax1_zmin is not None:
    while len(args.ax1_zmin) < len(args.param):
        args.ax1_zmin.append(args.ax1_zmin[-1])
if args.ax1_zmax is not None:
    while len(args.ax1_zmax) < len(args.param):
        args.ax1_zmax.append(args.ax1_zmax[-1])
if args.ax1_zstp is not None:
    while len(args.ax1_zstp) < len(args.param):
        args.ax1_zstp.append(args.ax1_zstp[-1])
if args.src_geotiff is None:
    raise ValueError('Error, src_geotiff is not specified.')
elif args.dst_geotiff is None or args.fignam is None:
    bnam,enam = os.path.splitext(args.src_geotiff)
    if args.dst_geotiff is None:
        args.dst_geotiff = bnam+'_indices'+enam
    if args.fignam is None:
        args.fignam = bnam+'_indices.pdf'

def calc_vpix(data,band):
    vpix = data[band_index[band]].copy()
    if args.data_min is not None:
        vpix[vpix < args.data_min] = np.nan
    if args.data_max is not None:
        vpix[vpix > args.data_max] = np.nan
    return vpix

# Read Source GeoTIFF
ds = gdal.Open(args.src_geotiff)
src_nx = ds.RasterXSize
src_ny = ds.RasterYSize
src_nb = ds.RasterCount
if src_nb != len(bands):
    raise ValueError('Error, src_nb={}, len(bands)={} >>> {}'.format(src_nb,len(bands),args.src_geotiff))
src_shape = (src_ny,src_nx)
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
if src_nodata is not None and not np.isnan(src_nodata):
    src_data[src_data == src_nodata] = np.nan

# Read Mask GeoTIFF
if args.mask_geotiff is not None:
    ds = gdal.Open(args.mask_geotiff)
    mask_nx = ds.RasterXSize
    mask_ny = ds.RasterYSize
    mask_nb = ds.RasterCount
    if mask_nb != 1:
        raise ValueError('Error, mask_nb={} >>> {}'.format(mask_nb,args.mask_geotiff))
    mask_shape = (mask_ny,mask_nx)
    if mask_shape != src_shape:
        raise ValueError('Error, mask_shape={}, src_shape={} >>> {}'.format(mask_shape,src_shape,args.mask_geotiff))
    mask_data = ds.ReadAsArray().reshape(mask_ny,mask_nx)
    ds = None
    src_data[:,mask_data < 0.5] = np.nan

fnam = args.src_geotiff
norm = 0.0
value_pix = {}
for band in bands:
    value_pix[band] = calc_vpix(src_data,band)
    if band in args.norm_band:
        norm += value_pix[band]
norm = len(args.norm_band)/norm
dst_data = []
pnams = []
for param in args.param:
    if param == 'NDVI':
        red = value_pix['r']
        nir = value_pix['n']
        pnams.append(param)
        dst_data.append((nir-red)/(nir+red))
    elif param == 'GNDVI':
        green = value_pix['g']
        nir = value_pix['n']
        pnams.append(param)
        dst_data.append((nir-green)/(nir+green))
    elif param == 'RGI':
        green = value_pix['g']
        red = value_pix[args.rgi_red_band]
        pnams.append(param)
        dst_data.append(green*red)
    elif param == 'NRGI':
        green = value_pix['g']
        red = value_pix[args.rgi_red_band]
        pnams.append(param)
        dst_data.append(green*norm*red*norm)
    elif param[0] == 'S':
        if len(param) == 2:
            band = param[1]
            pnams.append('{}'.format(bands[band]))
            dst_data.append(value_pix[band])
        else:
            raise ValueError('Error, len(param)={} >>> {}'.format(len(param),param))
    elif param[0] == 'N':
        if len(param) == 2:
            band = param[1]
            pnams.append('Normalized {}'.format(bands[band]))
            dst_data.append(value_pix[band]*norm)
        else:
            raise ValueError('Error, len(param)={} >>> {}'.format(len(param),param))
    else:
        raise ValueError('Error, param={}'.format(param))
dst_data = np.array(dst_data)

# Write Destination GeoTIFF
dst_nx = src_nx
dst_ny = src_ny
dst_nb = len(args.param)
dst_prj = src_prj
dst_trans = src_trans
dst_meta = src_meta
dst_dtype = gdal.GDT_Float32
dst_nodata = np.nan
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
            im = ax1.imshow(dst_data[i],extent=(src_xmin,src_xmax,src_ymin,src_ymax),vmin=args.ax1_zmin[i],vmax=args.ax1_zmax[i],cmap=cm.jet,interpolation='none')
        elif args.ax1_zmin is not None:
            im = ax1.imshow(dst_data[i],extent=(src_xmin,src_xmax,src_ymin,src_ymax),vmin=args.ax1_zmin[i],cmap=cm.jet,interpolation='none')
        elif args.ax1_zmax is not None:
            im = ax1.imshow(dst_data[i],extent=(src_xmin,src_xmax,src_ymin,src_ymax),vmax=args.ax1_zmax[i],cmap=cm.jet,interpolation='none')
        else:
            im = ax1.imshow(dst_data[i],extent=(src_xmin,src_xmax,src_ymin,src_ymax),cmap=cm.jet,interpolation='none')
        divider = make_axes_locatable(ax1)
        cax = divider.append_axes('right',size='5%',pad=0.05)
        if args.ax1_zstp is not None:
            if args.ax1_zmin is not None:
                zmin = min((np.floor(np.nanmin(dst_data[i])/args.ax1_zstp[i])-1.0)*args.ax1_zstp[i],args.ax1_zmin[i])
            else:
                zmin = (np.floor(np.nanmin(dst_data[i])/args.ax1_zstp[i])-1.0)*args.ax1_zstp[i]
            if args.ax1_zmax is not None:
                zmax = max(np.nanmax(dst_data[i]),args.ax1_zmax[i]+0.1*args.ax1_zstp[i])
            else:
                zmax = np.nanmax(dst_data[i])+0.1*args.ax1_zstp[i]
            ax2 = plt.colorbar(im,cax=cax,ticks=np.arange(zmin,zmax,args.ax1_zstp[i])).ax
        else:
            ax2 = plt.colorbar(im,cax=cax).ax
        ax2.minorticks_on()
        ax2.set_ylabel(pnams[i])
        ax2.yaxis.set_label_coords(3.5,0.5)
        if args.remove_nan:
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
        if not args.batch:
            plt.draw()
            plt.pause(0.1)
    pdf.close()
