import os
import sys
try:
    import gdal
except Exception:
    from osgeo import gdal
import numpy as np
import pandas as pd
from proc_class import Process

class Identify(Process):

    def __init__(self):
        super().__init__()
        self._freeze()

    def run(self):
        # Start process
        super().run()

        # Check files
        if not os.path.exists(self.values['inp_fnam']):
            raise IOError('{}: error, no such file >>> {}'.format(self.proc_name,self.values['inp_fnam']))
        if not os.path.exists(self.values['gcp_fnam']):
            raise IOError('{}: error, no such file >>> {}'.format(self.proc_name,self.values['gcp_fnam']))
        if not os.path.exists(self.values['obs_fnam']):
            raise IOError('{}: error, no such file >>> {}'.format(self.proc_name,self.values['obs_fnam']))
        if (self.values['assign_fnam'] != '') and not os.path.exists(self.values['assign_fnam']):
            raise IOError('{}: error, no such file >>> {}'.format(self.proc_name,self.values['assign_fnam']))
        trg_bnam = '{}_{}'.format(self.obs_block,self.obs_date)
        wrk_dir = os.path.join(self.drone_analysis,self.obs_block,self.proc_name)
        if not os.path.exists(wrk_dir):
            os.makedirs(wrk_dir)
        if not os.path.isdir(wrk_dir):
            raise ValueError('{}: error, no such folder >>> {}'.format(self.proc_name,wrk_dir))

        # Read data
        orders = {'0th':0,'1st':1,'2nd':2,'3rd':3}
        tmp_fnam = self.mktemp(suffix='.dat')
        command = self.python_path
        command += ' "{}"'.format(os.path.join(self.scr_dir,'read_survey_xls.py'))
        command += ' --inp_fnam "{}"'.format(self.values['obs_fnam'])
        command += ' --geocor_fnam "{}"'.format(self.values['gcp_fnam'])
        command += ' --sheet {}'.format(self.values['i_sheet'])
        command += ' --epsg {}'.format(self.values['epsg'])
        command += ' --geocor_npoly {}'.format(orders[self.values['geocor_order']])
        command += ' --optfile "{}"'.format(tmp_fnam)
        command += ' --out_fnam "{}"'.format(os.path.join(wrk_dir,'{}_observation.csv'.format(trg_bnam)))
        self.run_command(command,message='<<< Read observation data >>>')
        if os.path.exists(tmp_fnam):
            os.remove(tmp_fnam)

        df = pd.read_csv(os.path.join(wrk_dir,'{}_observation.csv'.format(trg_bnam)),comment='#')
        df.columns = df.columns.str.strip()
        plot_bunch = df['PlotPaddy'].astype(int).values
        plots = np.unique(plot_bunch)

        # Subset image
        command = self.python_path
        command += ' "{}"'.format(os.path.join(self.scr_dir,'drone_subset.py'))
        command += ' --src_geotiff "{}"'.format(self.values['inp_fnam'])
        command += ' --dst_geotiff "{}"'.format(os.path.join(wrk_dir,'{}.tif'.format(trg_bnam)))
        command += ' --gps_fnam "{}"'.format(os.path.join(wrk_dir,'{}_observation.csv'.format(trg_bnam)))
        command += ' --bunch_rmax {}'.format(self.values['bunch_rmax'])
        command += ' --bunch_emax {}'.format(self.values['bunch_emax'])
        command += ' --bunch_nmin {}'.format(self.values['bunch_nmin'])
        command += ' --buffer {}'.format(self.values['buffer'])
        command += ' --fignam "{}"'.format(os.path.join(wrk_dir,'{}_subset.pdf'.format(trg_bnam)))
        command += ' --ax1_title "{}"'.format(trg_bnam)
        command += ' --gamma 1'
        command += ' --fact 30'
        command += ' --interp_point'
        command += ' --remove_nan'
        command += ' --debug'
        command += ' --batch'
        self.run_command(command,message='<<< Subset image >>>')

        ds = gdal.Open(self.values['inp_fnam'])
        trans = ds.GetGeoTransform()
        ds = None
        xstp = trans[1]
        ystp = trans[5]
        pixel_size = abs(xstp)
        inner_size = int(self.values['neighbor_size'][0]/pixel_size+0.5)
        if (inner_size%2) == 0:
            inner_size += 1
        outer_size = int(self.values['neighbor_size'][1]/pixel_size+0.5)
        if (outer_size%2) == 0:
            outer_size += 1
        if outer_size <= inner_size:
            outer_size = inner_size+2

        # Calculate redness ratio/signal ratio
        for plot in plots:
            command = self.python_path
            command += ' "{}"'.format(os.path.join(self.scr_dir,'drone_calc_rr.py'))
            command += ' --src_geotiff "{}"'.format(os.path.join(wrk_dir,'{}_plot{}.tif'.format(trg_bnam,plot)))
            command += ' --dst_geotiff "{}"'.format(os.path.join(wrk_dir,'{}_plot{}_rr.tif'.format(trg_bnam,plot)))
            command += ' --param {}'.format('S'+self.values['rr_param'][0] if self.values['rr_param'][0].islower() else self.values['rr_param'][0])
            command += ' --param {}'.format('Br' if self.values['rr_param'][1] in ['S/B'] else 'Nr')
            command += ' --inner_size {}'.format(inner_size)
            command += ' --outer_size {}'.format(outer_size)
            if not np.isnan(self.values['data_range'][0]):
                command += ' --data_min="{}"'.format(self.values['data_range'][0])
            if not np.isnan(self.values['data_range'][1]):
                command += ' --data_max="{}"'.format(self.values['data_range'][1])
            command += ' --fignam "{}"'.format(os.path.join(wrk_dir,'{}_plot{}_rr.pdf'.format(trg_bnam,plot)))
            command += ' --ax1_title "{} (Plot{})"'.format(trg_bnam,plot)
            # for Redness Ratio
            command += ' --ax1_zmin 0'
            command += ' --ax1_zmax 1'
            command += ' --ax1_zstp 0.2'
            # for Signal Ratio
            command += ' --ax1_zmin 0'
            command += ' --ax1_zmax 5'
            command += ' --ax1_zstp 1'
            command += ' --remove_nan'
            command += ' --debug'
            command += ' --batch'
            self.run_command(command,message='<<< Calculate redness ratio (Plot{}) >>>'.format(plot))

        # Identify point
        if self.values['assign_fnam'] != '':
            tmp_fnam = self.values['assign_fnam']
        elif ((np.flatnonzero(self.values['assign_plot1']).size > 0) or
              (np.flatnonzero(self.values['assign_plot2']).size > 0) or
              (np.flatnonzero(self.values['assign_plot3']).size > 0)):
            tmp_fnam = os.path.join(wrk_dir,'{}_assign.dat'.format(trg_bnam))
            with open(tmp_fnam,'w') as fp:
                for pnam in ['assign_plot1','assign_plot2','assign_plot3']:
                    for p_org,p_new in zip(self.list_labels[pnam],self.values[pnam]):
                        if p_new != 0:
                            fp.write('{} {}\n'.format(int(p_org.replace(':','')),p_new))
        else:
            tmp_fnam = None
        command = self.python_path
        command += ' "{}"'.format(os.path.join(self.scr_dir,'drone_identify_points.py'))
        command += ' --src_geotiff "{}"'.format(os.path.join(wrk_dir,'{}.tif'.format(trg_bnam)))
        command += ' --csv_fnam "{}"'.format(os.path.join(wrk_dir,'{}_observation.csv'.format(trg_bnam)))
        command += ' --out_fnam "{}"'.format(os.path.join(wrk_dir,'{}_identify.csv'.format(trg_bnam)))
        command += ' --bunch_rmax {}'.format(self.values['bunch_rmax'])
        command += ' --bunch_emax {}'.format(self.values['bunch_emax'])
        command += ' --bunch_nmin {}'.format(self.values['bunch_nmin'])
        command += ' --pixel_rmax {}'.format(self.values['point_rmax'])
        command += ' --point_dmax {}'.format(self.values['point_dmax'][0])
        command += ' --point_lwid {}'.format(self.values['point_dmax'][1])
        command += ' --point_smin {}'.format(self.values['point_area'][0])
        command += ' --point_smax {}'.format(self.values['point_area'][1])
        command += ' --point_area {}'.format(self.values['point_area'][2])
        command += ' --point_nmin {}'.format(self.values['point_nmin'])
        command += ' --rr_param {}'.format('S'+self.values['rr_param'][0] if self.values['rr_param'][0].islower() else self.values['rr_param'][0])
        command += ' --sr_param {}'.format('Br' if self.values['rr_param'][1] in ['S/B'] else 'Nr')
        command += ' --rthr_min {}'.format(self.values['rthr'][0])
        command += ' --rthr_max {}'.format(self.values['rthr'][1])
        command += ' --rstp {}'.format(self.values['rthr'][2])
        command += ' --sthr {}'.format(self.values['sthr'])
        command += ' --criteria "{}"'.format('Distance' if 'Distance' in self.values['criteria'] else 'Area')
        command += ' --fignam "{}"'.format(os.path.join(wrk_dir,'{}_identify.pdf'.format(trg_bnam)))
        command += ' --ax1_title "{}"'.format(trg_bnam)
        command += ' --gamma 1'
        command += ' --fact 30'
        command += ' --ax1_zmin 0.0'
        command += ' --ax1_zmax 0.3'
        command += ' --ax1_zstp 0.1'
        if tmp_fnam is not None:
            command += ' --assign_fnam "{}"'.format(tmp_fnam)
        if self.values['ignore_error']:
            command += ' --ignore_error'
        command += ' --remove_nan'
        command += ' --debug'
        command += ' --batch'
        self.run_command(command,message='<<< Identify point >>>')

        # Finish process
        super().finish()
        return
