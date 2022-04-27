#!/usr/bin/env python
import os
import gdal
import numpy as np
from scipy.signal import convolve2d

filt1 = np.ones((35,35))
norm = filt1.sum()
filt1 *= 1.0/norm

filt2 = np.ones((29,29))
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
