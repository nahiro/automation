#!/usr/bin/env python
import os
import sys
import gdal
import osr
from skimage.measure import points_in_poly
import shapefile
from shapely.geometry import Polygon
import numpy as np
from scipy.interpolate import griddata
from optparse import OptionParser,IndentedHelpFormatter

# Default values
BUFFER = -1.5 # m

# Read options
parser = OptionParser(formatter=IndentedHelpFormatter(max_help_position=200,width=200))
parser.add_option('-s','--shp_fnam',default=None,help='Shape file name (%default)')
parser.add_option('-b','--buffer',default=BUFFER,type='float',help='Buffer distance (%default)')
parser.add_option('-I','--src_geotiff',default=None,help='Source GeoTIFF name (%default)')
parser.add_option('-O','--dst_geotiff',default=None,help='Destination GeoTIFF name (%default)')
parser.add_option('--use_index',default=False,action='store_true',help='Use index instead of OBJECTID (%default)')
(opts,args) = parser.parse_args()
if opts.dst_geotiff is None:
    bnam,enam = os.path.splitext(os.path.basename(opts.src_geotiff))
    opts.dst_geotiff = bnam+'_mask'+enam

ds = gdal.Open(opts.src_geotiff)
src_nx = ds.RasterXSize
src_ny = ds.RasterYSize
src_nb = ds.RasterCount
src_shape = (src_ny,src_nx)
src_prj = ds.GetProjection()
src_trans = ds.GetGeoTransform()
src_meta = ds.GetMetadata()
src_data = ds.ReadAsArray().astype(np.float64).reshape(src_nb,src_ny,src_nx)
src_band = []
for iband in range(src_nb):
    band = ds.GetRasterBand(iband+1)
    src_band.append(band.GetDescription())
src_nodata = band.GetNoDataValue()
src_xmin = src_trans[0]
src_xstp = src_trans[1]
src_xmax = src_xmin+src_nx*src_xstp
src_ymax = src_trans[3]
src_ystp = src_trans[5]
src_ymin = src_ymax+src_ny*src_ystp
src_indy,src_indx = np.indices(src_shape)
src_xp = src_trans[0]+(src_indx+0.5)*src_trans[1]+(src_indy+0.5)*src_trans[2]
src_yp = src_trans[3]+(src_indx+0.5)*src_trans[4]+(src_indy+0.5)*src_trans[5]
src_points = np.hstack((src_xp.reshape(-1,1),src_yp.reshape(-1,1)))
ds = None

dst_nx = src_nx
dst_ny = src_ny
dst_nb = 1
dst_shape = (dst_ny,dst_nx)
dst_prj = src_prj
dst_trans = src_trans
dst_meta = src_meta
dst_data = np.full(dst_shape,-1)
dst_band = 'mask'
dst_nodata = -1

r = shapefile.Reader(opts.shp_fnam)
for ii,shaperec in enumerate(r.iterShapeRecords()):
    rec = shaperec.record
    shp = shaperec.shape
    if opts.use_index:
        object_id = ii+1
    else:
        object_id = rec.OBJECTID
    if len(shp.points) < 1:
        sys.stderr.write('Warning, len(shp.points)={}, ii={}\n'.format(len(shp.points),ii))
        continue
    poly_buffer = Polygon(shp.points).buffer(opts.buffer)
    if poly_buffer.area <= 0.0:
        continue
    xmin_buffer,ymin_buffer,xmax_buffer,ymax_buffer = poly_buffer.bounds
    if (xmin_buffer > src_xmax) or (xmax_buffer < src_xmin) or (ymin_buffer > src_ymax) or (ymax_buffer < src_ymin):
        continue
    flags = np.full(dst_shape,False)
    if poly_buffer.type == 'MultiPolygon':
        for p in poly_buffer:
            path_search = np.array(p.exterior.coords.xy).swapaxes(0,1)
            flags |= points_in_poly(src_points,path_search).reshape(dst_shape)
    else:
        path_search = np.array(poly_buffer.exterior.coords.xy).swapaxes(0,1)
        flags = points_in_poly(src_points,path_search).reshape(dst_shape)
    dst_data[flags] = object_id

drv = gdal.GetDriverByName('GTiff')
ds = drv.Create(opts.dst_geotiff,dst_nx,dst_ny,dst_nb,gdal.GDT_Int32)
ds.SetProjection(dst_prj)
ds.SetGeoTransform(dst_trans)
ds.SetMetadata(dst_meta)
band = ds.GetRasterBand(1)
band.WriteArray(dst_data)
band.SetDescription(dst_band)
band.SetNoDataValue(dst_nodata) # The TIFFTAG_GDAL_NODATA only support one value per dataset
ds.FlushCache()
ds = None # close dataset
