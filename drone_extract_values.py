#!/usr/bin/env python
import os
import sys
import re
import zlib # import zlib before gdal to prevent segmentation fault when saving pdf
import gdal
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib.backends.backend_pdf import PdfPages
from optparse import OptionParser,IndentedHelpFormatter

# Constants

# Default values
CSV_FNAM = 'gps_points.dat'
INNER_RADIUS = 0.2 # m
OUTER_RADIUS = 0.5 # m

# Read options
parser = OptionParser(formatter=IndentedHelpFormatter(max_help_position=200,width=200))
parser.add_option('-I','--src_geotiff',default=None,action='append',help='Source GeoTIFF name (%default)')
parser.add_option('-g','--csv_fnam',default=CSV_FNAM,help='CSV file name (%default)')
parser.add_option('-e','--ext_fnam',default=None,help='Extract file name (%default)')
parser.add_option('-i','--inner_radius',default=INNER_RADIUS,type='float',help='Inner region radius in m (%default)')
parser.add_option('-o','--outer_radius',default=OUTER_RADIUS,type='float',help='Outer region radius in m (%default)')
parser.add_option('-H','--header_none',default=False,action='store_true',help='Read csv file with no header (%default)')
parser.add_option('-F','--fignam',default=None,help='Output figure name for debug (%default)')
parser.add_option('-z','--ax1_zmin',default=None,type='float',action='append',help='Axis1 Z min for debug (%default)')
parser.add_option('-Z','--ax1_zmax',default=None,type='float',action='append',help='Axis1 Z max for debug (%default)')
parser.add_option('-s','--ax1_zstp',default=None,type='float',action='append',help='Axis1 Z stp for debug (%default)')
parser.add_option('-n','--remove_nan',default=False,action='store_true',help='Remove nan for debug (%default)')
parser.add_option('-d','--debug',default=False,action='store_true',help='Debug mode (%default)')
parser.add_option('-b','--batch',default=False,action='store_true',help='Batch mode (%default)')
(opts,args) = parser.parse_args()
if opts.src_geotiff is None:
    raise ValueError('Error, opts.src_geotiff={}'.format(opts.src_geotiff))
if opts.ext_fnam is None or opts.fignam is None:
    bnam,enam = os.path.splitext(opts.csv_fnam)
    if opts.ext_fnam is None:
        opts.ext_fnam = bnam+'_values'+enam
    if opts.fignam is None:
        opts.fignam = bnam+'_values.pdf'

comments = ''
header = None
loc_bunch = []
number_bunch = []
plot_bunch = []
x_bunch = []
y_bunch = []
rest_bunch = []
with open(opts.csv_fnam,'r') as fp:
    #Location, BunchNumber, PlotPaddy, Easting, Northing, PlantDate, Age, Tiller, BLB, Blast, Borer, Rat, Hopper, Drought
    #           15,   1,   1,  750949.8273,  9242821.0756, 2022-01-08,    55,  27,   1,   0,   5,   0,   0,   0
    for line in fp:
        if len(line) < 1:
            continue
        elif line[0] == '#':
            comments += line
            continue
        elif not opts.header_none and header is None:
            header = line # skip header
            item = [s.strip() for s in header.split(',')]
            if len(item) < 6:
                raise ValueError('Error in header ({}) >>> {}'.format(opts.csv_fnam,header))
            if item[0] != 'Location' or item[1] != 'BunchNumber' or item[2] != 'PlotPaddy' or item[3] != 'Easting' or item[4] != 'Northing':
                raise ValueError('Error in header ({}) >>> {}'.format(opts.csv_fnam,header))
            continue
        m = re.search('^([^,]+),([^,]+),([^,]+),([^,]+),([^,]+),(.*)',line)
        if not m:
            continue
        loc_bunch.append(m.group(1))
        number_bunch.append(int(m.group(2)))
        plot_bunch.append(int(m.group(3)))
        x_bunch.append(float(m.group(4)))
        y_bunch.append(float(m.group(5)))
        rest_bunch.append(m.group(6))
loc_bunch = np.array(loc_bunch)
number_bunch = np.array(number_bunch)
indx_bunch = np.arange(len(number_bunch))
plot_bunch = np.array(plot_bunch)
x_bunch = np.array(x_bunch)
y_bunch = np.array(y_bunch)
rest_bunch = np.array(rest_bunch)
plots = np.unique(plot_bunch)

if opts.debug:
    if not opts.batch:
        plt.interactive(True)
    fig = plt.figure(1,facecolor='w',figsize=(5,5))
    plt.subplots_adjust(top=0.9,bottom=0.1,left=0.05,right=0.85)
    pdf = PdfPages(opts.fignam)
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
            fp.write('{:3d}, {:3d}, {:12.4f}, {:13.4f},{}'.format(number_bunch[i],plot_bunch[i],x_bunch[i],y_bunch[i],rest_bunch[i]))
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
            lg = loc_bunch[indx]
            ng = number_bunch[indx]
            xg = x_bunch[indx]
            yg = y_bunch[indx]
            rest = rest_bunch[indx]
            size = len(indx)
            indx_member = np.arange(size)
            if not np.all(np.argsort(ng) == indx_member): # wrong order
                raise ValueError('Error, plot={}, ng={} >>> {}'.format(plot,ng,opts.csv_fnam))
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
                fp.write('{:>13s}, {:3d}, {:3d}, {:12.4f}, {:13.4f},{}'.format(lg[i],ng[i],plot,xg[i],yg[i],rest[i]))
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
if opts.debug:
    pdf.close()
