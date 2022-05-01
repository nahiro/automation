#!/usr/bin/env python
import os
import sys
import shutil
import re
import gdal
import numpy as np
from subprocess import call
from shapely.geometry import Point,Polygon
from matplotlib.path import Path
import matplotlib.patches as patches
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from optparse import OptionParser,IndentedHelpFormatter

# Default values
GPS_FNAM = 'gps_points.csv'
RMAX = 10.0 # m
NMIN = 5
XMGN = 10.0 # m
YWID = 0.01 # m
BUFFER = 5.0 # m
FIGNAM = 'drone_subset.pdf'
FACT = 10.0
GAMMA = 2.2

# Read options
parser = OptionParser(formatter=IndentedHelpFormatter(max_help_position=200,width=200))
parser.add_option('-I','--src_geotiff',default=None,help='Source GeoTIFF name (%default)')
parser.add_option('-O','--dst_geotiff',default=None,help='Destination GeoTIFF name (%default)')
parser.add_option('-g','--gps_fnam',default=GPS_FNAM,help='GPS file name (%default)')
parser.add_option('-R','--rmax',default=RMAX,type='float',help='Maximum distance in m (%default)')
parser.add_option('-n','--nmin',default=NMIN,type='int',help='Minimum number (%default)')
parser.add_option('-m','--xmgn',default=XMGN,type='float',help='X margin in m (%default)')
parser.add_option('-M','--ymgn',default=None,type='float',help='Y margin in m (%default)')
parser.add_option('-W','--ywid',default=YWID,type='float',help='Y width in m (%default)')
parser.add_option('-b','--buffer',default=BUFFER,type='float',help='Buffer radius in m (%default)')
parser.add_option('-F','--fignam',default=FIGNAM,help='Output figure name for debug (%default)')
parser.add_option('-S','--fact',default=FACT,type='float',help='Scale factor of output figure for debug (%default)')
parser.add_option('-G','--gamma',default=GAMMA,type='float',help='Gamma factor of output figure for debug (%default)')
parser.add_option('-i','--interp_point',default=False,action='store_true',help='Interpolate mode (%default)')
parser.add_option('-d','--debug',default=False,action='store_true',help='Debug mode (%default)')
(opts,args) = parser.parse_args()
if opts.ymgn is None:
    opts.ymgn = opts.xmgn

header = None
number_bunch = []
plot_bunch = []
x_bunch = []
y_bunch = []
with open(opts.gps_fnam,'r') as fp:
    #BunchNumber, PlotPaddy, Easting, Northing, DamagedByBLB
    #  1,  1, 751739.0086, 9243034.0783,  1
    for line in fp:
        if len(line) < 1:
            continue
        elif line[0] == '#':
            continue
        elif re.search('[a-zA-Z]',line):
            if header is None:
                header = line # skip header
                continue
            else:
                raise ValueError('Error in reading {} >>> {}'.format(opts.gps_fnam,line))
        item = line.split(sep=',')
        if len(item) < 4:
            continue
        number_bunch.append(int(item[0]))
        plot_bunch.append(int(item[1]))
        x_bunch.append(float(item[2]))
        y_bunch.append(float(item[3]))
number_bunch = np.array(number_bunch)
plot_bunch = np.array(plot_bunch)
x_bunch = np.array(x_bunch)
y_bunch = np.array(y_bunch)
index_bunch = np.arange(len(number_bunch))

plots = np.unique(plot_bunch)
groups = {}
groups_removed = {}
for plot in plots:
    cnd = (plot_bunch == plot)
    if cnd.sum() < opts.nmin:
        raise ValueError('Error, plot={}, cnd.sum()={} >>> {}'.format(plot,cnd.sum(),opts.gps_fnam))
    indx = index_bunch[cnd]
    xg = x_bunch[indx]
    yg = y_bunch[indx]
    index_member = np.arange(len(indx))
    flag = []
    for i_temp in index_member:
        cnd = (index_member != i_temp)
        r = np.sqrt(np.square(xg[cnd]-xg[i_temp])+np.square(yg[cnd]-yg[i_temp]))
        if r.min() > opts.rmax:
            flag.append(False)
        else:
            flag.append(True)
    flag = np.array(flag)
    groups[plot] = indx[flag]
    groups_removed[plot] = indx[~flag]
    if len(groups[plot]) < opts.nmin:
        raise ValueError('Error, plot={}, len(groups[{}])={} >>> {}'.format(plot,len(groups[plot]),opts.gps_fnam))

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

if opts.debug:
    plt.interactive(True)
    fig = plt.figure(1,facecolor='w',figsize=(5,5))
    pdf = PdfPages(opts.fignam)
bnam,enam = os.path.splitext(opts.dst_geotiff)
for plot in plots:
    ng = number_bunch[groups[plot]]
    xg = x_bunch[groups[plot]]
    yg = y_bunch[groups[plot]]
    # Create subset image
    out_xmin = xg.min()-opts.xmgn
    out_ymin = yg.min()-opts.ymgn
    out_xmax = xg.max()+opts.xmgn
    out_ymax = yg.max()+opts.ymgn
    xoff = int((out_xmin-src_xmin)/np.abs(src_xstp)+0.5)
    yoff = int((src_ymax-out_ymax)/np.abs(src_ystp)+0.5)
    xsize = int((out_xmax-out_xmin)/np.abs(src_xstp)+0.5)
    ysize = int((out_ymax-out_ymin)/np.abs(src_ystp)+0.5)
    if xoff < 0 or yoff < 0 or xsize < 0 or ysize < 0:
        raise ValueError('Error, xoff={}, yoff={}, xsize={}, ysize={}'.format(xoff,yoff,xsize,ysize))
    tnam = bnam+'_{}_temp'.format(plot)+enam
    onam = bnam+'_plot{}'.format(plot)+enam
    command = 'gdal_translate'
    command += ' -srcwin {} {} {} {}'.format(xoff,yoff,xsize,ysize)
    command += ' {}'.format(opts.src_geotiff)
    command += ' {}'.format(tnam)
    #print(command)
    call(command,shell=True)
    # Read subset image
    ds = gdal.Open(tnam)
    tmp_nx = ds.RasterXSize
    tmp_ny = ds.RasterYSize
    tmp_nb = ds.RasterCount
    tmp_trans = ds.GetGeoTransform()
    if tmp_trans[2] != 0.0 or tmp_trans[4] != 0.0:
        raise ValueError('Error, tmp_trans={}'.format(tmp_trans))
    tmp_data = ds.ReadAsArray().reshape(tmp_nb,tmp_ny,tmp_nx)
    tmp_xmin = tmp_trans[0]
    tmp_xstp = tmp_trans[1]
    tmp_ymax = tmp_trans[3]
    tmp_ystp = tmp_trans[5]
    tmp_xmax = tmp_xmin+tmp_nx*tmp_xstp
    tmp_ymin = tmp_ymax+tmp_ny*tmp_ystp
    tmp_xgrd = tmp_xmin+(np.arange(tmp_nx)+0.5)*tmp_xstp
    tmp_ygrd = tmp_ymax+(np.arange(tmp_ny)+0.5)*tmp_ystp
    ds = None
    if os.path.exists(tnam):
        os.remove(tnam)
    tmp_shape = (tmp_ny,tmp_nx)
    tmp_indy,tmp_indx = np.indices(tmp_shape)
    tmp_xp = tmp_trans[0]+(tmp_indx+0.5)*tmp_trans[1]+(tmp_indy+0.5)*tmp_trans[2]
    tmp_yp = tmp_trans[3]+(tmp_indx+0.5)*tmp_trans[4]+(tmp_indy+0.5)*tmp_trans[5]
    # Fit line
    xc = xg.copy()
    yc = yg.copy()
    coef = np.polyfit(xc,yc,1)
    dist = np.abs(coef[0]*xc-yc+coef[1])/np.sqrt(coef[0]*coef[0]+1)
    cnd = np.abs(dist-dist.mean()) < 2.0*dist.std()
    if not np.all(cnd):
        xc = xc[cnd]
        yc = yc[cnd]
        coef = np.polyfit(xc,yc,1)
        dist = np.abs(coef[0]*xc-yc+coef[1])/np.sqrt(coef[0]*coef[0]+1)
        cnd = np.abs(dist-dist.mean()) < 2.0*dist.std()
        if not np.all(cnd):
            xc = xc[cnd]
            yc = yc[cnd]
            coef = np.polyfit(xc,yc,1)
    xf = tmp_xgrd.copy()
    yf = np.polyval(coef,xf)
    # Origin
    xo = xf[0]
    yo = yf[0]
    # Unit direction vector
    xd = xf[-1]-xo
    yd = yf[-1]-yo
    norm = 1.0/np.sqrt(xd*xd+yd*yd)
    xd *= norm
    yd *= norm
    prod = (xg-xo)*xd+(yg-yo)*yd
    cnd = (np.diff(prod) < 0.0)
    if cnd.sum() > (~cnd).sum(): # opposite direction
        xd,yd = np.negative([xd,yd])
    # Interpolate
    if opts.interp_point and groups_removed[plot].size > 0:
        ng_removed = number_bunch[groups_removed[plot]]
        prod = (xg-xo)*xd+(yg-yo)*yd
        prod_removed = np.polyval(np.polyfit(ng,prod,1),ng_removed)
        xg_removed = xo+prod_removed*xd
        yg_removed = yo+prod_removed*yd
        groups[plot] = np.append(groups[plot],groups_removed[plot])
        ng = np.append(ng,ng_removed)
        xg = np.append(xg,xg_removed)
        yg = np.append(yg,yg_removed)
        indx = np.argsort(groups[plot])
        groups[plot] = groups[plot][indx]
        ng = ng[indx]
        xg = xg[indx]
        yg = yg[indx]
    # Inner product
    prod = (xg-xo)*xd+(yg-yo)*yd
    indx = np.argsort(prod)
    xs = xg[indx]
    ys = yg[indx]
    points = []
    points.extend([(x,y+opts.ywid) for x,y in zip(xs,ys)])
    points.extend([(x,y-opts.ywid) for x,y in zip(xs[::-1],ys[::-1])])
    points.extend([(x,y+opts.ywid) for x,y in zip(xs[:1],ys[:1])])
    poly_buffer = Polygon(points).buffer(opts.buffer)
    # Search internal points
    flags = []
    path_search = []
    if poly_buffer.area <= 0.0:
        sys.stderr.write('Warning, poly_buffer.area={} >>> Plot# {}\n'.format(poly_buffer.area,plot))
    elif poly_buffer.type == 'MultiPolygon':
        sys.stderr.write('Warning, poly_buffer.type={} >>> Plot# {}\n'.format(poly_buffer.type,plot))
        for p in poly_buffer:
            p_search = Path(np.array(p.exterior.coords.xy).swapaxes(0,1))
            path_search.append(p_search)
            if len(flags) < 1:
                flags = p_search.contains_points(np.hstack((tmp_xp.reshape(-1,1),tmp_yp.reshape(-1,1))),radius=0.0).reshape(tmp_shape)
            else:
                flags |= p_search.contains_points(np.hstack((tmp_xp.reshape(-1,1),tmp_yp.reshape(-1,1))),radius=0.0).reshape(tmp_shape)
    else:
        path_search = Path(np.array(poly_buffer.buffer(0.0).exterior.coords.xy).swapaxes(0,1))
        flags = path_search.contains_points(np.hstack((tmp_xp.reshape(-1,1),tmp_yp.reshape(-1,1))),radius=0.0).reshape(tmp_shape)
    # Write GeoTIFF
    dst_nx = tmp_nx
    dst_ny = tmp_ny
    dst_nb = tmp_nb
    dst_prj = src_prj
    dst_trans = tmp_trans
    dst_meta = src_meta
    dst_dtype = src_dtype
    if src_nodata is None:
        dst_nodata = np.nan
    else:
        dst_nodata = src_nodata
    dst_data = tmp_data.copy()
    dst_data[:,~flags] = dst_nodata
    dst_band = []
    for iband in range(dst_nb):
        dst_band.append(src_band[iband])
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
        b = tmp_data[0].astype(np.float32)
        g = tmp_data[1].astype(np.float32)
        r = tmp_data[2].astype(np.float32)
        fact = opts.fact
        b = (b*fact/32768.0).clip(0,1)
        g = (g*fact/32768.0).clip(0,1)
        r = (r*fact/32768.0).clip(0,1)
        if np.abs(opts.gamma-1.0) > 1.0e-6:
            rgb = np.power(np.dstack((r,g,b)),1.0/opts.gamma)
        else:
            rgb = np.dstack((r,g,b))
        fig.clear()
        if tmp_ny > tmp_nx:
            wx = tmp_nx/tmp_ny
            ax1 = fig.add_axes((0.5-0.5*wx,0,wx,1))
        else:
            wy = tmp_ny/tmp_nx
            ax1 = fig.add_axes((0,0.5-0.5*wy,1,wy))
        ax1.set_xticks([])
        ax1.set_yticks([])
        #ax1.plot(tmp_xp[::100,::100],tmp_yp[::100,::100],'k.')
        ax1.imshow(rgb,extent=(tmp_xmin,tmp_xmax,tmp_ymin,tmp_ymax),interpolation='none')
        if poly_buffer.area <= 0.0:
            pass
        elif poly_buffer.type == 'MultiPolygon':
            for p_search in path_search:
                patch = patches.PathPatch(p_search,facecolor='none',lw=2,ls='--')
                ax1.add_patch(patch)
        else:
            patch = patches.PathPatch(path_search,facecolor='none',lw=2,ls='--')
            ax1.add_patch(patch)
        ax1.plot(xg,yg,'ko')
        ax1.plot(xf,yf,'k:')
        for ntmp,xtmp,ytmp in zip(ng,xg,yg):
            ax1.text(xtmp,ytmp,'{}'.format(ntmp))
        ax1.set_xlim(tmp_xmin,tmp_xmax)
        ax1.set_ylim(tmp_ymin,tmp_ymax)
        plt.savefig(pdf,format='pdf')
        plt.draw()
        plt.pause(0.1)

    #break
if opts.debug:
    pdf.close()
