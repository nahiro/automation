#!/usr/bin/env python
import os
import sys
import re
from datetime import datetime
try:
    import gdal
except Exception:
    from osgeo import gdal
from glob import glob
import numpy as np
from subprocess import call
from proc_class import Process

class Geocor(Process):

    def calc_mean(x,y,emax=2.0,nrpt=10,nmin=1,selected=None):
        if selected is not None:
            indx = selected.copy()
        else:
            indx = np.where(np.isfinite(x+y))[0]
        for n in range(nrpt):
            x_selected = x[indx]
            y_selected = y[indx]
            i_selected = indx.copy()
            x_center = x_selected.mean()
            y_center = y_selected.mean()
            r_selected = np.sqrt(np.square(x_selected-x_center)+np.square(y_selected-y_center))
            rmse = np.sqrt(np.mean(np.square(x_selected-x_center)+np.square(y_selected-y_center)))
            cnd = (r_selected < rmse*emax)
            indx = indx[cnd]
            if (indx.size == x_selected.size) or (indx.size < nmin):
                break
        return x_center,y_center,rmse,x_selected.size,i_selected

    def run(self):
        # Start process
        super().run()

        # Check files
        if not os.path.exists(self.values['gis_fnam']):
            raise IOError('{}: error, no such file >>> {}'.format(self.proc_name,self.values['gis_fnam']))
        if not os.path.exists(self.values['ref_fnam']):
            raise IOError('{}: error, no such file >>> {}'.format(self.proc_name,self.values['ref_fnam']))
        if not os.path.exists(self.values['trg_fnam']):
            raise IOError('{}: error, no such file >>> {}'.format(self.proc_name,self.values['trg_fnam']))
        ref_bnam,ref_enam = os.path.splitext(os.path.basename(self.values['ref_fnam']))
        trg_bnam,trg_enam = os.path.splitext(os.path.basename(self.values['trg_fnam']))
        wrk_dir = os.path.join(self.drone_analysis,self.current_block,self.current_date,'geocor')
        if not os.path.exists(wrk_dir):
            os.makedirs(wrk_dir)
        if not os.path.isdir(wrk_dir):
            raise ValueError('{}: error, no such folder >>> {}'.format(self.proc_name,wrk_dir))

        # Rebin target
        ds = gdal.Open(self.values['trg_fnam'])
        trg_trans = ds.GetGeoTransform()
        trg_shape = (ds.RasterYSize,ds.RasterXSize)
        ds = None
        trg_xmin = trg_trans[0]
        trg_xstp = trg_trans[1]
        trg_xmax = trg_xmin+trg_xstp*trg_shape[1]
        trg_ymax = trg_trans[3]
        trg_ystp = trg_trans[5]
        trg_ymin = trg_ymax+trg_ystp*trg_shape[0]
        istp = int(abs(self.values['trg_binning']/trg_xstp)+0.5)
        jstp = int(abs(self.values['trg_binning']/trg_ystp)+0.5)
        if istp != jstp:
            raise ValueError('{}: error, istp={}, jstp={}'.format(self.proc_name,istp,jstp))
        command = self.python_path
        command += ' {}'.format(os.path.join(self.scr_dir,'rebin_gtiff.py'))
        command += ' --istp {}'.format(istp)
        command += ' --jstp {}'.format(jstp)
        command += ' --src_geotiff {}'.format(self.values['trg_fnam'])
        command += ' --dst_geotiff {}_resized.tif'.format(os.path.join(wrk_dir,trg_bnam))
        sys.stderr.write('Rebin target\n')
        sys.stderr.write(command+'\n')
        sys.stderr.flush()
        #call(command,shell=True)

        # Crop reference
        ds = gdal.Open(self.values['ref_fnam'])
        ref_trans = ds.GetGeoTransform()
        ref_shape = (ds.RasterYSize,ds.RasterXSize)
        ds = None
        ref_xmin = ref_trans[0]
        ref_xstp = ref_trans[1]
        ref_xmax = ref_xmin+ref_xstp*ref_shape[1]
        ref_ymax = ref_trans[3]
        ref_ystp = ref_trans[5]
        ref_ymin = ref_ymax+ref_ystp*ref_shape[0]
        xmgn = 10.0
        ymgn = 10.0
        out_xmin = np.floor(trg_xmin-xmgn)
        out_ymin = np.floor(trg_ymin-ymgn)
        out_xmax = np.ceil(trg_xmax+xmgn)
        out_ymax = np.ceil(trg_ymax+ymgn)
        xoff = int((out_xmin-ref_xmin)/np.abs(ref_xstp)+0.5)
        yoff = int((ref_ymax-out_ymax)/np.abs(ref_ystp)+0.5)
        xsize = int((out_xmax-out_xmin)/np.abs(ref_xstp)+0.5)
        ysize = int((out_ymax-out_ymin)/np.abs(ref_ystp)+0.5)
        if xoff < 0 or yoff < 0 or xsize < 0 or ysize < 0:
            raise ValueError('{}: error, xoff={}, yoff={}, xsize={}, ysize={}'.format(self.proc_name,xoff,yoff,xsize,ysize))
        command = 'gdal_translate'
        command += ' -srcwin {} {} {} {}'.format(xoff,yoff,xsize,ysize)
        command += ' -tr 0.2 0.2'
        command += ' {}'.format(self.values['ref_fnam'])
        command += ' {}'.format(os.path.join(wrk_dir,'{}_{}_resized.tif'.format(ref_bnam,trg_bnam)))
        sys.stderr.write('Crop reference\n')
        sys.stderr.write(command+'\n')
        sys.stderr.flush()
        #call(command,shell=True)

        # Make dist mask
        sys.stderr.write('Make dist mask\n')
        sys.stderr.flush()
        sys.stderr.write('{}\n'.format(datetime.now()))
        # Inside
        buffer1 = -0.5*self.values['boundary_width']
        fnam1 = os.path.join(wrk_dir,'mask1.tif')
        #if os.path.exists(fnam1):
        #    os.remove(fnam1)
        command = self.python_path
        command += ' {}'.format(os.path.join(self.scr_dir,'make_mask.py'))
        command += ' --shp_fnam {}'.format(self.values['gis_fnam'])
        command += ' --src_geotiff {}'.format(os.path.join(wrk_dir,'{}_{}_resized.tif'.format(ref_bnam,trg_bnam)))
        command += ' --dst_geotiff {}'.format(fnam1)
        command += ' --buffer="{:22.15e}"'.format(buffer1)
        command += ' --use_index'
        sys.stderr.write('Inside\n')
        sys.stderr.write(command+'\n')
        sys.stderr.flush()
        #call(command,shell=True)
        ds = gdal.Open(fnam1)
        mask_nx = ds.RasterXSize
        mask_ny = ds.RasterYSize
        mask_shape = (mask_ny,mask_nx)
        mask_prj = ds.GetProjection()
        mask_trans = ds.GetGeoTransform()
        mask_meta = ds.GetMetadata()
        mask1 = ds.ReadAsArray()
        mask_nodata = -1.0
        ds = None
        sys.stderr.write('{}\n'.format(datetime.now()))
        # Outside
        buffer2 = 0.5*self.values['boundary_width']
        fnam2 = os.path.join(wrk_dir,'mask2.tif')
        #if os.path.exists(fnam2):
        #    os.remove(fnam2)
        command = self.python_path
        command += ' {}'.format(os.path.join(self.scr_dir,'make_mask.py'))
        command += ' --shp_fnam {}'.format(self.values['gis_fnam'])
        command += ' --src_geotiff {}'.format(os.path.join(wrk_dir,'{}_{}_resized.tif'.format(ref_bnam,trg_bnam)))
        command += ' --dst_geotiff {}'.format(fnam2)
        command += ' --buffer="{:22.15e}"'.format(buffer2)
        command += ' --use_index'
        sys.stderr.write('Outside\n')
        sys.stderr.write(command+'\n')
        sys.stderr.flush()
        #call(command,shell=True)
        ds = gdal.Open(fnam2)
        mask2 = ds.ReadAsArray()
        ds = None
        sys.stderr.write('{}\n'.format(datetime.now()))
        # Both side
        mask = np.full(mask_shape,fill_value=1.0,dtype=np.float32)
        cnd = (mask1 < 0.5) & (mask2 > -0.5)
        mask[cnd] = mask_nodata
        sys.stderr.write('Both side\n')
        sys.stderr.flush()
        drv = gdal.GetDriverByName('GTiff')
        ds = drv.Create(os.path.join(wrk_dir,'{}_dist_mask.tif'.format(trg_bnam)),mask_nx,mask_ny,1,gdal.GDT_Int32)
        ds.SetProjection(mask_prj)
        ds.SetGeoTransform(mask_trans)
        ds.SetMetadata(mask_meta)
        band = ds.GetRasterBand(1)
        band.WriteArray(mask)
        band.SetDescription('dist mask')
        band.SetNoDataValue(mask_nodata) # The TIFFTAG_GDAL_NODATA only support one value per dataset
        ds.FlushCache()
        ds = None # close dataset
        #if os.path.exists(fnam1):
        #    os.remove(fnam1)
        #if os.path.exists(fnam2):
        #    os.remove(fnam2)
        sys.stderr.write('{}\n'.format(datetime.now()))

        # Make area mask
        buffer3 = 0.0
        command = self.python_path
        command += ' {}'.format(os.path.join(self.scr_dir,'make_mask.py'))
        command += ' --shp_fnam {}'.format(self.values['gis_fnam'])
        command += ' --src_geotiff {}'.format(os.path.join(wrk_dir,'{}_{}_resized.tif'.format(ref_bnam,trg_bnam)))
        command += ' --dst_geotiff {}'.format(os.path.join(wrk_dir,'{}_area_mask.tif'.format(trg_bnam)))
        command += ' --buffer="{:22.15e}"'.format(buffer3)
        command += ' --use_index'
        command += ' --select_inside'
        sys.stderr.write('Make area map\n')
        sys.stderr.write(command+'\n')
        sys.stderr.flush()
        #call(command,shell=True)
        sys.stderr.write('{}\n'.format(datetime.now()))

        trials = ['1st','2nd','3rd','4th','5th']
        trg_pixel_size = abs(trg_xstp*istp)
        sizes = np.int64(np.array(self.values['part_sizes'])/trg_pixel_size+0.5) #[250,250,120,120,80]
        steps = np.int64(np.array(self.values['gcp_intervals'])/trg_pixel_size+0.5) #[125,125,60,60,40]
        shifts = np.int64(np.array(self.values['max_shifts'])/trg_pixel_size+0.5) #[40,25,12,8,8]
        margins = np.int64(np.array(self.values['margins'])/trg_pixel_size+0.5) #[60,40,18,12,12]
        print('trg_pixel_size=',trg_pixel_size)
        print('sizes=',sizes)
        print('steps=',steps)
        print('shiftss=',shifts)
        print('margins=',margins)

"""

    target = 'P4M_{}_{}'.format(field,dstr)

    shift_dat = '{}_resized_geocor_shift.dat'.format(target)
    #if os.path.exists(shift_dat):
    #    #os.remove(shift_dat)
    #    continue

    ds = gdal.Open(os.path.join(datdir,'{}_resized.tif'.format(target)))
    trg_trans = ds.GetGeoTransform()
    trg_shape = (ds.RasterYSize,ds.RasterXSize)
    ds = None
    trg_xmin = trg_trans[0]
    trg_xstp = trg_trans[1]
    trg_xmax = trg_xmin+trg_xstp*trg_shape[1]
    trg_ymax = trg_trans[3]
    trg_ystp = trg_trans[5]
    trg_ymin = trg_ymax+trg_ystp*trg_shape[0]
    ulx_resized = trg_xmin
    uly_resized = trg_ymax
    lrx_resized = trg_xmax
    lry_resized = trg_ymin

    ds = gdal.Open(os.path.join(datdir,'{}.tif'.format(target)))
    trg_trans = ds.GetGeoTransform()
    trg_shape = (ds.RasterYSize,ds.RasterXSize)
    ds = None
    trg_xmin = trg_trans[0]
    trg_xstp = trg_trans[1]
    trg_xmax = trg_xmin+trg_xstp*trg_shape[1]
    trg_ymax = trg_trans[3]
    trg_ystp = trg_trans[5]
    trg_ymin = trg_ymax+trg_ystp*trg_shape[0]
    ulx = trg_xmin
    uly = trg_ymax
    lrx = trg_xmax
    lry = trg_ymin

    for itry in range(len(trials)):
        fnam = '{}_resized_geocor_{}.dat'.format(target,trials[itry])
        if os.path.exists(fnam):
            x,y,r,ni,nb,r90 = np.loadtxt(fnam,usecols=(4,5,6,9,11,12),unpack=True)
            indx0 = np.arange(r.size)[(r>1.3) & (nb>nb.max()*0.1) & (r90<1.0)]
            x_diff1,y_diff1,e1,n1,indx1 = calc_mean(x,y,emax=3.0,selected=indx0)
            x_diff2,y_diff2,e2,n2,indx2 = calc_mean(x,y,emax=2.0,selected=indx1)
            x_diff3,y_diff3,e3,n3,indx3 = calc_mean(x,y,emax=1.5,selected=indx2)
        else:
            command = 'python'
            command += ' {}'.format(os.path.join(scrdir,'find_gcps.py'))
            if itry == 0:
                command += ' {}'.format(os.path.join(datdir,'{}_resized.tif'.format(target)))
            else:
                command += ' {}_resized_geocor_{}.tif'.format(target,trials[itry-1])
            command += ' {}'.format(os.path.join(datdir,'{}_{}_resized.tif'.format(ref_bnam,target)))
            command += ' --ref_mask_fnam {}'.format(os.path.join(datdir,'{}_{}_resized_mask.tif'.format(ref_bnam,target)))
            command += ' --out_fnam {}'.format(fnam)
            command += ' --subset_width {}'.format(sizes[itry])
            command += ' --subset_height {}'.format(sizes[itry])
            command += ' --trg_indx_step {}'.format(steps[itry])
            command += ' --trg_indy_step {}'.format(steps[itry])
            command += ' --shift_width {}'.format(shifts[itry])
            command += ' --shift_height {}'.format(shifts[itry])
            command += ' --margin_width {}'.format(margins[itry])
            command += ' --margin_height {}'.format(margins[itry])
            if itry < 2:
                command += ' --scan_indx_step 2'
                command += ' --scan_indy_step 2'
            #    command += ' --interp nearest'
            command += ' --ref_band -1'
            command += ' --trg_ndvi'
            command += ' --trg_multi_band 2'
            command += ' --trg_multi_band 4'
            #command += ' --trg_band 4' # nir
            #command += ' --trg_band 3' # red_edge
            #command += ' --trg_band 2' # red
            #command += ' --trg_band 1' # green
            #command += ' --trg_band 0' # blue
            command += ' --rthr 0.01'
            command += ' --feps 0.0001'
            #if trials[itry] == trials[-1]:
            #    command += ' --img_fnam '+os.path.join(npzdir,'{}_resized_geocor.npz'.format(target))
            #    command += ' --scan_fnam '+os.path.join(scndir,'{}_resized_geocor_scan.dat'.format(target))
            command += ' --trg_data_min -10000.0'
            command += ' --trg_data_max 32767.0'
            command += ' --ref_data_umax 320.0'
            command += ' --ref_data_umin 180.0'
            #command += ' --trg_blur_sigma 1'
            command += ' --long'
            sys.stdout.write(command+'\n')
            sys.stdout.flush()
            call(command,shell=True)

            x,y,r,ni,nb,r90 = np.loadtxt(fnam,usecols=(4,5,6,9,11,12),unpack=True)
            indx0 = np.arange(r.size)[(r>1.3) & (nb>nb.max()*0.1) & (r90<1.0)]
            x_diff1,y_diff1,e1,n1,indx1 = calc_mean(x,y,emax=3.0,selected=indx0)
            x_diff2,y_diff2,e2,n2,indx2 = calc_mean(x,y,emax=2.0,selected=indx1)
            x_diff3,y_diff3,e3,n3,indx3 = calc_mean(x,y,emax=1.5,selected=indx2)
            with open(shift_dat,'a') as fp:
                fp.write('{} {:8.4f} {:8.4f} {:7.4f} {:7.4f} {:7.4f} {:3d} {:3d} {:3d}\n'.format(trials[itry],x_diff3,y_diff3,e1,e2,e3,n1,n2,n3))
        ulx_resized += x_diff3
        uly_resized += y_diff3
        lrx_resized += x_diff3
        lry_resized += y_diff3
        ulx += x_diff3
        uly += y_diff3
        lrx += x_diff3
        lry += y_diff3

        # 0th order corrections of resized image
        command = 'gdal_translate'
        command += ' -a_ullr {:.4f} {:.4f} {:.4f} {:.4f}'.format(ulx_resized,uly_resized,lrx_resized,lry_resized) # <ulx> <uly> <lrx> <lry>
        command += ' {}'.format(os.path.join(datdir,'{}_resized.tif'.format(target)))
        command += ' {}_resized_geocor_{}.tif'.format(target,trials[itry])
        call(command,shell=True)

        if trials[itry] == trials[-1]:
            # Higher order correction of resized image
            gnam = '{}_resized_geocor.dat'.format(target)
            with open(fnam,'r') as fp:
                lines = fp.readlines()
            with open(gnam,'w') as fp:
                for i,line in enumerate(lines):
                    if i in indx2:
                        fp.write(line)
            for order in [1,2,3]:
                command = 'python'
                command += ' {}'.format(os.path.join(scrdir,'auto_geocor.py'))
                command += ' {}_resized_geocor_{}.tif'.format(target,trials[itry-1])
                command += ' --out_fnam {}_resized_geocor_np{}.tif'.format(target,order)
                command += ' --scrdir {}'.format(scrdir)
                command += ' --use_gcps {}'.format(gnam) # use
                command += ' --optfile {}_resized_geocor_gcp.dat'.format(target)
                command += ' --npoly {}'.format(order)
                command += ' --refine_gcps 0.1'
                command += ' --minimum_number 3'
                #sys.stdout.write(command+'\n')
                #sys.stdout.flush()
                call(command,shell=True)

            # 0th order corrections at full resolution
            command = 'gdal_translate'
            command += ' -a_ullr {:.4f} {:.4f} {:.4f} {:.4f}'.format(ulx,uly,lrx,lry) # <ulx> <uly> <lrx> <lry>
            command += ' {}'.format(os.path.join(datdir,'{}.tif'.format(target)))
            command += ' {}_geocor_{}.tif'.format(target,trials[itry])
            call(command,shell=True)

            # Higher order correction at full resolution
            hnam = '{}_geocor.dat'.format(target)
            command = 'python'
            command += ' {}'.format(os.path.join(scrdir,'trans_gcp.py'))
            command += ' --src_fnam {}'.format(gnam)
            command += ' --dst_fnam {}'.format(hnam)
            command += ' --src_geotiff {}'.format(os.path.join(datdir,'{}_resized.tif'.format(target)))
            command += ' --dst_geotiff {}'.format(os.path.join(datdir,'{}.tif'.format(target)))
            call(command,shell=True)
            for order in [1,2,3]:
                command = 'python'
                command += ' {}'.format(os.path.join(scrdir,'auto_geocor.py'))
                command += ' {}'.format(os.path.join(datdir,'{}.tif'.format(target)))
                command += ' --out_fnam {}_geocor_np{}.tif'.format(target,order)
                command += ' --scrdir {}'.format(scrdir)
                command += ' --use_gcps {}'.format(hnam) # use
                command += ' --optfile {}_geocor_gcp.dat'.format(target)
                command += ' --npoly {}'.format(order)
                command += ' --refine_gcps 0.1'
                command += ' --minimum_number 3'
                #sys.stdout.write(command+'\n')
                #sys.stdout.flush()
                call(command,shell=True)

    #break
"""

        # Finish process
        sys.stderr.write('Finished process {}.\n\n'.format(self.proc_name))
        sys.stderr.flush()
        return
