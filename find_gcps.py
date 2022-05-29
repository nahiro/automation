#!/usr/bin/env python
import os
import sys
import re
try:
    import gdal
except Exception:
    from osgeo import gdal
try:
    import osr
except Exception:
    from osgeo import osr
import numpy as np
from scipy.interpolate import RegularGridInterpolator
from scipy.optimize import leastsq
from scipy.ndimage import gaussian_filter
from optparse import OptionParser,IndentedHelpFormatter

# Default values
REF_BAND = 4 # WorldView Red
TRG_BAND = 3 # Sentinel-2 Red
SUBSET_WIDTH = 100 # pixel
SUBSET_HEIGHT = 100 # pixel
X0 = 0.0 # m
Y0 = 0.0 # m
SHIFT_WIDTH = 3 # pixel
SHIFT_HEIGHT = 3 # pixel
MARGIN_WIDTH = 5 # pixel
MARGIN_HEIGHT = 5 # pixel
SCAN_STEP = 1 # pixel
INTERP = 'linear'
RTHR = 0.3
RMAX = 10.0
FEPS = 0.01
REF_MASK_FNAM = 'ref_mask.tif'

# Read options
parser = OptionParser(formatter=IndentedHelpFormatter(max_help_position=200,width=200))
parser.set_usage('Usage: %prog target_georeferenced_image reference_georeferenced_image [options]')
parser.add_option('-o','--out_fnam',default=None,help='Output file name (%default)')
parser.add_option('-b','--ref_band',default=REF_BAND,type='int',help='Reference band# (%default)')
parser.add_option('-B','--trg_band',default=TRG_BAND,type='int',help='Target band# (%default)')
parser.add_option('--ref_multi_band',default=None,type='int',action='append',help='Reference multi-band number (%default)')
parser.add_option('--ref_multi_ratio',default=None,type='float',action='append',help='Reference multi-band ratio (%default)')
parser.add_option('--trg_multi_band',default=None,type='int',action='append',help='Target multi-band number (%default)')
parser.add_option('--trg_multi_ratio',default=None,type='float',action='append',help='Target multi-band ratio (%default)')
parser.add_option('-x','--trg_indx_start',default=None,type='int',help='Target start x index (0)')
parser.add_option('-X','--trg_indx_stop',default=None,type='int',help='Target stop x index (target width)')
parser.add_option('-s','--trg_indx_step',default=None,type='int',help='Target step x index (half of subset_width)')
parser.add_option('-y','--trg_indy_start',default=None,type='int',help='Target start y index (0)')
parser.add_option('-Y','--trg_indy_stop',default=None,type='int',help='Target stop y index (target height)')
parser.add_option('-S','--trg_indy_step',default=None,type='int',help='Target step y index (half of subset_height)')
parser.add_option('-W','--subset_width',default=SUBSET_WIDTH,type='int',help='Subset width in target pixel (%default)')
parser.add_option('-H','--subset_height',default=SUBSET_HEIGHT,type='int',help='Subset height in target pixel (%default)')
parser.add_option('--x0',default=X0,type='float',help='Initial x shift in m (%default)')
parser.add_option('--y0',default=Y0,type='float',help='Initial y shift in m (%default)')
parser.add_option('--shift_width',default=SHIFT_WIDTH,type='int',help='Max shift width in target pixel (%default)')
parser.add_option('--shift_height',default=SHIFT_HEIGHT,type='int',help='Max shift height in target pixel (%default)')
parser.add_option('--margin_width',default=MARGIN_WIDTH,type='int',help='Margin width in target pixel (%default)')
parser.add_option('--margin_height',default=MARGIN_HEIGHT,type='int',help='Margin height in target pixel (%default)')
parser.add_option('--scan_indx_step',default=SCAN_STEP,type='int',help='Scan step x index (%default)')
parser.add_option('--scan_indy_step',default=SCAN_STEP,type='int',help='Scan step y index (%default)')
parser.add_option('--ref_data_min',default=None,type='float',help='Minimum reference data value (%default)')
parser.add_option('--ref_data_max',default=None,type='float',help='Maximum reference data value (%default)')
parser.add_option('--trg_data_min',default=None,type='float',help='Minimum target data value (%default)')
parser.add_option('--trg_data_max',default=None,type='float',help='Maximum target data value (%default)')
parser.add_option('--ref_data_umax',default=None,type='float',help='Maximum reference data value to use (%default)')
parser.add_option('--ref_data_umin',default=None,type='float',help='Minimum reference data value to use (%default)')
parser.add_option('--trg_blur_sigma',default=None,type='int',help='Target blur radius in pixel (%default)')
parser.add_option('-I','--interp',default=INTERP,help='Interpolation method (%default)')
parser.add_option('-r','--rthr',default=RTHR,type='float',help='Threshold of correlation coefficient (%default)')
parser.add_option('-E','--feps',default=FEPS,type='float',help='Step length for curve_fit (%default)')
parser.add_option('--img_fnam',default=None,help='Image file name (%default)')
parser.add_option('--scan_fnam',default=None,help='Scan file name (%default)')
parser.add_option('--ref_mask_fnam',default=REF_MASK_FNAM,help='Reference mask file name (%default)')
parser.add_option('--trg_ndvi',default=False,action='store_true',help='Target is NDVI with R=trg_multi_band[0] and NIR=trg_multi_band[1] (%default)')
parser.add_option('-e','--exp',default=False,action='store_true',help='Output in exp format (%default)')
parser.add_option('--long',default=False,action='store_true',help='Output in long format (%default)')
parser.add_option('-u','--use_edge',default=False,action='store_true',help='Use GCPs near the edge of the correction range (%default)')
parser.add_option('-v','--verbose',default=False,action='store_true',help='Verbose mode (%default)')
parser.add_option('-d','--debug',default=False,action='store_true',help='Debug mode (%default)')
(opts,args) = parser.parse_args()
if len(args) < 2:
    parser.print_help()
    sys.exit(0)
trg_fnam = args[0]
ref_fnam = args[1]

def gaussian_filter_nan(arr,sigma):
    # Reference: https://stackoverflow.com/questions/18697532/gaussian-filtering-a-image-with-nan-in-python
    nan_msk = np.isnan(arr)
    loss = np.zeros(arr.shape)
    loss[nan_msk] = 1
    loss = gaussian_filter(loss,sigma=sigma,mode='constant',cval=1)
    gauss = arr.copy()
    gauss[nan_msk] = 0
    gauss = gaussian_filter(gauss,sigma=sigma,mode='constant',cval=0)
    gauss[nan_msk] = np.nan
    gauss += loss*arr
    return gauss

def interp_img(p,refx,refy,refz,refm,trgx,trgy,trgz):
    if opts.trg_blur_sigma is not None:
        f = RegularGridInterpolator((trgx+p[0],trgy[::-1]+p[1]),gaussian_filter_nan(trgz,sigma=opts.trg_blur_sigma)[::-1].T,method=opts.interp)
    else:
        f = RegularGridInterpolator((trgx+p[0],trgy[::-1]+p[1]),trgz[::-1].T,method=opts.interp)
    xg,yg = np.meshgrid(refx,refy)
    intz = f(np.array((xg,yg)).T).T
    return refz,refm,intz

def residuals(p,refx,refy,refz,refm,trgx,trgy,trgz,pmax,check=False):
    if opts.debug:
        sys.stderr.write('{}\n'.format(p))
    if np.any(np.isnan(p)):
        return np.full(3,RMAX) # length = len(p)+1
    else:
        pdif = np.abs([p[0]-opts.x0,p[1]-opts.y0])-pmax
        cnd = (pdif > 0.0)
        if np.any(cnd):
            return np.full(3,RMAX+pdif[cnd].sum()) # length = len(p)+1
    if opts.trg_blur_sigma is not None:
        f = RegularGridInterpolator((trgx+p[0],trgy[::-1]+p[1]),gaussian_filter_nan(trgz,sigma=opts.trg_blur_sigma)[::-1].T,method=opts.interp)
    else:
        f = RegularGridInterpolator((trgx+p[0],trgy[::-1]+p[1]),trgz[::-1].T,method=opts.interp)
    xg,yg = np.meshgrid(refx,refy)
    intz = f(np.array((xg,yg)).T).T
    cnd = (~np.isnan(intz))
    if cnd.sum() < cnd.size*0.3:
        return np.full(3,RMAX) # length = len(p)+1
    cnd = (~np.isnan(refz)) & (~np.isnan(intz)) & (~np.isnan(refm)) & (refm > 0.5) # inside
    if cnd.sum() < cnd.size*0.1:
        return np.full(3,RMAX) # length = len(p)+1
    zi = intz[cnd]
    ni = int(zi.size*0.9)
    #ni = int(zi.size)
    vi = zi[np.argsort(zi)[:ni]]
    cnd = (~np.isnan(refz)) & (~np.isnan(intz)) & (~np.isnan(refm)) & (refm < 0.5) # boundary
    if cnd.sum() < cnd.size*0.01:
        return np.full(3,RMAX) # length = len(p)+1
    zb = intz[cnd]
    nb = int(zb.size*0.9)
    #nb = int(zb.size)
    vb = zb[np.argsort(zb)[:nb]]
    vi_avg = vi.mean()
    vi_std = vi.std()
    if check:
        vb_avg = vb.mean()
        r = np.sqrt(np.square(vb-vi_avg).sum()/nb)/vi_std
        return r,vi_avg,vi_std,vb_avg,ni,nb
    else:
        r = np.sqrt(np.square(vb-vi_avg).sum()/nb)/vi_std
        return np.full(3,RMAX-r) # length = len(p)+1

ds = gdal.Open(ref_fnam)
prj = ds.GetProjection()
srs = osr.SpatialReference(wkt=prj)
if opts.ref_multi_band is not None:
    if len(opts.ref_multi_band) != len(opts.ref_multi_ratio):
        raise ValueError('Error, len(opts.ref_multi_band)={}, len(opts.ref_multi_ratio)={}'.format(len(opts.ref_multi_band),len(opts.ref_multi_ratio)))
    ref_data = 0.0
    for band,ratio in zip(opts.ref_multi_band,opts.ref_multi_ratio):
        ref_data += ds.GetRasterBand(band+1).ReadAsArray().astype(np.float64)*ratio
elif opts.ref_band < 0:
    ref_data = ds.ReadAsArray().astype(np.float64)
else:
    ref_data = ds.GetRasterBand(opts.ref_band+1).ReadAsArray().astype(np.float64)
trans = ds.GetGeoTransform()
ref_shape = ref_data.shape
indy,indx = np.indices(ref_shape)
ref_xp = trans[0]+(indx+0.5)*trans[1]+(indy+0.5)*trans[2]
ref_yp = trans[3]+(indx+0.5)*trans[4]+(indy+0.5)*trans[5]
ref_epsg = srs.GetAttrValue('AUTHORITY',1)
ds = None # close dataset
ref_xp0 = ref_xp[0,:]
ref_yp0 = ref_yp[:,0]
ref_xp_min = ref_xp0.min()
ref_xp_max = ref_xp0.max()
ref_yp_min = ref_yp0.min()
ref_yp_max = ref_yp0.max()
ref_xp_stp = ref_xp0[1]-ref_xp0[0]
ref_yp_stp = ref_yp0[1]-ref_yp0[0]
if ref_xp_stp <= 0.0:
    raise ValueError('Error, ref_xp_stp={}'.format(ref_xp_stp))
if ref_yp_stp >= 0.0:
    raise ValueError('Error, ref_yp_stp={}'.format(ref_yp_stp))

if opts.ref_data_min is not None:
    ref_data[ref_data < opts.ref_data_min] = np.nan
if opts.ref_data_max is not None:
    ref_data[ref_data > opts.ref_data_max] = np.nan

if opts.ref_mask_fnam is not None:
    ds = gdal.Open(opts.ref_mask_fnam)
    ref_mask = ds.ReadAsArray()
    ref_mask_trans = ds.GetGeoTransform()
    ref_mask_shape = ref_mask.shape
    ds = None # close dataset
    if ref_mask_shape != ref_shape:
        raise ValueError('Error, ref_mask_shape={}, ref_shape={}'.format(ref_mask_shape,ref_shape))

ds = gdal.Open(trg_fnam)
prj = ds.GetProjection()
srs = osr.SpatialReference(wkt=prj)
if opts.trg_multi_band is not None:
    if opts.trg_ndvi:
        if len(opts.trg_multi_band) != 2:
            raise ValueError('Error, len(opts.trg_multi_band)={}'.format(len(opts.trg_multi_band)))
        red = ds.GetRasterBand(opts.trg_multi_band[0]+1).ReadAsArray().astype(np.float64)
        nir = ds.GetRasterBand(opts.trg_multi_band[1]+1).ReadAsArray().astype(np.float64)
        trg_data = (nir-red)/(nir+red)
        if opts.trg_data_min is not None:
            cnd = (red < opts.trg_data_min)
            trg_data[cnd] = red[cnd]
            cnd = (nir < opts.trg_data_min)
            trg_data[cnd] = nir[cnd]
        if opts.trg_data_max is not None:
            cnd = (red > opts.trg_data_max)
            trg_data[cnd] = red[cnd]
            cnd = (nir > opts.trg_data_max)
            trg_data[cnd] = nir[cnd]
    else:
        if len(opts.trg_multi_band) != len(opts.trg_multi_ratio):
            raise ValueError('Error, len(opts.trg_multi_band)={}, len(opts.trg_multi_ratio)={}'.format(len(opts.trg_multi_band),len(opts.trg_multi_ratio)))
        trg_data = 0.0
        for band,ratio in zip(opts.trg_multi_band,opts.trg_multi_ratio):
            trg_data += ds.GetRasterBand(band+1).ReadAsArray().astype(np.float64)*ratio
elif opts.trg_band < 0:
    trg_data = ds.ReadAsArray().astype(np.float64)
else:
    trg_data = ds.GetRasterBand(opts.trg_band+1).ReadAsArray().astype(np.float64)
trans = ds.GetGeoTransform()
trg_shape = trg_data.shape
indy,indx = np.indices(trg_shape)
trg_xp = trans[0]+(indx+0.5)*trans[1]+(indy+0.5)*trans[2]
trg_yp = trans[3]+(indx+0.5)*trans[4]+(indy+0.5)*trans[5]
trg_epsg = srs.GetAttrValue('AUTHORITY',1)
if trg_epsg != ref_epsg:
    sys.stderr.write('Warning, different EPSG, ref:{}, trg:{}\n'.format(ref_epsg,trg_epsg))
ds = None # close dataset
trg_xp0 = trg_xp[0,:]
trg_yp0 = trg_yp[:,0]
trg_xp_min = trg_xp0.min()
trg_xp_max = trg_xp0.max()
trg_yp_min = trg_yp0.min()
trg_yp_max = trg_yp0.max()
trg_xp_stp = trg_xp0[1]-trg_xp0[0]
trg_yp_stp = trg_yp0[1]-trg_yp0[0]
if trg_xp_stp <= 0.0:
    raise ValueError('Error, trg_xp_stp={}'.format(trg_xp_stp))
if trg_yp_stp >= 0.0:
    raise ValueError('Error, trg_yp_stp={}'.format(trg_yp_stp))

if opts.trg_data_min is not None:
    trg_data[trg_data < opts.trg_data_min] = np.nan
if opts.trg_data_max is not None:
    trg_data[trg_data > opts.trg_data_max] = np.nan

ref_height,ref_width = ref_shape
trg_height,trg_width = trg_shape
subset_half_width = opts.subset_width//2
subset_half_height = opts.subset_height//2
if opts.trg_indx_start is None:
    opts.trg_indx_start = 0
if opts.trg_indx_stop is None:
    opts.trg_indx_stop = trg_width
if opts.trg_indx_step is None:
    opts.trg_indx_step = subset_half_width
if opts.trg_indy_start is None:
    opts.trg_indy_start = 0
if opts.trg_indy_stop is None:
    opts.trg_indy_stop = trg_height
if opts.trg_indy_step is None:
    opts.trg_indy_step = subset_half_height

if opts.out_fnam is not None:
    if os.path.exists(opts.out_fnam):
        os.remove(opts.out_fnam)
for trg_indyc in np.arange(opts.trg_indy_start,opts.trg_indy_stop,opts.trg_indy_step):
    trg_indy1 = trg_indyc-subset_half_height-opts.margin_height
    trg_indy2 = trg_indyc+subset_half_height+opts.margin_height+1
    if trg_indy1 < 0:
        continue
    if trg_indy2 > trg_height:
        break
    ref_yp1 = trg_yp0[trg_indyc-subset_half_height] # yp1 > ypc
    ref_yp2 = trg_yp0[trg_indyc+subset_half_height] # yp2 < ypc
    if ref_yp1 > ref_yp_max:
        continue
    if ref_yp2 < ref_yp_min:
        continue
    ref_indy1 = np.where(ref_yp0 <= ref_yp1)[0]
    if ref_indy1.size < 1:
        continue
    ref_indy1 = ref_indy1[0]
    ref_indy2 = np.where(ref_yp0 >= ref_yp2)[0]
    if ref_indy2.size < 1:
        continue
    ref_indy2 = ref_indy2[-1]+1
    for trg_indxc in np.arange(opts.trg_indx_start,opts.trg_indx_stop,opts.trg_indx_step):
        trg_indx1 = trg_indxc-subset_half_width-opts.margin_width
        trg_indx2 = trg_indxc+subset_half_width+opts.margin_width+1
        if trg_indx1 < 0:
            continue
        if trg_indx2 > trg_width:
            break
        ref_xp1 = trg_xp0[trg_indxc-subset_half_width]
        ref_xp2 = trg_xp0[trg_indxc+subset_half_width]
        if ref_xp1 < ref_xp_min:
            continue
        if ref_xp2 > ref_xp_max:
            continue
        ref_indx1 = np.where(ref_xp0 >= ref_xp1)[0]
        if ref_indx1.size < 1:
            continue
        ref_indx1 = ref_indx1[0]
        ref_indx2 = np.where(ref_xp0 <= ref_xp2)[0]
        if ref_indx2.size < 1:
            continue
        ref_indx2 = ref_indx2[-1]+1
        # target subset
        trg_subset_xp0 = trg_xp0[trg_indx1:trg_indx2]
        trg_subset_yp0 = trg_yp0[trg_indy1:trg_indy2]
        trg_subset_data = trg_data[trg_indy1:trg_indy2,trg_indx1:trg_indx2].copy()
        #if opts.trg_data_min is not None and trg_subset_data.min() < opts.trg_data_min:
        #    continue
        #if opts.trg_data_max is not None and trg_subset_data.max() > opts.trg_data_max:
        #    continue
        # reference subset
        ref_subset_xp0 = ref_xp0[ref_indx1:ref_indx2]
        ref_subset_yp0 = ref_yp0[ref_indy1:ref_indy2]
        ref_subset_data = ref_data[ref_indy1:ref_indy2,ref_indx1:ref_indx2].copy()
        ref_subset_mask = ref_mask[ref_indy1:ref_indy2,ref_indx1:ref_indx2].copy()
        if opts.ref_data_min is not None and np.nanmin(ref_subset_data) < opts.ref_data_min:
            continue
        if opts.ref_data_max is not None and np.nanmax(ref_subset_data) > opts.ref_data_max:
            continue

        if opts.ref_data_umax is not None:
            cnd1 = (~np.isnan(ref_subset_data)) & (ref_subset_data > opts.ref_data_umax)
            if cnd1.sum() > 0:
                cnd2 = np.full(ref_subset_data.shape,False)
                indy,indx = np.indices(ref_subset_data.shape)
                for indy_tmp,indx_tmp in zip(indy[cnd1],indx[cnd1]):
                    cnd2[indy_tmp-5:indy_tmp+6,indx_tmp-5:indx_tmp+6] = True
                ref_subset_data[cnd2] = np.nan
        if opts.ref_data_umin is not None:
            cnd1 = (~np.isnan(ref_subset_data)) & (ref_subset_data < opts.ref_data_umin)
            if cnd1.sum() > 0:
                cnd2 = np.full(ref_subset_data.shape,False)
                indy,indx = np.indices(ref_subset_data.shape)
                for indy_tmp,indx_tmp in zip(indy[cnd1],indx[cnd1]):
                    cnd2[indy_tmp-5:indy_tmp+6,indx_tmp-5:indx_tmp+6] = True
                ref_subset_data[cnd2] = np.nan

        if opts.scan_fnam is not None:
            scan_fnam = opts.scan_fnam.replace('.dat','_{:05d}_{:05d}.dat'.format(trg_indxc,trg_indyc))
            if os.path.exists(scan_fnam):
                os.remove(scan_fnam)
        trg_pmax = np.array([np.abs(trg_xp_stp*(opts.shift_width+0.5)),np.abs(trg_yp_stp*(opts.shift_height+0.5))])
        scan_indx = np.arange(-opts.shift_width,opts.shift_width+1,opts.scan_indx_step)
        scan_indy = np.arange(-opts.shift_height,opts.shift_height+1,opts.scan_indy_step)
        scan_xp = []
        scan_yp = []
        scan_r = []
        p1 = np.array([opts.x0,opts.y0])
        rmax = -1.0e10
        for i in scan_indy:
            dy = opts.y0+np.abs(trg_yp_stp)*i
            for j in scan_indx:
                dx = opts.x0+np.abs(trg_xp_stp)*j
                p2 = np.array([dx,dy])
                r = RMAX-residuals(p2,ref_subset_xp0,ref_subset_yp0,ref_subset_data,ref_subset_mask,
                                  trg_subset_xp0,trg_subset_yp0,trg_subset_data,trg_pmax)[0]
                scan_xp.append(dx)
                scan_yp.append(dy)
                scan_r.append(r)
                if opts.scan_fnam is not None:
                    with open(scan_fnam,'a') as fp:
                        fp.write('{:5d} {:5d} {:13.6e}\n'.format(j,i,r))
                if r > rmax:
                    rmax = r
                    p1 = p2.copy()
        scan_xp = np.array(scan_xp).reshape(scan_indy.size,scan_indx.size)
        scan_yp = np.array(scan_yp).reshape(scan_indy.size,scan_indx.size)
        scan_r = np.array(scan_r).reshape(scan_indy.size,scan_indx.size)
        result = leastsq(residuals,p1,args=(ref_subset_xp0,ref_subset_yp0,ref_subset_data,ref_subset_mask,
                                            trg_subset_xp0,trg_subset_yp0,trg_subset_data,trg_pmax),
                                            epsfcn=opts.feps,full_output=True)
        p2 = result[0]
        if not opts.use_edge:
            if np.abs(p2[0]-opts.x0) >= np.abs(trg_xp_stp*(opts.shift_width-0.5)):
                continue
            if np.abs(p2[1]-opts.y0) >= np.abs(trg_yp_stp*(opts.shift_height-0.5)):
                continue
        r = RMAX-result[2]['fvec'][0]
        if r > opts.rthr:
            r_check,vi_avg,vi_std,vb_avg,ni,nb = residuals(p2,ref_subset_xp0,ref_subset_yp0,ref_subset_data,ref_subset_mask,
                                                              trg_subset_xp0,trg_subset_yp0,trg_subset_data,trg_pmax,check=True)
            if not np.allclose([r],[r_check]):
                raise ValueError('Error, r={}, r_check={}'.format(r,r_check))
            cnd = (scan_r > r*0.90)
            xcnd = scan_xp[cnd]-p2[0]
            ycnd = scan_yp[cnd]-p2[1]
            if xcnd.size < 1:
                r90 = 0.0
            else:
                r90 = np.sqrt((np.square(xcnd)+np.square(ycnd)).mean())
            if opts.exp:
                line = '{:8.1f} {:8.1f} {:15.8e} {:15.8e} {:15.8e} {:15.8e} {:8.3f} {:15.8e} {:15.8e} {:6d} {:15.8e} {:6d} {:8.3f}\n'.format(trg_indxc+0.5,trg_indyc+0.5,trg_xp0[trg_indxc]+p2[0],trg_yp0[trg_indyc]+p2[1],p2[0],p2[1],r,vi_avg,vi_std,ni,vb_avg,nb,r90)
            elif opts.long:
                line = '{:8.1f} {:8.1f} {:12.6f} {:12.6f} {:10.6f} {:10.6f} {:10.5f} {:13.6f} {:13.6f} {:6d} {:13.6f} {:6d} {:10.5f}\n'.format(trg_indxc+0.5,trg_indyc+0.5,trg_xp0[trg_indxc]+p2[0],trg_yp0[trg_indyc]+p2[1],p2[0],p2[1],r,vi_avg,vi_std,ni,vb_avg,nb,r90)
            else:
                line = '{:8.1f} {:8.1f} {:8.2f} {:8.2f} {:6.2f} {:6.2f} {:8.3f} {:11.4f} {:11.4f} {:6d} {:11.4f} {:6d} {:8.3f}\n'.format(trg_indxc+0.5,trg_indyc+0.5,trg_xp0[trg_indxc]+p2[0],trg_yp0[trg_indyc]+p2[1],p2[0],p2[1],r,vi_avg,vi_std,ni,vb_avg,nb,r90)
            if opts.out_fnam is not None:
                with open(opts.out_fnam,'a') as fp:
                    fp.write(line)
            else:
                sys.stdout.write(line)
            if opts.verbose:
                sys.stderr.write(line)
            if opts.img_fnam is not None:
                img_fnam = opts.img_fnam.replace('.npz','_{:05d}_{:05d}.npz'.format(trg_indxc,trg_indyc))
                ref_img,msk_img,trg_img = interp_img(p2,ref_subset_xp0,ref_subset_yp0,ref_subset_data,ref_subset_mask,trg_subset_xp0,trg_subset_yp0,trg_subset_data)
                np.savez(img_fnam,ref_img=ref_img,msk_img=msk_img,trg_img=trg_img,xp0=ref_subset_xp0,yp0=ref_subset_yp0)
