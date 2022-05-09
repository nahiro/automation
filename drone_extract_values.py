#!/usr/bin/env python
import os
import sys
import re
import gdal
import numpy as np
from optparse import OptionParser,IndentedHelpFormatter

# Constants

# Default values
GPS_FNAM = 'gps_points.dat'
INNER_RADIUS = 0.2 # m
OUTER_RADIUS = 0.5 # m

# Read options
parser = OptionParser(formatter=IndentedHelpFormatter(max_help_position=200,width=200))
parser.add_option('-I','--src_geotiff',default=None,action='append',help='Source GeoTIFF name (%default)')
parser.add_option('-g','--gps_fnam',default=GPS_FNAM,help='GPS file name (%default)')
parser.add_option('-e','--ext_fnam',default=None,help='Extract file name (%default)')
parser.add_option('-i','--inner_radius',default=INNER_RADIUS,type='float',help='Inner region radius in m (%default)')
parser.add_option('-o','--outer_radius',default=OUTER_RADIUS,type='float',help='Outer region radius in m (%default)')
(opts,args) = parser.parse_args()
if opts.src_geotiff is None:
    raise ValueError('Error, opts.src_geotiff={}'.format(opts.src_geotiff))
if opts.ext_fnam is None:
    bnam,enam = os.path.splitext(opts.gps_fnam)
    opts.ext_fnam = bnam+'_values'+enam

comments = ''
header = None
number_bunch = []
plot_bunch = []
x_bunch = []
y_bunch = []
blb_bunch = []
with open(opts.gps_fnam,'r') as fp:
    #BunchNumber, PlotPaddy, Easting, Northing, DamagedByBLB
    #  1,  1, 751739.0086, 9243034.0783,  1
    for line in fp:
        if len(line) < 1:
            continue
        elif line[0] == '#':
            comments += line
            continue
        elif re.search('[a-zA-Z]',line):
            if header is None:
                header = line # skip header
                continue
            else:
                raise ValueError('Error in reading {} >>> {}'.format(opts.gps_fnam,line))
        item = line.split(sep=',')
        if len(item) < 5:
            continue
        number_bunch.append(int(item[0]))
        plot_bunch.append(int(item[1]))
        x_bunch.append(float(item[2]))
        y_bunch.append(float(item[3]))
        blb_bunch.append(int(item[4]))
number_bunch = np.array(number_bunch)
indx_bunch = np.arange(len(number_bunch))
plot_bunch = np.array(plot_bunch)
x_bunch = np.array(x_bunch)
y_bunch = np.array(y_bunch)
blb_bunch = np.array(blb_bunch)
plots = np.unique(plot_bunch)

if len(opts.src_geotiff) == 1:
    # Read Source GeoTIFF
    fnam = opts.src_geotiff[0]
    ds = gdal.Open(fnam)
    src_nx = ds.RasterXSize
    src_ny = ds.RasterYSize
    src_nb = ds.RasterCount
    src_prj = ds.GetProjection()
    src_trans = ds.GetGeoTransform()
    if src_trans[2] != 0.0 or src_trans[4] != 0.0:
        raise ValueError('Error, src_trans={} >>> {}'.format(src_trans,fnam))
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
    src_shape = (src_ny,src_nx)
    src_indy,src_indx = np.indices(src_shape)
    src_xp = src_trans[0]+(src_indx+0.5)*src_trans[1]+(src_indy+0.5)*src_trans[2]
    src_yp = src_trans[3]+(src_indx+0.5)*src_trans[4]+(src_indy+0.5)*src_trans[5]
    with open(opts.ext_fnam,'w') as fp:
        if len(comments) > 0:
            fp.write(comments)
        if header is not None:
            fp.write(header.rstrip())
            for iband in range(src_nb):
                fp.write(', {:>13s}'.format(src_band[iband]))
            fp.write('\n')
        for i in range(len(number_bunch)):
            fp.write('{:3d}, {:3d}, {:12.4f}, {:13.4f}, {:3d}'.format(number_bunch[i],plot_bunch[i],x_bunch[i],y_bunch[i],blb_bunch[i]))
            r = np.sqrt(np.square(src_xp-x_bunch[i])+np.square(src_yp-y_bunch[i]))
            cnd1 = (r > opts.inner_radius) & (r < opts.outer_radius)
            for iband in range(src_nb):
                cnd2 = cnd1 & (~np.isnan(src_data[iband]))
                dcnd = src_data[iband][cnd2]
                if dcnd.size < 1:
                    raise ValueError('Error, no data for Plot#{}, Bunch#{} ({}) >>> {}'.format(plot_bunch[i],number_bunch[i],src_band[iband],fnam))
                fp.write(', {:13.6e}'.format(dcnd.mean()))
            fp.write('\n')
elif len(opts.src_geotiff) == len(plots):
    with open(opts.ext_fnam,'w') as fp:
        if len(comments) > 0:
            fp.write(comments)
        for plot,fnam in zip(plots,opts.src_geotiff):
            cnd = (plot_bunch == plot)
            indx = indx_bunch[cnd]
            ng = number_bunch[indx]
            xg = x_bunch[indx]
            yg = y_bunch[indx]
            blb = blb_bunch[indx]
            size = len(indx)
            indx_member = np.arange(size)
            if not np.all(np.argsort(ng) == indx_member): # wrong order
                raise ValueError('Error, plot={}, ng={} >>> {}'.format(plot,ng,opts.gps_fnam))
            # Read Source GeoTIFF
            ds = gdal.Open(fnam)
            src_nx = ds.RasterXSize
            src_ny = ds.RasterYSize
            src_nb = ds.RasterCount
            src_prj = ds.GetProjection()
            src_trans = ds.GetGeoTransform()
            if src_trans[2] != 0.0 or src_trans[4] != 0.0:
                raise ValueError('Error, src_trans={} >>> {}'.format(src_trans,fnam))
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
            src_shape = (src_ny,src_nx)
            src_indy,src_indx = np.indices(src_shape)
            src_xp = src_trans[0]+(src_indx+0.5)*src_trans[1]+(src_indy+0.5)*src_trans[2]
            src_yp = src_trans[3]+(src_indx+0.5)*src_trans[4]+(src_indy+0.5)*src_trans[5]
            if header is not None:
                fp.write(header.rstrip())
                for iband in range(src_nb):
                    fp.write(', {:>13s}'.format(src_band[iband]))
                fp.write('\n')
                header = None
            for i in indx_member:
                fp.write('{:3d}, {:3d}, {:12.4f}, {:13.4f}, {:3d}'.format(ng[i],plot,xg[i],yg[i],blb[i]))
                r = np.sqrt(np.square(src_xp-xg[i])+np.square(src_yp-yg[i]))
                cnd1 = (r > opts.inner_radius) & (r < opts.outer_radius)
                for iband in range(src_nb):
                    cnd2 = cnd1 & (~np.isnan(src_data[iband]))
                    dcnd = src_data[iband][cnd2]
                    if dcnd.size < 1:
                        raise ValueError('Error, no data for Plot#{}, Bunch#{} ({}) >>> {}'.format(plot,ng[i],src_band[iband],fnam))
                    fp.write(', {:13.6e}'.format(dcnd.mean()))
                fp.write('\n')
else:
    raise ValueError('Error, len(opts.src_geotiff)={}'.format(len(opts.src_geotiff)))
