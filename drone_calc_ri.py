#!/usr/bin/env python
import os
import gdal
import numpy as np
from scipy.signal import convolve2d
import matplotlib.pyplot as plt
from optparse import OptionParser,IndentedHelpFormatter

# Constants
PARAMS = ['Grg','Lrg','Lb','Lg','Lr','Le','Ln','Srg','Sb','Sg','Sr','Se','Sn']

# Default values
PARAM = 'Lrg'
INNER_SIZE = 29 # pixel
OUTER_SIZE = 35 # pixel
FIGNAM = 'drone_calc_ri.pdf'

# Read options
parser = OptionParser(formatter=IndentedHelpFormatter(max_help_position=200,width=200))
parser.add_option('-I','--src_geotiff',default=None,help='Source GeoTIFF name (%default)')
parser.add_option('-O','--dst_geotiff',default=None,help='Destination GeoTIFF name (%default)')
parser.add_option('-p','--param',default=PARAM,help='Outer parameter (%default)')
parser.add_option('-i','--inner_size',default=INNER_SIZE,type='int',help='Inner region size in pixel (%default)')
parser.add_option('-o','--outer_size',default=OUTER_SIZE,type='int',help='Outer region size in pixel (%default)')
parser.add_option('-F','--fignam',default=FIGNAM,help='Output figure name for debug (%default)')
parser.add_option('-d','--debug',default=False,action='store_true',help='Debug mode (%default)')
(opts,args) = parser.parse_args()
if not opts.param in PARAMS:
    raise ValueError('Error, unknown parameter >>> {}'.format(opts.param))
if opts.dst_geotiff is None:
    bnam,enam = os.path.splitext(opts.src_geotiff)
    opts.dst_geotiff = bnam+'_ri'+enam

filt1 = np.ones((opts.outer_size,opts.outer_size))
norm = filt1.sum()
filt1 *= 1.0/norm

filt2 = np.ones((opts.inner_size,opts.inner_size))
norm = filt2.sum()
filt2 *= 1.0/norm

BLOCKS = ['11b','15','1b']
DATES = ['20220301','20220304','20220306']
datdir = '/home/naohiro/Work/Drone/220316/orthomosaic/ndvi_rms_repeat'

for block,date in zip(BLOCKS,DATES):
    fnam = os.path.join(datdir,'P4M_RTK_{}_{}_geocor.tif'.format(block,date))
    ds = gdal.Open(fnam)
    data = ds.ReadAsArray().astype(np.float64)
    ds = None

    blue = data[0]
    cnd = (blue < -10000)
    blue[cnd] = np.nan
    cnv1 = convolve2d(blue,filt1,mode='same')
    cnv2 = convolve2d(blue,filt2,mode='same')
    vout = (cnv1*filt1.size-cnv2*filt2.size)/(filt1.size-filt2.size)
    np.save('P4M_RTK_{}_{}_blue.npy'.format(block,date),blue)
    np.save('P4M_RTK_{}_{}_blue_out.npy'.format(block,date),vout)

    green = data[1]
    cnd = (green < -10000)
    green[cnd] = np.nan
    cnv1 = convolve2d(green,filt1,mode='same')
    cnv2 = convolve2d(green,filt2,mode='same')
    vout = (cnv1*filt1.size-cnv2*filt2.size)/(filt1.size-filt2.size)
    np.save('P4M_RTK_{}_{}_green.npy'.format(block,date),green)
    np.save('P4M_RTK_{}_{}_green_out.npy'.format(block,date),vout)

    red = data[2]
    cnd = (red < -10000)
    red[cnd] = np.nan
    cnv1 = convolve2d(red,filt1,mode='same')
    cnv2 = convolve2d(red,filt2,mode='same')
    vout = (cnv1*filt1.size-cnv2*filt2.size)/(filt1.size-filt2.size)
    np.save('P4M_RTK_{}_{}_red.npy'.format(block,date),red)
    np.save('P4M_RTK_{}_{}_red_out.npy'.format(block,date),vout)

    red2 = np.square(red)
    cnv1 = convolve2d(red2,filt1,mode='same')
    cnv2 = convolve2d(red2,filt2,mode='same')
    vout2 = (cnv1*filt1.size-cnv2*filt2.size)/(filt1.size-filt2.size)
    sn = (red-vout)/np.sqrt(vout2-vout*vout)
    np.save('P4M_RTK_{}_{}_red_sn.npy'.format(block,date),sn)

    rededge = data[3]
    cnd = (rededge < -10000)
    rededge[cnd] = np.nan
    cnv1 = convolve2d(rededge,filt1,mode='same')
    cnv2 = convolve2d(rededge,filt2,mode='same')
    vout = (cnv1*filt1.size-cnv2*filt2.size)/(filt1.size-filt2.size)
    np.save('P4M_RTK_{}_{}_rededge.npy'.format(block,date),rededge)
    np.save('P4M_RTK_{}_{}_rededge_out.npy'.format(block,date),vout)

    nir = data[4]
    cnd = (nir < -10000)
    nir[cnd] = np.nan
    cnv1 = convolve2d(nir,filt1,mode='same')
    cnv2 = convolve2d(nir,filt2,mode='same')
    vout = (cnv1*filt1.size-cnv2*filt2.size)/(filt1.size-filt2.size)
    np.save('P4M_RTK_{}_{}_nir.npy'.format(block,date),nir)
    np.save('P4M_RTK_{}_{}_nir_out.npy'.format(block,date),vout)

ds = gdal.Open(opts.src_geotiff)
src_nx = ds.RasterXSize
src_ny = ds.RasterYSize
src_nb = ds.RasterCount
src_prj = ds.GetProjection()
src_trans = ds.GetGeoTransform()
if src_trans[2] != 0.0 or src_trans[4] != 0.0:
    raise ValueError('Error, src_trans={}'.format(src_trans))
src_meta = ds.GetMetadata()
src_band = []
for iband in range(src_nb):
    band = ds.GetRasterBand(iband+1)
    src_band.append(band.GetDescription())
src_dtype = band.DataType
src_nodata = band.GetNoDataValue()
src_xmin = src_trans[0]
src_xstp = src_trans[1]
src_ymax = src_trans[3]
src_ystp = src_trans[5]
ds = None

# Write GeoTIFF
dst_nx = src_nx
dst_ny = src_ny
dst_nb = 1
dst_prj = src_prj
dst_trans = src_trans
dst_meta = src_meta
dst_dtype = gdal.GDT_Float32
dst_nodata = np.nan
dst_data = [ri]
dst_band = ['{}'.format(opts.ri_type)]
drv = gdal.GetDriverByName('GTiff')
ds = drv.Create(onam,dst_nx,dst_ny,dst_nb,dst_dtype)
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
    fig.clear()
    ax1 = plot.subplot(111)
    ax1.set_xticks([])
    ax1.set_yticks([])
    ax1.imshow(ri,extent=(src_xmin,src_xmax,src_ymin,src_ymax),interpolation='none')
    ax1.set_xlim(src_xmin,src_xmax)
    ax1.set_ylim(src_ymin,src_ymax)
    plt.savefig(opts.fignam)
    plt.draw()
