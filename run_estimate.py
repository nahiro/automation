import os
import sys
try:
    import gdal
except Exception:
    from osgeo import gdal
from proc_class import Process

class Estimate(Process):

    def __init__(self):
        super().__init__()
        self.ax1_zmin = None
        self.ax1_zmax = None
        self.ax1_zstp = None
        self._freeze()

    def run(self):
        # Start process
        super().run()

        # Check files
        if not os.path.exists(self.values['inp_fnam']):
            raise IOError('{}: error, no such file >>> {}'.format(self.proc_name,self.values['inp_fnam']))
        if not os.path.exists(self.values['pv_fnam']):
            raise IOError('{}: error, no such file >>> {}'.format(self.proc_name,self.values['pv_fnam']))
        if not os.path.exists(self.values['pm_fnam']):
            raise IOError('{}: error, no such file >>> {}'.format(self.proc_name,self.values['pm_fnam']))
        trg_bnam = '{}_{}'.format(self.obs_block,self.obs_date)
        wrk_dir = os.path.join(self.drone_analysis,self.obs_block,self.obs_date,self.proc_name)
        if not os.path.exists(wrk_dir):
            os.makedirs(wrk_dir)
        if not os.path.isdir(wrk_dir):
            raise ValueError('{}: error, no such folder >>> {}'.format(self.proc_name,wrk_dir))

        # Make mask
        mask_fnam = os.path.join(wrk_dir,'{}_mask.tif'.format(trg_bnam))
        command = self.python_path
        command += ' "{}"'.format(os.path.join(self.scr_dir,'make_mask.py'))
        command += ' --shp_fnam "{}"'.format(self.values['gis_fnam'])
        command += ' --src_geotiff "{}"'.format(self.values['inp_fnam'])
        command += ' --dst_geotiff "{}"'.format(mask_fnam)
        command += ' --buffer="{}"'.format(-abs(self.values['buffer']))
        command += ' --use_index'
        self.run_command(command,message='<<< Make mask >>>')

        # Make rebinned image
        img_fnam = os.path.join(wrk_dir,'{}_resized.tif'.format(trg_bnam))
        ds = gdal.Open(self.values['inp_fnam'])
        inp_trans = ds.GetGeoTransform()
        inp_shape = (ds.RasterYSize,ds.RasterXSize)
        ds = None
        inp_xmin = inp_trans[0]
        inp_xstp = inp_trans[1]
        inp_xmax = inp_xmin+inp_xstp*inp_shape[1]
        inp_ymax = inp_trans[3]
        inp_ystp = inp_trans[5]
        inp_ymin = inp_ymax+inp_ystp*inp_shape[0]
        istp = int(abs(self.values['region_size']/inp_xstp)+0.5)
        jstp = int(abs(self.values['region_size']/inp_ystp)+0.5)
        if istp != jstp:
            raise ValueError('{}: error, istp={}, jstp={}'.format(self.proc_name,istp,jstp))
        command = self.python_path
        command += ' "{}"'.format(os.path.join(self.scr_dir,'rebin_gtiff.py'))
        command += ' --istp {}'.format(istp)
        command += ' --jstp {}'.format(jstp)
        command += ' --src_geotiff "{}"'.format(self.values['inp_fnam'])
        command += ' --dst_geotiff "{}"'.format(img_fnam)
        command += ' --mask_geotiff "{}"'.format(mask_fnam)
        command += ' --rmax 0.1'
        self.run_command(command,message='<<< Rebin image >>>')

        # Make parcel image
        mask_resized_fnam = os.path.join(wrk_dir,'{}_mask_resized.tif'.format(trg_bnam))
        command = self.python_path
        command += ' "{}"'.format(os.path.join(self.scr_dir,'rebin_mask.py'))
        command += ' --istp {}'.format(istp)
        command += ' --jstp {}'.format(jstp)
        command += ' --src_geotiff "{}"'.format(mask_fnam)
        command += ' --dst_geotiff "{}"'.format(mask_resized_fnam)
        command += ' --rmax 0.1'
        self.run_command(command,message='<<< Make parcel image >>>')

        # Estimate point-value
        command = self.python_path
        command += ' "{}"'.format(os.path.join(self.scr_dir,'drone_score_estimate.py'))
        command += ' --inp_fnam "{}"'.format(self.values['pv_fnam'])
        command += ' --src_geotiff "{}"'.format(img_fnam)
        command += ' --dst_geotiff "{}"'.format(os.path.join(wrk_dir,'{}_pv_mesh.tif'.format(trg_bnam)))
        for param,flag in zip(self.list_labels['y_params'],self.values['y_params']):
            if flag:
                command += ' --y_param {}'.format(param)
                command += ' --y_number {}'.format(self.values['pv_number'])
        for value,flag in zip(self.values['score_max'],self.values['y_params']):
            if flag:
                command += ' --smax {}'.format(value)
        for value,flag in zip(self.values['score_step'],self.values['y_params']):
            if flag:
                command += ' --sint {}'.format(value)
        if self.values['digitize']:
            command += ' --digitize'
        command += ' --fignam "{}"'.format(os.path.join(wrk_dir,'{}_pv_mesh.pdf'.format(trg_bnam)))
        for value,flag in zip(self.ax1_zmin[0],self.values['y_params']):
            if flag:
                command += ' --ax1_zmin="{}"'.format(value)
        for value,flag in zip(self.ax1_zmax[0],self.values['y_params']):
            if flag:
                command += ' --ax1_zmax="{}"'.format(value)
        for value,flag in zip(self.ax1_zstp[0],self.values['y_params']):
            if flag:
                command += ' --ax1_zstp="{}"'.format(value)
        command += ' --ax1_title "{}"'.format(trg_bnam)
        command += ' --remove_nan'
        command += ' --debug'
        command += ' --batch'
        self.run_command(command,message='<<< Estimate point-value >>>')

        # Estimate plot-mean
        command = self.python_path
        command += ' "{}"'.format(os.path.join(self.scr_dir,'drone_score_estimate.py'))
        command += ' --inp_fnam "{}"'.format(self.values['pm_fnam'])
        command += ' --src_geotiff "{}"'.format(img_fnam)
        command += ' --dst_geotiff "{}"'.format(os.path.join(wrk_dir,'{}_pm_mesh.tif'.format(trg_bnam)))
        for param,flag in zip(self.list_labels['y_params'],self.values['y_params']):
            if flag:
                command += ' --y_param {}'.format(param)
                command += ' --y_number {}'.format(self.values['pm_number'])
                command += ' --smax 1'
        command += ' --fignam "{}"'.format(os.path.join(wrk_dir,'{}_pm_mesh.pdf'.format(trg_bnam)))
        for value,flag in zip(self.ax1_zmin[1],self.values['y_params']):
            if flag:
                command += ' --ax1_zmin="{}"'.format(value)
        for value,flag in zip(self.ax1_zmax[1],self.values['y_params']):
            if flag:
                command += ' --ax1_zmax="{}"'.format(value)
        for value,flag in zip(self.ax1_zstp[1],self.values['y_params']):
            if flag:
                command += ' --ax1_zstp="{}"'.format(value)
        command += ' --ax1_title "{}"'.format(trg_bnam)
        command += ' --remove_nan'
        command += ' --debug'
        command += ' --batch'
        self.run_command(command,message='<<< Estimate plot-mean >>>')

        # Calculate damage intensity of plot from point-value
        command = self.python_path
        command += ' "{}"'.format(os.path.join(self.scr_dir,'drone_damage_calculate.py'))
        command += ' --src_geotiff "{}"'.format(os.path.join(wrk_dir,'{}_pv_mesh.tif'.format(trg_bnam)))
        command += ' --mask_geotiff "{}"'.format(mask_resized_fnam)
        command += ' --shp_fnam "{}"'.format(self.values['gis_fnam'])
        command += ' --out_csv "{}"'.format(os.path.join(wrk_dir,'{}_pv_plot.csv'.format(trg_bnam)))
        command += ' --out_shp "{}"'.format(os.path.join(wrk_dir,'{}_pv_plot.shp'.format(trg_bnam)))
        for param,flag in zip(self.list_labels['y_params'],self.values['y_params']):
            if flag:
                command += ' --y_param {}'.format(param)
        for value,flag in zip(self.values['score_max'],self.values['y_params']):
            if flag:
                command += ' --smax {}'.format(value)
        command += ' --rmax 0.01'
        command += ' --fignam "{}"'.format(os.path.join(wrk_dir,'{}_pv_plot.pdf'.format(trg_bnam)))
        for value,flag in zip(self.ax1_zmin[2],self.values['y_params']):
            if flag:
                command += ' --ax1_zmin="{}"'.format(value)
        for value,flag in zip(self.ax1_zmax[2],self.values['y_params']):
            if flag:
                command += ' --ax1_zmax="{}"'.format(value)
        for value,flag in zip(self.ax1_zstp[2],self.values['y_params']):
            if flag:
                command += ' --ax1_zstp="{}"'.format(value)
        command += ' --ax1_title "{}"'.format(trg_bnam)
        command += ' --use_index'
        command += ' --remove_nan'
        command += ' --debug'
        command += ' --batch'
        self.run_command(command,message='<<< Estimate damage intensity of plot from point-value >>>')

        # Calculate damage intensity of plot from plot-mean
        command = self.python_path
        command += ' "{}"'.format(os.path.join(self.scr_dir,'drone_damage_calculate.py'))
        command += ' --src_geotiff "{}"'.format(os.path.join(wrk_dir,'{}_pm_mesh.tif'.format(trg_bnam)))
        command += ' --mask_geotiff "{}"'.format(mask_resized_fnam)
        command += ' --shp_fnam "{}"'.format(self.values['gis_fnam'])
        command += ' --out_csv "{}"'.format(os.path.join(wrk_dir,'{}_pm_plot.csv'.format(trg_bnam)))
        command += ' --out_shp "{}"'.format(os.path.join(wrk_dir,'{}_pm_plot.shp'.format(trg_bnam)))
        for param,flag in zip(self.list_labels['y_params'],self.values['y_params']):
            if flag:
                command += ' --y_param {}'.format(param)
                command += ' --smax 1'
        command += ' --rmax 0.01'
        command += ' --fignam "{}"'.format(os.path.join(wrk_dir,'{}_pm_plot.pdf'.format(trg_bnam)))
        for value,flag in zip(self.ax1_zmin[3],self.values['y_params']):
            if flag:
                command += ' --ax1_zmin="{}"'.format(value)
        for value,flag in zip(self.ax1_zmax[3],self.values['y_params']):
            if flag:
                command += ' --ax1_zmax="{}"'.format(value)
        for value,flag in zip(self.ax1_zstp[3],self.values['y_params']):
            if flag:
                command += ' --ax1_zstp="{}"'.format(value)
        command += ' --ax1_title "{}"'.format(trg_bnam)
        command += ' --use_index'
        command += ' --remove_nan'
        command += ' --debug'
        command += ' --batch'
        self.run_command(command,message='<<< Estimate damage intensity of plot from plot-mean >>>')

        if os.path.exists(mask_fnam):
            os.remove(mask_fnam)
        if os.path.exists(mask_resized_fnam):
            os.remove(mask_resized_fnam)

        # Finish process
        super().finish()
        return
