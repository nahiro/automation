#!/usr/bin/env python
import os
import sys
import shutil
import re
try:
    import gdal
except Exception:
    from osgeo import gdal
import numpy as np
import pandas as pd
from subprocess import call
from shapely.geometry import Point,Polygon
from matplotlib.path import Path
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.backends.backend_pdf import PdfPages
from argparse import ArgumentParser,RawTextHelpFormatter

# Default values
GPS_FNAM = 'gps_points.csv'
BUNCH_RMAX = 10.0 # m
BUNCH_EMAX = 2.0  # sigma
BUNCH_NMIN = 5
XMGN = 10.0 # m
YWID = 0.01 # m
BUFFER = 5.0 # m
FIGNAM = 'drone_subset.pdf'
FACT = 10.0
GAMMA = 2.2

# Read options
parser = ArgumentParser(formatter_class=lambda prog:RawTextHelpFormatter(prog,max_help_position=200,width=200))
parser.add_argument('-I','--src_geotiff',default=None,help='Source GeoTIFF name (%(default)s)')
parser.add_argument('-O','--dst_geotiff',default=None,help='Destination GeoTIFF name (%(default)s)')
parser.add_argument('-g','--gps_fnam',default=GPS_FNAM,help='GPS file name (%(default)s)')
parser.add_argument('-R','--bunch_rmax',default=BUNCH_RMAX,type=float,help='Maximum bunch distance in a plot in m (%(default)s)')
parser.add_argument('-E','--bunch_emax',default=BUNCH_EMAX,type=float,help='Maximum distance of a bunch from the fit line in sigma (%(default)s)')
parser.add_argument('-n','--bunch_nmin',default=BUNCH_NMIN,type=int,help='Minimum bunch number in a plot (%(default)s)')
parser.add_argument('-m','--xmgn',default=XMGN,type=float,help='X margin in m (%(default)s)')
parser.add_argument('-M','--ymgn',default=None,type=float,help='Y margin in m (%(default)s)')
parser.add_argument('-W','--ywid',default=YWID,type=float,help='Y width in m (%(default)s)')
parser.add_argument('-B','--buffer',default=BUFFER,type=float,help='Buffer radius in m (%(default)s)')
parser.add_argument('-F','--fignam',default=FIGNAM,help='Output figure name for debug (%(default)s)')
parser.add_argument('-t','--ax1_title',default=None,help='Axis1 title for debug (%(default)s)')
parser.add_argument('-S','--fact',default=FACT,type=float,help='Scale factor of output figure for debug (%(default)s)')
parser.add_argument('-G','--gamma',default=GAMMA,type=float,help='Gamma factor of output figure for debug (%(default)s)')
parser.add_argument('-i','--interp_point',default=False,action='store_true',help='Interpolate mode (%(default)s)')
parser.add_argument('-N','--remove_nan',default=False,action='store_true',help='Remove nan for debug (%(default)s)')
parser.add_argument('-d','--debug',default=False,action='store_true',help='Debug mode (%(default)s)')
parser.add_argument('-b','--batch',default=False,action='store_true',help='Batch mode (%(default)s)')
args = parser.parse_args()
if args.ymgn is None:
    args.ymgn = args.xmgn

df = pd.read_csv(args.gps_fnam,comment='#')
df.columns = df.columns.str.strip()
number_bunch = df['BunchNumber'].astype(int).values
indx_bunch = np.arange(len(number_bunch))
plot_bunch = df['PlotPaddy'].astype(int).values
if 'EastingI' in df.columns and 'NorthingI' in df.columns:
    x_bunch = df['EastingI'].astype(float).values
    y_bunch = df['NorthingI'].astype(float).values
elif 'EastingG' in df.columns and 'NorthingG' in df.columns:
    x_bunch = df['EastingG'].astype(float).values
    y_bunch = df['NorthingG'].astype(float).values
elif 'EastingO' in df.columns and 'NorthingO' in df.columns:
    x_bunch = df['EastingO'].astype(float).values
    y_bunch = df['NorthingO'].astype(float).values
else:
    x_bunch = df['Easting'].astype(float).values
    y_bunch = df['Northing'].astype(float).values

plots = np.unique(plot_bunch)
inside_plot = {}
removed_plot = {}
for plot in plots:
    cnd = (plot_bunch == plot)
    indx = indx_bunch[cnd]
    if len(indx) < args.bunch_nmin:
        raise ValueError('Error, plot={}, len(indx)={} >>> {}'.format(plot,len(indx),args.gps_fnam))
    xg = x_bunch[indx]
    yg = y_bunch[indx]
    indx_member = np.arange(len(indx))
    flag = []
    for i_temp in indx_member:
        cnd = (indx_member != i_temp)
        r = np.sqrt(np.square(xg[cnd]-xg[i_temp])+np.square(yg[cnd]-yg[i_temp]))
        if r.min() > args.bunch_rmax:
            flag.append(False)
        else:
            flag.append(True)
    flag = np.array(flag)
    inside_plot[plot] = indx[flag]
    removed_plot[plot] = indx[~flag]
    if len(inside_plot[plot]) < args.bunch_nmin:
        raise ValueError('Error, plot={}, len(inside_plot[{}])={} >>> {}'.format(plot,plot,len(inside_plot[plot]),args.gps_fnam))

ds = gdal.Open(args.src_geotiff)
src_nx = ds.RasterXSize
src_ny = ds.RasterYSize
src_nb = ds.RasterCount
src_prj = ds.GetProjection()
src_trans = ds.GetGeoTransform()
if src_trans[2] != 0.0 or src_trans[4] != 0.0:
    raise ValueError('Error, src_trans={}'.format(src_trans))
src_meta = ds.GetMetadata()
src_data = ds.ReadAsArray().reshape(src_nb,src_ny,src_nx)
src_band = []
for iband in range(src_nb):
    band = ds.GetRasterBand(iband+1)
    src_band.append(band.GetDescription())
src_dtype = band.DataType
src_nodata = band.GetNoDataValue()
ds = None
src_xmin = src_trans[0]
src_xstp = src_trans[1]
src_ymax = src_trans[3]
src_ystp = src_trans[5]
src_xgrd = src_xmin+(np.arange(src_nx)+0.5)*src_xstp
src_ygrd = src_ymax+(np.arange(src_ny)+0.5)*src_ystp
src_shape = (src_ny,src_nx)
src_indy,src_indx = np.indices(src_shape)
src_xp = src_trans[0]+(src_indx+0.5)*src_trans[1]+(src_indy+0.5)*src_trans[2]
src_yp = src_trans[3]+(src_indx+0.5)*src_trans[4]+(src_indy+0.5)*src_trans[5]

if args.debug:
    if not args.batch:
        plt.interactive(True)
    fig = plt.figure(1,facecolor='w',figsize=(5,5))
    pdf = PdfPages(args.fignam)
bnam,enam = os.path.splitext(args.dst_geotiff)
for plot in plots:
    onam = bnam+'_plot{}'.format(plot)+enam
    ng = number_bunch[inside_plot[plot]]
    xg = x_bunch[inside_plot[plot]]
    yg = y_bunch[inside_plot[plot]]
    # Fit line
    xc = xg.copy()
    yc = yg.copy()
    coef = np.polyfit(xc,yc,1)
    dist = np.abs(coef[0]*xc-yc+coef[1])/np.sqrt(coef[0]*coef[0]+1)
    cnd = (dist-dist.mean()) < args.bunch_emax*dist.std()
    if not np.all(cnd):
        xc = xc[cnd]
        yc = yc[cnd]
        coef = np.polyfit(xc,yc,1)
        dist = np.abs(coef[0]*xc-yc+coef[1])/np.sqrt(coef[0]*coef[0]+1)
        cnd = (dist-dist.mean()) < args.bunch_emax*dist.std()
        if not np.all(cnd):
            xc = xc[cnd]
            yc = yc[cnd]
            coef = np.polyfit(xc,yc,1)
    xf = np.array([xg.min()-args.xmgn,xg.max()+args.xmgn])
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
        xo = xf[-1]
        yo = yf[-1]
        xd,yd = np.negative([xd,yd])
    # Interpolate
    if args.interp_point and removed_plot[plot].size > 0:
        ng_removed = number_bunch[removed_plot[plot]]
        prod = (xg-xo)*xd+(yg-yo)*yd
        prod_removed = np.polyval(np.polyfit(ng,prod,1),ng_removed)
        xg_removed = xo+prod_removed*xd
        yg_removed = yo+prod_removed*yd
        inside_plot[plot] = np.append(inside_plot[plot],removed_plot[plot])
        ng = np.append(ng,ng_removed)
        xg = np.append(xg,xg_removed)
        yg = np.append(yg,yg_removed)
        indx = np.argsort(inside_plot[plot])
        inside_plot[plot] = inside_plot[plot][indx]
        ng = ng[indx]
        xg = xg[indx]
        yg = yg[indx]
    # Create subset image
    out_xmin = xg.min()-args.xmgn
    out_ymin = yg.min()-args.ymgn
    out_xmax = xg.max()+args.xmgn
    out_ymax = yg.max()+args.ymgn
    xoff = max(int((out_xmin-src_xmin)/np.abs(src_xstp)+0.5),0)
    yoff = max(int((src_ymax-out_ymax)/np.abs(src_ystp)+0.5),0)
    xsize = min(int((out_xmax-out_xmin)/np.abs(src_xstp)+0.5),src_nx-xoff)
    ysize = min(int((out_ymax-out_ymin)/np.abs(src_ystp)+0.5),src_ny-yoff)
    if xsize < 0 or ysize < 0:
        raise ValueError('Error, xoff={}, yoff={}, xsize={}, ysize={}'.format(xoff,yoff,xsize,ysize))
    dst_nx = xsize
    dst_ny = ysize
    dst_nb = src_nb
    dst_prj = src_prj
    dst_xmin = src_xgrd[xoff]-0.5*src_xstp
    dst_xstp = src_xstp
    dst_xmax = dst_xmin+dst_nx*dst_xstp
    dst_ymax = src_ygrd[yoff]-0.5*src_ystp
    dst_ystp = src_ystp
    dst_ymin = dst_ymax+dst_ny*dst_ystp
    dst_trans = [0.0]*len(src_trans)
    dst_trans[0] = dst_xmin
    dst_trans[1] = dst_xstp
    dst_trans[3] = dst_ymax
    dst_trans[5] = dst_ystp
    dst_meta = src_meta
    dst_data = src_data[:,yoff:yoff+ysize,xoff:xoff+xsize]
    dst_band = src_band
    dst_dtype = src_dtype
    if src_nodata is None:
        dst_nodata = np.nan
    else:
        dst_nodata = src_nodata
    dst_shape = (dst_ny,dst_nx)
    dst_xp = src_xp[yoff:yoff+ysize,xoff:xoff+xsize]
    dst_yp = src_yp[yoff:yoff+ysize,xoff:xoff+xsize]
    # Inner product
    prod = (xg-xo)*xd+(yg-yo)*yd
    indx = np.argsort(prod)
    xs = xg[indx]
    ys = yg[indx]
    points = []
    points.extend([(x,y+args.ywid) for x,y in zip(xs,ys)])
    points.extend([(x,y-args.ywid) for x,y in zip(xs[::-1],ys[::-1])])
    points.extend([(x,y+args.ywid) for x,y in zip(xs[:1],ys[:1])])
    poly_buffer = Polygon(points).buffer(args.buffer)
    # Search internal points
    flags = []
    path_search = []
    if poly_buffer.area <= 0.0:
        sys.stderr.write('Warning, poly_buffer.area={} >>> Plot# {}\n'.format(poly_buffer.area,plot))
    elif poly_buffer.type == 'MultiPolygon':
        sys.stderr.write('Warning, poly_buffer.type={} >>> Plot# {}\n'.format(poly_buffer.type,plot))
        for p in poly_buffer.geoms:
            p_search = Path(np.array(p.exterior.coords.xy).swapaxes(0,1))
            path_search.append(p_search)
            if len(flags) < 1:
                flags = p_search.contains_points(np.hstack((dst_xp.reshape(-1,1),dst_yp.reshape(-1,1))),radius=0.0).reshape(dst_shape)
            else:
                flags |= p_search.contains_points(np.hstack((dst_xp.reshape(-1,1),dst_yp.reshape(-1,1))),radius=0.0).reshape(dst_shape)
    else:
        path_search = Path(np.array(poly_buffer.buffer(0.0).exterior.coords.xy).swapaxes(0,1))
        flags = path_search.contains_points(np.hstack((dst_xp.reshape(-1,1),dst_yp.reshape(-1,1))),radius=0.0).reshape(dst_shape)
    dst_data[:,~flags] = dst_nodata
    # Write GeoTIFF
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
    if args.debug:
        b = dst_data[0].astype(np.float32)
        g = dst_data[1].astype(np.float32)
        r = dst_data[2].astype(np.float32)
        fact = args.fact
        b = (b*fact/32768.0).clip(0,1)
        g = (g*fact/32768.0).clip(0,1)
        r = (r*fact/32768.0).clip(0,1)
        if np.abs(args.gamma-1.0) > 1.0e-6:
            rgb = np.power(np.dstack((r,g,b)),1.0/args.gamma)
        else:
            rgb = np.dstack((r,g,b))
        if args.remove_nan:
            rgb[~flags,:] = 1.0
        fig.clear()
        if dst_ny > dst_nx:
            wx = dst_nx/dst_ny*0.95
            ax1 = fig.add_axes((0.5-0.5*wx,0,wx,0.95))
        else:
            wy = dst_ny/dst_nx
            ax1 = fig.add_axes((0,0.5-0.5*wy,1,wy))
        ax1.set_xticks([])
        ax1.set_yticks([])
        #ax1.plot(dst_xp[::100,::100],dst_yp[::100,::100],'k.')
        ax1.imshow(rgb,extent=(dst_xmin,dst_xmax,dst_ymin,dst_ymax),interpolation='none')
        if not args.remove_nan:
            if poly_buffer.area <= 0.0:
                pass
            elif poly_buffer.type == 'MultiPolygon':
                for p_search in path_search:
                    patch = patches.PathPatch(p_search,facecolor='none',lw=2,ls='--')
                    ax1.add_patch(patch)
            else:
                patch = patches.PathPatch(path_search,facecolor='none',lw=2,ls='--')
                ax1.add_patch(patch)
        ax1.plot(xg,yg,'o',mfc='none',mec='k')
        ax1.plot(xf,yf,'k:')
        for ntmp,xtmp,ytmp in zip(ng,xg,yg):
            if np.isnan(xtmp) or np.isnan(ytmp):
                continue
            ax1.text(xtmp,ytmp,'{}'.format(ntmp))
        if args.remove_nan:
            xp = dst_xp[flags]
            yp = dst_yp[flags]
            fig_xmin = xp.min()
            fig_xmax = xp.max()
            fig_ymin = yp.min()
            fig_ymax = yp.max()
        else:
            fig_xmin = dst_xmin
            fig_xmax = dst_xmax
            fig_ymin = dst_ymin
            fig_ymax = dst_ymax
        ax1.set_xlim(fig_xmin,fig_xmax)
        ax1.set_ylim(fig_ymin,fig_ymax)
        if args.ax1_title is not None:
            ax1.set_title('{} (Plot{})'.format(args.ax1_title,plot))
        plt.savefig(pdf,format='pdf')
        if not args.batch:
            plt.draw()
            plt.pause(0.1)
    #break
if args.debug:
    pdf.close()
