#!/usr/bin/env python
import os
import sys
import shutil
import tempfile
import re
try:
    import gdal
except Exception:
    from osgeo import gdal
import numpy as np
from itertools import combinations
from skimage.measure import label,regionprops
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.patches as patches
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib.backends.backend_pdf import PdfPages
from argparse import ArgumentParser,RawTextHelpFormatter

# Constants
RR_PARAMS = ['Grg','Lrg','Lb','Lg','Lr','Le','Ln','Srg','Sb','Sg','Sr','Se','Sn']
SR_PARAMS = ['Nr','Br']
CRITERIAS = ['Distance','Area']
bands = {}
bands['b'] = 'Blue'
bands['g'] = 'Green'
bands['r'] = 'Red'
bands['e'] = 'RedEdge'
bands['n'] = 'NIR'

# Default values
CSV_FNAM = 'gps_points.dat'
FIGNAM = 'drone_identify_points.pdf'
FACT = 10.0
GAMMA = 2.2
PIXEL_RMAX = 1.0  # m
POINT_DMAX = 1.0  # m
POINT_LWID = 0.5  # m
#POINT_SMIN = 0.08 # m
#POINT_SMAX = 0.45 # m
POINT_SMIN = 0.015 # m2
POINT_SMAX = 0.105 # m2
POINT_AREA = 0.05 # m2
POINT_NMIN = 5
BUNCH_RMAX = 10.0 # m
BUNCH_EMAX = 2.0  # sigma
BUNCH_NMIN = 5
RR_PARAM = 'Lrg'
SR_PARAM = 'Nr'
RTHR_MIN = 0.0
RTHR_MAX = 1.0
RSTP = 0.01
STHR = 1.0
CRITERIA = 'Distance'

# Read options
parser = ArgumentParser(formatter_class=lambda prog:RawTextHelpFormatter(prog,max_help_position=200,width=200))
parser.add_argument('-I','--src_geotiff',default=None,help='Source GeoTIFF name (%(default)s)')
parser.add_argument('-g','--csv_fnam',default=CSV_FNAM,help='CSV file name (%(default)s)')
parser.add_argument('-o','--out_fnam',default=None,help='Output file name (%(default)s)')
parser.add_argument('-A','--assign_fnam',default=None,help='Assignment file name (%(default)s)')
parser.add_argument('-R','--pixel_rmax',default=PIXEL_RMAX,type=float,help='Maximum pixel distance of a point in m (%(default)s)')
parser.add_argument('-D','--point_dmax',default=POINT_DMAX,type=float,help='Maximum distance of a point from the fit line in m (%(default)s)')
parser.add_argument('-W','--point_lwid',default=POINT_LWID,type=float,help='Maximum distance of a point from the selected line in m (%(default)s)')
parser.add_argument('-m','--point_smin',default=POINT_SMIN,type=float,help='Minimum point area in m2 (%(default)s)')
parser.add_argument('-M','--point_smax',default=POINT_SMAX,type=float,help='Maximum point area in m2 (%(default)s)')
parser.add_argument('-a','--point_area',default=POINT_AREA,type=float,help='Standard point area in m2 (%(default)s)')
parser.add_argument('-N','--point_nmin',default=POINT_NMIN,type=int,help='Minimum point number in a plot (%(default)s)')
parser.add_argument('--bunch_rmax',default=BUNCH_RMAX,type=float,help='Maximum bunch distance in a plot in m (%(default)s)')
parser.add_argument('--bunch_emax',default=BUNCH_EMAX,type=float,help='Maximum distance of a bunch from the fit line in sigma (%(default)s)')
parser.add_argument('--bunch_nmin',default=BUNCH_NMIN,type=int,help='Minimum bunch number in a plot (%(default)s)')
parser.add_argument('-p','--rr_param',default=RR_PARAM,help='Redness ratio parameter (%(default)s)')
parser.add_argument('-P','--sr_param',default=SR_PARAM,help='Signal ratio parameter (%(default)s)')
parser.add_argument('-t','--rthr_min',default=RTHR_MIN,type=float,help='Min threshold of redness ratio (%(default)s)')
parser.add_argument('-T','--rthr_max',default=RTHR_MAX,type=float,help='Max threshold of redness ratio (%(default)s)')
parser.add_argument('-r','--rstp',default=RSTP,type=float,help='Threshold step of redness ratio (%(default)s)')
parser.add_argument('-S','--sthr',default=STHR,type=float,help='Threshold of signal ratio (%(default)s)')
parser.add_argument('-C','--criteria',default=CRITERIA,help='Selection criteria (%(default)s)')
parser.add_argument('-F','--fignam',default=FIGNAM,help='Output figure name for debug (%(default)s)')
parser.add_argument('--fact',default=FACT,type=float,help='Scale factor of output figure for debug (%(default)s)')
parser.add_argument('-G','--gamma',default=GAMMA,type=float,help='Gamma factor of output figure for debug (%(default)s)')
parser.add_argument('-z','--ax1_zmin',default=None,type=float,help='Axis1 Z min for debug (%(default)s)')
parser.add_argument('-Z','--ax1_zmax',default=None,type=float,help='Axis1 Z max for debug (%(default)s)')
parser.add_argument('-s','--ax1_zstp',default=None,type=float,help='Axis1 Z stp for debug (%(default)s)')
parser.add_argument('--ax1_title',default=None,help='Axis1 title for debug (%(default)s)')
parser.add_argument('-E','--ignore_error',default=False,action='store_true',help='Ignore error (%(default)s)')
parser.add_argument('-H','--header_none',default=False,action='store_true',help='Read csv file with no header (%(default)s)')
parser.add_argument('-n','--remove_nan',default=False,action='store_true',help='Remove nan for debug (%(default)s)')
parser.add_argument('-d','--debug',default=False,action='store_true',help='Debug mode (%(default)s)')
parser.add_argument('-b','--batch',default=False,action='store_true',help='Batch mode (%(default)s)')
args = parser.parse_args()
if not args.rr_param in RR_PARAMS:
    raise ValueError('Error, unknown redness ratio parameter >>> {}'.format(args.rr_param))
if not args.sr_param in SR_PARAMS:
    raise ValueError('Error, unknown signal ratio parameter >>> {}'.format(args.sr_param))
if not args.criteria in CRITERIAS:
    raise ValueError('Error, unsupported criteria >>> {}'.format(args.criteria))
if args.out_fnam is None:
    bnam,enam = os.path.splitext(args.csv_fnam)
    args.out_fnam = bnam+'_identify'+enam

if args.assign_fnam is not None:
    assign = {}
    with open(args.assign_fnam,'r') as fp:
        for line in fp:
            item = line.split()
            if len(item) < 2:
                continue
            if item[0][0] == '#':
                continue
            p_org = int(item[0])
            p_new = int(item[1])
            if p_new != 0:
                assign[p_org] = p_new

comments = ''
header = None
easting = None
northing = None
loc_bunch = []
number_bunch = []
plot_bunch = []
x_bunch = []
y_bunch = []
rest_bunch = []
with open(args.csv_fnam,'r') as fp:
    #Location, BunchNumber, PlotPaddy, EastingG, NorthingG, PlantDate, Age, Tiller, BLB, Blast, Borer, Rat, Hopper, Drought
    #           15,   1,   1,  750949.8273,  9242821.0756, 2022-01-08,    55,  27,   1,   0,   5,   0,   0,   0
    for line in fp:
        if len(line) < 1:
            continue
        elif line[0] == '#':
            comments += line
            continue
        elif not args.header_none and header is None:
            header = line # skip header
            item = [s.strip() for s in header.split(',')]
            if len(item) < 6:
                raise ValueError('Error in header ({}) >>> {}'.format(args.csv_fnam,header))
            if (item[0] != 'Location' or item[1] != 'BunchNumber' or item[2] != 'PlotPaddy' or
                not item[3] in ['Easting','EastingO','EastingG','EastingI'] or
                not item[4] in ['Northing','NorthingO','NorthingG','NorthingI']):
                raise ValueError('Error in header ({}) >>> {}'.format(args.csv_fnam,header))
            easting = item[3]
            northing = item[4]
            continue
        m = re.search('^([^,]+),([^,]+),([^,]+),([^,]+),([^,]+),(.*)',line)
        if not m:
            continue
        loc_bunch.append(m.group(1).strip())
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
size_plot = {}
loc_plot = {}
number_plot = {}
rest_plot = {}
inside_plot = {}
removed_plot = {}
for plot in plots:
    cnd = (plot_bunch == plot)
    indx = indx_bunch[cnd]
    size_plot[plot] = len(indx)
    if size_plot[plot] < args.bunch_nmin:
        raise ValueError('Error, plot={}, size_plot[{}]={} >>> {}'.format(plot,plot,size_plot[plot],args.csv_fnam))
    loc_plot[plot] = loc_bunch[indx]
    number_plot[plot] = number_bunch[indx]
    rest_plot[plot] = rest_bunch[indx]
    xg = x_bunch[indx]
    yg = y_bunch[indx]
    indx_member = np.arange(size_plot[plot])
    if not np.array_equal(np.argsort(number_plot[plot]),indx_member): # wrong order
        raise ValueError('Error, plot={}, number_plot[{}]={} >>> {}'.format(plot,plot,number_plot[plot],args.csv_fnam))
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
        raise ValueError('Error, plot={}, len(inside_plot[{}])={} >>> {}'.format(plot,plot,len(inside_plot[plot]),args.csv_fnam))

if args.debug:
    if not args.batch:
        plt.interactive(True)
    fig = plt.figure(1,facecolor='w',figsize=(5,5))
    plt.subplots_adjust(top=0.9,bottom=0.1,left=0.05,right=0.85)
    pdf = PdfPages(args.fignam)
tmp_fp = tempfile.TemporaryFile(mode='r+')
if len(comments) > 0:
    tmp_fp.write(comments)
if header is not None:
    tmp_fp.write(header.replace(easting,'EastingI').replace(northing,'NorthingI'))
bnam,enam = os.path.splitext(args.src_geotiff)
err_list = []
for plot in plots:
    # Read redness ratio image
    onam = bnam+'_plot{}_rr'.format(plot)+enam
    ds = gdal.Open(onam)
    rr_nx = ds.RasterXSize
    rr_ny = ds.RasterYSize
    rr_nb = ds.RasterCount
    rr_shape = (rr_ny,rr_nx)
    rr_trans = ds.GetGeoTransform()
    if rr_trans[2] != 0.0 or rr_trans[4] != 0.0:
        raise ValueError('Error, rr_trans={}'.format(rr_trans))
    rr = None
    sr = None
    rr_band = []
    for iband in range(rr_nb):
        band = ds.GetRasterBand(iband+1)
        rr_band.append(band.GetDescription())
        if rr_band[iband] == args.rr_param:
            rr = band.ReadAsArray().reshape(rr_ny,rr_nx)
        elif rr_band[iband] == args.sr_param:
            sr = band.ReadAsArray().reshape(rr_ny,rr_nx)
    rr_xmin = rr_trans[0]
    rr_xstp = rr_trans[1]
    rr_ymax = rr_trans[3]
    rr_ystp = rr_trans[5]
    rr_xmax = rr_xmin+rr_nx*rr_xstp
    rr_ymin = rr_ymax+rr_ny*rr_ystp
    rr_xgrd = rr_xmin+(np.arange(rr_nx)+0.5)*rr_xstp
    rr_ygrd = rr_ymax+(np.arange(rr_ny)+0.5)*rr_ystp
    ds = None
    rr_indy,rr_indx = np.indices(rr_shape)
    rr_xp = rr_trans[0]+(rr_indx+0.5)*rr_trans[1]+(rr_indy+0.5)*rr_trans[2]
    rr_yp = rr_trans[3]+(rr_indx+0.5)*rr_trans[4]+(rr_indy+0.5)*rr_trans[5]
    if rr is None:
        raise ValueError('Error in finding {} ({}) >>> {}'.format(args.rr_param,rr_band,onam))
    if sr is None:
        raise ValueError('Error in finding {} ({}) >>> {}'.format(args.sr_param,rr_band,onam))
    cnd_sr = (sr > args.sthr)
    point_rmax = np.sqrt(args.point_smax/np.pi)
    area_unit = np.abs(rr_xstp*rr_ystp)
    # Fit line
    xg_bunch = x_bunch[inside_plot[plot]]
    yg_bunch = y_bunch[inside_plot[plot]]
    xc_bunch = xg_bunch.copy()
    yc_bunch = yg_bunch.copy()
    coef = np.polyfit(xc_bunch,yc_bunch,1)
    dist = np.abs(coef[0]*xc_bunch-yc_bunch+coef[1])/np.sqrt(coef[0]*coef[0]+1)
    cnd = (dist-dist.mean()) < args.bunch_emax*dist.std()
    if not np.all(cnd):
        xc_bunch = xc_bunch[cnd]
        yc_bunch = yc_bunch[cnd]
        coef = np.polyfit(xc_bunch,yc_bunch,1)
        dist = np.abs(coef[0]*xc_bunch-yc_bunch+coef[1])/np.sqrt(coef[0]*coef[0]+1)
        cnd = (dist-dist.mean()) < args.bunch_emax*dist.std()
        if not np.all(cnd):
            xc_bunch = xc_bunch[cnd]
            yc_bunch = yc_bunch[cnd]
            coef = np.polyfit(xc_bunch,yc_bunch,1)
    xf_bunch = rr_xgrd.copy()
    yf_bunch = np.polyval(coef,xf_bunch)
    # Origin
    xo_bunch = xf_bunch[0]
    yo_bunch = yf_bunch[0]
    # Unit direction vector
    xd_bunch = xf_bunch[-1]-xo_bunch
    yd_bunch = yf_bunch[-1]-yo_bunch
    norm = 1.0/np.sqrt(xd_bunch*xd_bunch+yd_bunch*yd_bunch)
    xd_bunch *= norm
    yd_bunch *= norm
    prod = (xg_bunch-xo_bunch)*xd_bunch+(yg_bunch-yo_bunch)*yd_bunch
    cnd = (np.diff(prod) < 0.0)
    if cnd.sum() > (~cnd).sum(): # opposite direction
        xo_bunch = xf_bunch[-1]
        yo_bunch = yf_bunch[-1]
        xd_bunch,yd_bunch = np.negative([xd_bunch,yd_bunch])
    # Search points
    cnd_dist = None
    rthr = args.rthr_max
    err = False
    xsav_point = []
    ysav_point = []
    while True:
        if rthr < args.rthr_min:
            sys.stderr.write('Warning, rthr={} (Plot{})\n'.format(rthr,plot))
            sys.stderr.flush()
            err = True
            err_list.append(plot)
            break
        elif cnd_dist is None:
            cnd_all = cnd_sr & (rr > rthr)
        else:
            cnd_all = cnd_sr & cnd_dist & (rr > rthr)
        rthr -= args.rstp
        if cnd_all.sum() < 1:
            continue
        labels,num = label(cnd_all,return_num=True)
        if num < args.point_nmin:
            continue
        number_point = []
        xmin_point = []
        xmax_point = []
        ymin_point = []
        ymax_point = []
        x_point = []
        y_point = []
        for region in regionprops(labels):
            minr,minc,maxr,maxc = region.bbox
            xmin = rr_xmin+(minc+0.5)*rr_xstp
            xmax = rr_xmin+(maxc-0.5)*rr_xstp
            ymax = rr_ymax+(minr+0.5)*rr_ystp
            ymin = rr_ymax+(maxr-0.5)*rr_ystp
            indy = region.coords[:,0]
            indx = region.coords[:,1]
            x = rr_xmin+(indx+0.5)*rr_xstp
            y = rr_ymax+(indy+0.5)*rr_ystp
            flag = False
            for i_point in range(len(number_point)):
                if (xmax < xmin_point[i_point]-args.pixel_rmax) or (xmin > xmax_point[i_point]+args.pixel_rmax) \
                or (ymax < ymin_point[i_point]-args.pixel_rmax) or (ymin > ymax_point[i_point]+args.pixel_rmax):
                    continue
                for xtmp,ytmp in zip(x,y):
                    r = np.sqrt(np.square(xtmp-x_point[i_point])+np.square(ytmp-y_point[i_point]))
                    if r.min() < args.pixel_rmax:
                        number_point[i_point] += region.area
                        xmin_point[i_point] = min(xmin_point[i_point],xmin)
                        xmax_point[i_point] = max(xmax_point[i_point],xmax)
                        ymin_point[i_point] = min(ymin_point[i_point],ymin)
                        ymax_point[i_point] = max(ymax_point[i_point],ymax)
                        x_point[i_point] = np.append(x_point[i_point],x)
                        y_point[i_point] = np.append(y_point[i_point],y)
                        flag = True
                        break
                if flag:
                    break
            if not flag:
                number_point.append(region.area)
                xmin_point.append(xmin)
                xmax_point.append(xmax)
                ymin_point.append(ymin)
                ymax_point.append(ymax)
                x_point.append(x)
                y_point.append(y)
        num = len(number_point)
        if num < args.point_nmin:
            continue
        area_point = np.array(number_point)*area_unit
        indexes_to_be_removed = []
        for i_point in range(num):
            #xwid = xmax_point[i_point]-xmin_point[i_point]
            #ywid = ymax_point[i_point]-ymin_point[i_point]
            #if (xwid < args.point_smin) or (xwid > args.point_smax) or (ywid < args.point_smin) or (ywid > args.point_smax):
            if (area_point[i_point] < args.point_smin) or (area_point[i_point] > args.point_smax):
                indexes_to_be_removed.append(i_point)
        for indx in sorted(indexes_to_be_removed,reverse=True):
            del number_point[indx]
            del xmin_point[indx]
            del xmax_point[indx]
            del ymin_point[indx]
            del ymax_point[indx]
            del x_point[indx]
            del y_point[indx]
            area_point = np.delete(area_point,indx)
        num = len(number_point)
        if num < args.point_nmin:
            continue
        xctr_point = np.array([x.mean() for x in x_point])
        yctr_point = np.array([y.mean() for y in y_point])
        number_core = [(np.sqrt(np.square(x_point[i_point]-xctr_point[i_point])
                               +np.square(y_point[i_point]-yctr_point[i_point])) < point_rmax).sum() for i_point in range(num)]
        area_core = np.array(number_core)*area_unit
        indexes_to_be_removed = []
        for i_point in range(num):
            if (area_core[i_point] < args.point_smin):
                indexes_to_be_removed.append(i_point)
        for indx in sorted(indexes_to_be_removed,reverse=True):
            del number_point[indx]
            del number_core[indx]
            del xmin_point[indx]
            del xmax_point[indx]
            del ymin_point[indx]
            del ymax_point[indx]
            del x_point[indx]
            del y_point[indx]
            area_point = np.delete(area_point,indx)
            area_core = np.delete(area_core,indx)
            xctr_point = np.delete(xctr_point,indx)
            yctr_point = np.delete(yctr_point,indx)
        num = len(number_point)
        if num < args.point_nmin:
            continue
        # Select line
        indx_point = np.arange(num)
        indx_select = None
        nmax = -1
        rmin = 1.0e10
        for c in combinations(indx_point,2):
            indx_comb = np.array(c)
            indx_others = np.array([i for i in indx_point if i not in c])
            coef = np.polyfit(xctr_point[indx_comb],yctr_point[indx_comb],1)
            dist = np.abs(coef[0]*xctr_point[indx_others]-yctr_point[indx_others]+coef[1])/np.sqrt(coef[0]*coef[0]+1)
            cnd = (dist < args.point_lwid)
            n = cnd.sum()
            if n == cnd.size: # all passed
                indx_select = indx_point
                break
            elif n > nmax:
                r = np.sqrt(np.square(dist[cnd]).mean())
                nmax = n
                rmin = r
                indx_select = np.sort(np.append(indx_comb,indx_others[cnd]))
            elif n == nmax:
                r = np.sqrt(np.square(dist[cnd]).mean())
                if r < rmin:
                    rmin = r
                    indx_select = np.sort(np.append(indx_comb,indx_others[cnd]))
        if indx_select is None:
            raise ValueError('Error in selecting line, plot={}'.format(plot))
        xc_point = xctr_point[indx_select]
        yc_point = yctr_point[indx_select]
        coef = np.polyfit(xc_point,yc_point,1)
        xf_point = rr_xgrd.copy()
        yf_point = np.polyval(coef,xf_point)
        # Origin
        xo_point = xf_point[0]
        yo_point = yf_point[0]
        # Unit direction vector
        xd_point = xf_point[-1]-xo_point
        yd_point = yf_point[-1]-yo_point
        norm = 1.0/np.sqrt(xd_point*xd_point+yd_point*yd_point)
        xd_point *= norm
        yd_point *= norm
        if (xd_bunch*xd_point+yd_bunch*yd_point) < 0.0: # opposite direction
            xo_point = xf_point[-1]
            yo_point = yf_point[-1]
            xd_point,yd_point = np.negative([xd_point,yd_point])
        indexes_to_be_removed = []
        for i_point in range(num):
            dist = np.abs(coef[0]*xctr_point[i_point]-yctr_point[i_point]+coef[1])/np.sqrt(coef[0]*coef[0]+1)
            if dist > args.point_dmax:
                indexes_to_be_removed.append(i_point)
        for indx in sorted(indexes_to_be_removed,reverse=True):
            del number_point[indx]
            del number_core[indx]
            del xmin_point[indx]
            del xmax_point[indx]
            del ymin_point[indx]
            del ymax_point[indx]
            del x_point[indx]
            del y_point[indx]
            area_point = np.delete(area_point,indx)
            area_core = np.delete(area_core,indx)
            xctr_point = np.delete(xctr_point,indx)
            yctr_point = np.delete(yctr_point,indx)
        num = len(number_point)
        if len(xctr_point) >= len(xsav_point):
            xsav_point = xctr_point.copy()
            ysav_point = yctr_point.copy()
        if num >= size_plot[plot]:
            if num > size_plot[plot]:
                if args.criteria == 'Area':
                    indexes_to_be_removed = np.argsort(np.abs(area_point-args.point_area))[size_plot[plot]:]
                elif args.criteria == 'Distance':
                    dist_point = np.abs(coef[0]*xctr_point-yctr_point+coef[1])/np.sqrt(coef[0]*coef[0]+1)
                    indexes_to_be_removed = np.argsort(dist_point)[size_plot[plot]:]
                else:
                    raise ValueError('Error, unsupported criteria >>> {}'.format(args.criteria))
                for indx in sorted(indexes_to_be_removed,reverse=True):
                    del number_point[indx]
                    del number_core[indx]
                    del xmin_point[indx]
                    del xmax_point[indx]
                    del ymin_point[indx]
                    del ymax_point[indx]
                    del x_point[indx]
                    del y_point[indx]
                    area_point = np.delete(area_point,indx)
                    area_core = np.delete(area_core,indx)
                    xctr_point = np.delete(xctr_point,indx)
                    yctr_point = np.delete(yctr_point,indx)
            prod = (xctr_point-xo_point)*xd_point+(yctr_point-yo_point)*yd_point
            indx = np.argsort(prod)
            xctr_point = xctr_point[indx]
            yctr_point = yctr_point[indx]
            break
        else:
            dist = np.abs(coef[0]*rr_xp-rr_yp+coef[1])/np.sqrt(coef[0]*coef[0]+1)
            cnd_dist = (dist < args.point_dmax)
    if err:
        if len(xsav_point) < 1 or cnd_dist is None:
            raise ValueError('Error, len(xsav_point)={} cnd_dist={}'.format(len(xsav_point),cnd_dist))
        cnd = (cnd_dist) & (~np.isnan(rr))
        prod = (rr_xp[cnd]-xo_point)*xd_point+(rr_yp[cnd]-yo_point)*yd_point
        pmin = np.nanmin(prod)
        pmax = np.nanmax(prod)
        xsav_point = np.array(xsav_point)
        ysav_point = np.array(ysav_point)
        prod = (xsav_point-xo_point)*xd_point+(ysav_point-yo_point)*yd_point
        indx = np.argsort(prod)
        xtmp_point = xsav_point[indx].copy()
        ytmp_point = ysav_point[indx].copy()
        r1 = np.square(xo_point+pmin*xd_point-xtmp_point[0])+np.square(yo_point+pmin*yd_point-ytmp_point[0])
        r2 = np.square(xo_point+pmax*xd_point-xtmp_point[-1])+np.square(yo_point+pmax*yd_point-ytmp_point[-1])
        xctr_point = [np.nan]*size_plot[plot]
        yctr_point = [np.nan]*size_plot[plot]
        if r1 < r2: # Small numbers are missing
            sys.stderr.write('Warning, small numbers seem to be missing (Plot{})\n'.format(plot))
            sys.stderr.flush()
            for i in range(len(xtmp_point)):
                xctr_point[-i-1] = xtmp_point[-i-1]
                yctr_point[-i-1] = ytmp_point[-i-1]
        else: # Large numbers are missing
            sys.stderr.write('Warning, large numbers seem to be missing (Plot{})\n'.format(plot))
            sys.stderr.flush()
            for i in range(len(xtmp_point)):
                xctr_point[i] = xtmp_point[i]
                yctr_point[i] = ytmp_point[i]
    if args.assign_fnam is not None:
        xtmp_point = xctr_point.copy()
        ytmp_point = yctr_point.copy()
        n = list(number_plot[plot])
        for p_org,p_new in assign.items():
            if p_org in number_plot[plot]:
                i_org = n.index(p_org)
                if p_new < 0:
                    xtmp_point[i_org] = np.nan
                    ytmp_point[i_org] = np.nan
                else:
                    if not p_new in number_plot[plot]:
                        raise ValueError('Assignment error, invalid number {} for plot {}'.format(p_new,plot))
                    i_new = n.index(p_new)
                    xtmp_point[i_new] = xctr_point[i_org]
                    ytmp_point[i_new] = yctr_point[i_org]
                    if not p_org in assign.values():
                        xtmp_point[i_org] = np.nan
                        ytmp_point[i_org] = np.nan
        xctr_point = xtmp_point
        yctr_point = ytmp_point
    for i in range(size_plot[plot]):
        tmp_fp.write('{:>13s}, {:3d}, {:3d}, {:12.4f}, {:13.4f},{}\n'.format(loc_plot[plot][i],number_plot[plot][i],plot,xctr_point[i],yctr_point[i],rest_plot[plot][i]))
    rr_copy = rr.copy()
    if cnd_dist is None:
        cnd = cnd_sr
    else:
        cnd = cnd_sr & cnd_dist
    rr_copy[~cnd] = np.nan

    if args.debug:
        # Redness Ratio check image
        fig.clear()
        ax1 = plt.subplot(111)
        ax1.set_xticks([])
        ax1.set_yticks([])
        if args.ax1_zmin is not None and args.ax1_zmax is not None:
            im = ax1.imshow(rr_copy,extent=(rr_xmin,rr_xmax,rr_ymin,rr_ymax),vmin=args.ax1_zmin,vmax=args.ax1_zmax,cmap=cm.jet,interpolation='none')
        elif args.ax1_zmin is not None:
            im = ax1.imshow(rr_copy,extent=(rr_xmin,rr_xmax,rr_ymin,rr_ymax),vmin=args.ax1_zmin,cmap=cm.jet,interpolation='none')
        elif args.ax1_zmax is not None:
            im = ax1.imshow(rr_copy,extent=(rr_xmin,rr_xmax,rr_ymin,rr_ymax),vmax=args.ax1_zmax,cmap=cm.jet,interpolation='none')
        else:
            im = ax1.imshow(rr_copy,extent=(rr_xmin,rr_xmax,rr_ymin,rr_ymax),cmap=cm.jet,interpolation='none')
        divider = make_axes_locatable(ax1)
        cax = divider.append_axes('right',size='5%',pad=0.05)
        if args.ax1_zstp is not None:
            if args.ax1_zmin is not None:
                zmin = (np.floor(args.ax1_zmin/args.ax1_zstp)-1.0)*args.ax1_zstp
            else:
                zmin = (np.floor(np.nanmin(rr)/args.ax1_zstp)-1.0)*args.ax1_zstp
            if args.ax1_zmax is not None:
                zmax = args.ax1_zmax+0.1*args.ax1_zstp
            else:
                zmax = np.nanmax(rr)+0.1*args.ax1_zstp
            ax2 = plt.colorbar(im,cax=cax,ticks=np.arange(zmin,zmax,args.ax1_zstp)).ax
        else:
            ax2 = plt.colorbar(im,cax=cax).ax
        ax2.minorticks_on()
        if args.rr_param[0] == 'L':
            if len(args.rr_param) == 2:
                band1 = args.rr_param[1]
                pnam = 'Redness Ratio (Local {})'.format(bands[band1])
            elif len(args.rr_param) == 3:
                band1 = args.rr_param[1]
                band2 = args.rr_param[2]
                pnam = 'Redness Ratio (Local {} + {})'.format(bands[band1],bands[band2])
            else:
                raise ValueError('Error, len(args.rr_param)={} >>> {}'.format(len(args.rr_param),args.rr_param))
        elif args.rr_param[0] == 'G':
            if len(args.rr_param) == 2:
                band1 = args.rr_param[1]
                pnam = 'Redness Ratio (Global {})'.format(bands[band1])
            elif len(args.rr_param) == 3:
                band1 = args.rr_param[1]
                band2 = args.rr_param[2]
                pnam = 'Redness Ratio (Global {} + {})'.format(bands[band1],bands[band2])
            else:
                raise ValueError('Error, len(args.rr_param)={} >>> {}'.format(len(args.rr_param),args.rr_param))
        elif args.rr_param[0] == 'S':
            if len(args.rr_param) == 2:
                band1 = args.rr_param[1]
                pnam = 'Redness Ratio ({})'.format(bands[band1])
            elif len(args.rr_param) == 3:
                band1 = args.rr_param[1]
                band2 = args.rr_param[2]
                pnam = 'Redness Ratio ({} + {})'.format(bands[band1],bands[band2])
            else:
                raise ValueError('Error, len(args.rr_param)={} >>> {}'.format(len(args.rr_param),args.rr_param))
        else:
            raise ValueError('Error, args.rr_param={}'.format(args.rr_param))
        ax2.set_ylabel(pnam)
        ax2.yaxis.set_label_coords(3.5,0.5)
        #for i_point in range(len(number_point)):
        #    rect = patches.Rectangle((xmin_point[i_point],ymin_point[i_point]),
        #                              xmax_point[i_point]-xmin_point[i_point],
        #                              ymax_point[i_point]-ymin_point[i_point],fill=False,edgecolor='red',linewidth=2)
            #ax1.add_patch(rect)
        ax1.plot(xctr_point,yctr_point,'o',mfc='none',mec='k')
        ax1.plot(xf_point,yf_point,'k:')
        ng = number_plot[plot]
        for ntmp,xtmp,ytmp in zip(ng,xctr_point,yctr_point):
            if np.isnan(xtmp) or np.isnan(ytmp):
                continue
            ax1.text(xtmp,ytmp,'{}'.format(ntmp))
        if args.remove_nan:
            cnd = ~np.isnan(rr)
            xp = rr_xp[cnd]
            yp = rr_yp[cnd]
            fig_xmin = xp.min()
            fig_xmax = xp.max()
            fig_ymin = yp.min()
            fig_ymax = yp.max()
        else:
            fig_xmin = rr_xmin
            fig_xmax = rr_xmax
            fig_ymin = rr_ymin
            fig_ymax = rr_ymax
        ax1.set_xlim(fig_xmin,fig_xmax)
        ax1.set_ylim(fig_ymin,fig_ymax)
        if args.ax1_title is not None:
            ax1.set_title('{} (Plot{})'.format(args.ax1_title,plot))
        plt.savefig(pdf,format='pdf')
        if not args.batch:
            plt.draw()
            plt.pause(0.1)
        snam = bnam+'_plot{}'.format(plot)+enam
        # RGB check image
        ds = gdal.Open(snam)
        src_nx = ds.RasterXSize
        src_ny = ds.RasterYSize
        src_nb = ds.RasterCount
        src_shape = (src_ny,src_nx)
        src_trans = ds.GetGeoTransform()
        src_data = ds.ReadAsArray().reshape(src_nb,src_ny,src_nx)
        ds = None
        if src_shape != rr_shape:
            raise ValueError('Error, src_shape={}, rr_shape={}'.format(src_shape,rr_shape))
        if src_trans != rr_trans:
            raise ValueError('Error, src_trans={}, rr_trans={}'.format(src_trans,rr_trans))
        b = src_data[0].astype(np.float32)
        g = src_data[1].astype(np.float32)
        r = src_data[2].astype(np.float32)
        fact = args.fact
        b = (b*fact/32768.0).clip(0,1)
        g = (g*fact/32768.0).clip(0,1)
        r = (r*fact/32768.0).clip(0,1)
        if np.abs(args.gamma-1.0) > 1.0e-6:
            rgb = np.power(np.dstack((r,g,b)),1.0/args.gamma)
        else:
            rgb = np.dstack((r,g,b))
        if args.remove_nan:
            rgb[~cnd,:] = 1.0
        fig.clear()
        if rr_ny > rr_nx:
            wx = rr_nx/rr_ny*0.95
            ax1 = fig.add_axes((0.5-0.5*wx,0,wx,0.95))
        else:
            wy = rr_ny/rr_nx
            ax1 = fig.add_axes((0,0.5-0.5*wy,1,wy))
        ax1.set_xticks([])
        ax1.set_yticks([])
        ax1.imshow(rgb,extent=(rr_xmin,rr_xmax,rr_ymin,rr_ymax),interpolation='none')
        ax1.plot(xctr_point,yctr_point,'o',mfc='none',mec='k')
        ax1.plot(xf_point,yf_point,'k:')
        for ntmp,xtmp,ytmp in zip(ng,xctr_point,yctr_point):
            if np.isnan(xtmp) or np.isnan(ytmp):
                continue
            ax1.text(xtmp,ytmp,'{}'.format(ntmp))
        ax1.set_xlim(fig_xmin,fig_xmax)
        ax1.set_ylim(fig_ymin,fig_ymax)
        if args.ax1_title is not None:
            ax1.set_title('{} (Plot{})'.format(args.ax1_title,plot))
        plt.savefig(pdf,format='pdf')
        if not args.batch:
            plt.draw()
            plt.pause(0.1)
    #if plot == 2:
    #    break
if args.debug:
    pdf.close()
tmp_fp.seek(0)
line = tmp_fp.read()
with open(args.out_fnam,'w') as fp:
    fp.write(line)
tmp_fp.close()
if (len(err_list) > 0) and (not args.ignore_error):
    raise ValueError('Error, check the number of plot {}'.format(','.join([str(plot) for plot in err_list])))
