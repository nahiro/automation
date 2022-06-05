import os
import re
import zlib # to prevent segmentation fault when saving pdf
try:
    import gdal
except Exception:
    from osgeo import gdal
from glob import glob
import numpy as np
import cartopy.crs as ccrs
import cartopy.io.shapereader as shpreader
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib.backends.backend_pdf import PdfPages
from argparse import ArgumentParser,RawTextHelpFormatter

# Constants
ORDER_DICT = {0:'0th',1:'1st',2:'2nd',3:'3rd'}

# Default values
ORDER = [0,1,2,3]
FIGNAM = 'geocor_resized.pdf'

# Read options
parser = ArgumentParser(formatter_class=lambda prog:RawTextHelpFormatter(prog,max_help_position=200,width=200))
parser.add_argument('-f','--img_fnam',default=None,action='append',help='Image file name (%(default)s)')
parser.add_argument('-t','--title',default=None,action='append',help='Figure title (%(default)s)')
parser.add_argument('-o','--order',default=None,type=int,action='append',help='Geocor order ({})'.format(ORDER))
parser.add_argument('-s','--shp_fnam',default=None,help='Shape file name (%(default)s)')
parser.add_argument('-F','--fignam',default=FIGNAM,help='Output figure name (%(default)s)')
parser.add_argument('-b','--batch',default=False,action='store_true',help='Batch mode (%(default)s)')
args = parser.parse_args()
if args.order is None:
    args.order = ORDER

block_shp = list(shpreader.Reader(args.shp_fnam).geometries())

prj = ccrs.UTM(zone=48,southern_hemisphere=True)

if not args.batch:
    plt.interactive(True)
fig = plt.figure(1,facecolor='w',figsize=(6,6))
plt.subplots_adjust(top=0.85,bottom=0.002,left=0.002,right=0.998,wspace=0.01)
pdf = PdfPages(args.fignam)

for itarg in range(len(args.img_fnam)):
    fig_xmin = None
    fig_xmax = None
    fig_ymin = None
    fig_ymax = None
    for order in args.order:
        ds = gdal.Open('{}_np{}.tif'.format(os.path.splitext(args.img_fnam[itarg])[0],order))
        data = ds.ReadAsArray()
        data_trans = ds.GetGeoTransform()
        data_shape = (ds.RasterYSize,ds.RasterXSize)
        ds = None
        data_xmin = data_trans[0]
        data_xstp = data_trans[1]
        data_xmax = data_xmin+data_xstp*data_shape[1]
        data_ymax = data_trans[3]
        data_ystp = data_trans[5]
        data_ymin = data_ymax+data_ystp*data_shape[0]
        indy,indx = np.indices(data_shape)
        cnd = data[0] > -10000
        if fig_xmin is None:
            xp = data_trans[0]+(indx+0.5)*data_trans[1]+(indy+0.5)*data_trans[2]
            yp = data_trans[3]+(indx+0.5)*data_trans[4]+(indy+0.5)*data_trans[5]
            fig_xmin = xp[cnd].min()
            fig_xmax = xp[cnd].max()
            fig_ymin = yp[cnd].min()
            fig_ymax = yp[cnd].max()
        ind_xmin = indx[cnd].min()
        ind_xmax = indx[cnd].max()+1
        ind_ymin = indy[cnd].min()
        ind_ymax = indy[cnd].max()+1
        b = data[0].astype(np.float32)
        g = data[1].astype(np.float32)
        r = data[2].astype(np.float32)
        fact = 10.0
        b = (b*fact/32768.0).clip(0,1)
        g = (g*fact/32768.0).clip(0,1)
        r = (r*fact/32768.0).clip(0,1)
        rgb = np.power(np.dstack((r,g,b)),1.0/2.2)
        rgb_shape = data[0,ind_ymin:ind_ymax,ind_xmin:ind_xmax].shape
        cnd = ((np.isnan(rgb) | (rgb < 1.0e-6)).sum(axis=2) > 0)
        rgb[cnd,:] = 1.0
        ny,nx = rgb_shape
        fig.clear()
        axs = plt.subplot(111,projection=prj)
        axs.set_xticks([])
        axs.set_yticks([])
        axs.imshow(rgb,extent=(data_xmin,data_xmax,data_ymin,data_ymax),origin='upper',interpolation='none')
        #axs.add_geometries(block_shp,prj,edgecolor='k',facecolor='none')
        rgb_xmin = xp[ind_ymin:ind_ymax,ind_xmin:ind_xmax].min()
        rgb_ymax = yp[ind_ymin:ind_ymax,ind_xmin:ind_xmax].max()
        for shp in block_shp:
            xc = shp.centroid.x
            yc = shp.centroid.y
            ix = int((xc-rgb_xmin)/np.abs(data_xstp))
            iy = int((rgb_ymax-yc)/np.abs(data_ystp))
            #if ix > 0 and ix < nx and iy > 0 and iy < ny and not cnd[iy,ix]:
            if (xc > fig_xmin-50.0) and (xc < fig_xmax+50.0) and (yc > fig_ymin-50.0) and (yc < fig_ymax+50.0):
                axs.add_geometries([shp],prj,edgecolor='k',facecolor='none',linestyle='-',alpha=1.0,linewidth=0.02)
        axs.set_xlim(fig_xmin,fig_xmax)
        axs.set_ylim(fig_ymin,fig_ymax)
        axs.set_title('{} ({})'.format(args.title[itarg],ORDER_DICT[order]))
        plt.savefig(pdf,format='pdf')
        if not args.batch:
            plt.draw()
            plt.pause(0.1)
        #break
    #break

pdf.close()
