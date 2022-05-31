#!/usr/bin/env python
try:
    import gdal
except Exception:
    from osgeo import gdal
try:
    import osr
except Exception:
    from osgeo import osr
import numpy as np
import warnings
from argparse import ArgumentParser,RawTextHelpFormatter

# Read options
parser = ArgumentParser(formatter_class=lambda prog:RawTextHelpFormatter(prog,max_help_position=200,width=200))
parser.add_argument('-I','--src_geotiff',default=None,help='Source GeoTIFF name (%(default)s)')
parser.add_argument('-O','--dst_geotiff',default=None,help='Destination GeoTIFF name (%(default)s)')
parser.add_argument('-M','--mask_geotiff',default=None,help='Mask GeoTIFF name (%(default)s)')
parser.add_argument('-x','--imin',default=None,type=int,help='Start x index (%(default)s)')
parser.add_argument('-X','--imax',default=None,type=int,help='Stop x index (%(default)s)')
parser.add_argument('-s','--istp',default=None,type=int,help='Step x index (%(default)s)')
parser.add_argument('-y','--jmin',default=None,type=int,help='Start y index (%(default)s)')
parser.add_argument('-Y','--jmax',default=None,type=int,help='Stop y index (%(default)s)')
parser.add_argument('-S','--jstp',default=None,type=int,help='Step y index (%(default)s)')
parser.add_argument('-r','--rmax',default=None,type=float,help='Maximum exclusion ratio (%(default)s)')
args = parser.parse_args()

ds = gdal.Open(args.src_geotiff)
src_nx = ds.RasterXSize
src_ny = ds.RasterYSize
src_nb = ds.RasterCount
src_shape = (src_ny,src_nx)
src_prj = ds.GetProjection()
src_trans = ds.GetGeoTransform()
if src_trans[2] != 0.0 or src_trans[4] != 0.0:
    raise ValueError('Error, src_trans={}'.format(src_trans))
src_meta = ds.GetMetadata()
src_data = ds.ReadAsArray().astype(np.float64).reshape(src_nb,src_ny,src_nx)
src_band = []
for iband in range(src_nb):
    band = ds.GetRasterBand(iband+1)
    src_band.append(band.GetDescription())
src_nodata = band.GetNoDataValue()
src_xmin = src_trans[0]
src_xstp = src_trans[1]
src_ymax = src_trans[3]
src_ystp = src_trans[5]
src_xgrd = src_xmin+(np.arange(src_nx)+0.5)*src_xstp
src_ygrd = src_ymax+(np.arange(src_ny)+0.5)*src_ystp
ds = None

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

if args.imin is None:
    args.imin = 0
if args.imax is None:
    args.imax = src_nx
if args.jmin is None:
    args.jmin = 0
if args.jmax is None:
    args.jmax = src_ny

dst_nx = (args.imax-args.imin)//args.istp
dst_ny = (args.jmax-args.jmin)//args.jstp
dst_nb = src_nb
dst_shape = (dst_ny,dst_nx)
dst_prj = src_prj
dst_trans = [0.0]*len(src_trans)
dst_trans[0] = src_xgrd[args.imin]-0.5*src_xstp
dst_trans[1] = src_xstp*args.istp
dst_trans[3] = src_ygrd[args.jmin]-0.5*src_ystp
dst_trans[5] = src_ystp*args.jstp
dst_meta = src_meta
dst_data = []
dst_band = []
if args.rmax is not None and src_nodata is not None:
    dst_nsum = []
    dst_norm = 1.0/(args.istp*args.jstp)
for iband in range(dst_nb):
    tmp_data = src_data[iband,args.jmin:args.jmin+args.jstp*dst_ny,args.imin:args.imin+args.istp*dst_nx].reshape(dst_ny,args.jstp,dst_nx,args.istp)
    if src_nodata is None:
        dst_data.append(tmp_data.mean(axis=-1).mean(axis=1))
    elif np.isnan(src_nodata):
        cnd = np.isnan(tmp_data)
        if cnd.sum() > 0:
            with warnings.catch_warnings():
                warnings.filterwarnings(action='ignore',message='Mean of empty slice')
                dst_data.append(np.nanmean(np.nanmean(tmp_data,axis=-1),axis=1))
            if args.rmax is not None:
                dst_nsum.append(np.sum(np.sum(cnd,axis=-1),axis=1)*dst_norm)
        else:
            dst_data.append(tmp_data.mean(axis=-1).mean(axis=1))
            if args.rmax is not None:
                dst_nsum.append(np.full(dst_shape,0.0))
    else:
        cnd = (tmp_data == src_nodata)
        if cnd.sum() > 0:
            tmp_data[cnd] = np.nan
            with warnings.catch_warnings():
                warnings.filterwarnings(action='ignore',message='Mean of empty slice')
                avg_data = np.nanmean(np.nanmean(tmp_data,axis=-1),axis=1)
            if args.rmax is not None:
                dst_nsum.append(np.sum(np.sum(cnd,axis=-1),axis=1)*dst_norm)
            cnd = np.isnan(avg_data)
            avg_data[cnd] = src_nodata
            dst_data.append(avg_data)
        else:
            dst_data.append(tmp_data.mean(axis=-1).mean(axis=1))
            if args.rmax is not None:
                dst_nsum.append(np.full(dst_shape,0.0))
    dst_band.append(src_band[iband])
dst_data = np.array(dst_data).astype(np.float32)
if args.rmax is not None and src_nodata is not None:
    dst_nsum = np.array(dst_nsum)
    dst_data[dst_nsum > args.rmax] = np.nan
dst_nodata = src_nodata

drv = gdal.GetDriverByName('GTiff')
ds = drv.Create(args.dst_geotiff,dst_nx,dst_ny,dst_nb,gdal.GDT_Float32)
ds.SetProjection(dst_prj)
ds.SetGeoTransform(dst_trans)
ds.SetMetadata(dst_meta)
for iband in range(dst_nb):
    band = ds.GetRasterBand(iband+1)
    band.WriteArray(dst_data[iband])
    band.SetDescription(dst_band[iband])
if dst_nodata is None:
    band.SetNoDataValue(np.nan) # The TIFFTAG_GDAL_NODATA only support one value per dataset
else:
    band.SetNoDataValue(dst_nodata) # The TIFFTAG_GDAL_NODATA only support one value per dataset
ds.FlushCache()
ds = None # close dataset
