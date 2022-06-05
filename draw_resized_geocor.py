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

shpdir = 'All_area_polygon_20210914'
shp_fnam = 'All_area_polygon_20210914.shp'

block_shp = list(shpreader.Reader(os.path.join(shpdir,shp_fnam)).geometries())

targets = sorted(glob('P4M_*_resized_geocor_np3.tif'))
titles = []
for target in targets:
    m = re.search('(\S+)_resized_geocor_np3.tif',target)
    titles.append(m.group(1))

prj = ccrs.UTM(zone=48,southern_hemisphere=True)

#plt.interactive(True)
fig = plt.figure(1,facecolor='w',figsize=(6,6))
plt.subplots_adjust(top=0.85,bottom=0.002,left=0.002,right=0.998,wspace=0.01)
pdf = PdfPages('resized_geocor.pdf')

for itarg in range(len(targets)):
    fig_xmin = None
    fig_xmax = None
    fig_ymin = None
    fig_ymax = None
    for t in [targets[itarg].replace('np3','5th'),targets[itarg].replace('np3','np1'),targets[itarg].replace('np3','np2'),targets[itarg]]:
        ds = gdal.Open('{}'.format(t))
        data = ds.ReadAsArray()
        data_trans = ds.GetGeoTransform()
        data_shape = data[0].shape
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
        if '5th' in t:
            axs.set_title(titles[itarg].replace('P4M_','')+' (0th)',size=12)
        elif 'np2' in t:
            axs.set_title(titles[itarg].replace('P4M_','')+' (2nd)',size=12)
        elif 'np3' in t:
            axs.set_title(titles[itarg].replace('P4M_','')+' (3rd)',size=12)
        else:
            axs.set_title(titles[itarg].replace('P4M_','')+' (1st)',size=12)
        plt.savefig(pdf,format='pdf')
        #plt.draw()
        #plt.pause(0.1)
        #break
    #break

pdf.close()
