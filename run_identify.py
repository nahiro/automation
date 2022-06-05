import os
import sys
try:
    import gdal
except Exception:
    from osgeo import gdal
import numpy as np
import pandas as pd
from subprocess import call
from proc_class import Process

class Identify(Process):

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
        wrk_dir = os.path.join(self.drone_analysis,self.current_block,self.current_date,self.proc_name)
        if not os.path.exists(wrk_dir):
            os.makedirs(wrk_dir)
        if not os.path.isdir(wrk_dir):
            raise ValueError('{}: error, no such folder >>> {}'.format(self.proc_name,wrk_dir))

        # Read data
        trg_bnam = '{}_{}'.format(self.current_block,self.current_date)
        orders = {'0th':0,'1st':1,'2nd':2,'3rd':3}
        command = self.python_path
        command += ' {}'.format(os.path.join(self.scr_dir,'read_survey_xls.py'))
        command += ' --inp_fnam {}'.format(self.values['obs_fnam'])
        command += ' --geocor_fnam {}'.format(self.values['gcp_fnam'])
        command += ' --sheet {}'.format(self.values['i_sheet'])
        command += ' --epsg {}'.format(self.values['epsg'])
        command += ' --geocor_npoly {}'.format(orders[self.values['geocor_order']])
        command += ' --optfile {}'.format(os.path.join(wrk_dir,'temp.dat'))
        command += ' --out_fnam {}'.format(os.path.join(wrk_dir,'{}_identify.csv'.format(trg_bnam)))
        sys.stderr.write('\nRead observation data\n')
        sys.stderr.write(command+'\n')
        sys.stderr.flush()
        call(command,shell=True)
        df = pd.read_csv(os.path.join(wrk_dir,'{}_identify.csv'.format(trg_bnam)),comment='#')
        df.columns = df.columns.str.strip()
        plot_bunch = df['PlotPaddy'].values
        plots = np.unique(plot_bunch)

        # Subset image
        command = self.python_path
        command += ' {}'.format(os.path.join(self.scr_dir,'drone_subset.py'))
        command += ' --src_geotiff {}'.format(self.values['inp_fnam'])
        command += ' --dst_geotiff {}'.format(os.path.join(wrk_dir,'{}.tif'.format(trg_bnam)))
        command += ' --gps_fnam {}'.format(os.path.join(wrk_dir,'{}_identify.csv'.format(trg_bnam)))
        command += ' --bunch_rmax {}'.format(self.values['bunch_rmax'])
        command += ' --bunch_emax {}'.format(self.values['bunch_emax'])
        command += ' --bunch_nmin {}'.format(self.values['bunch_nmin'])
        command += ' --buffer {}'.format(self.values['buffer'])
        command += ' --fignam {}'.format(os.path.join(wrk_dir,'{}_subset.pdf'.format(trg_bnam)))
        command += ' --gamma 1'
        command += ' --fact 30'
        command += ' --interp_point'
        command += ' --remove_nan'
        command += ' --debug'
        command += ' --batch'
        sys.stderr.write('\nSubset image\n')
        sys.stderr.write(command+'\n')
        sys.stderr.flush()
        call(command,shell=True)
        ds = gdal.Open(iself.values['inp_fnam'])
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
        sys.stderr.write('\nCalculate redness ratio\n')
        for plot in plots:
            command = self.python_path
            command += ' {}'.format(os.path.join(self.scr_dir,'drone_calc_rr.py'))
            command += ' --src_geotiff {}'.format(os.path.join(wrk_dir,'{}_plot{}.tif'.format(trg_bnam,plot)))
            command += ' --dst_geotiff {}'.format(os.path.join(wrk_dir,'{}_plot{}_rr.tif'.format(trg_bnam,plot)))
            command += ' --param {}'.format('S'+self.values['rr_param'][0] if self.values['rr_param'][0].islower() else self.values['rr_param'][0])
            command += ' --param {}'.format('Br' if self.values['rr_param'][1] in ['S/B'] else 'Nr')
            command += ' --inner_size {}'.format(inner_size)
            command += ' --outer_size {}'.format(outer_size)
            if not np.isnan(self.values['data_range'][0]):
                command += ' --data_min="{}"'.format(self.values['data_range'][0])
            if not np.isnan(self.values['data_range'][1]):
                command += ' --data_max="{}"'.format(self.values['data_range'][1])
            command += ' --fignam {}'.format(os.path.join(wrk_dir,'{}_plot{}_rr.pdf'.format(trg_bnam)))
            # for Redness Ratio
            command += ' --ax1_zmin 0'
            command += ' --ax1_zmax 20'
            command += ' --ax1_zstp 5'
            # for Signal Ratio
            command += ' --ax1_zmin 0'
            command += ' --ax1_zmax 5'
            command += ' --ax1_zstp 1'
            command += ' --remove_nan'
            command += ' --debug'
            command += ' --batch'
            sys.stderr.write(command+'\n')
            sys.stderr.flush()
            call(command,shell=True)

        """
        call('drone_calc_rr.py -I {}_plot1.tif --data_min 10 -d -n  -p Lrg -p Nr -z 0 -Z 20 -s 5 -Z 5'.format(target),shell=True)
        call('drone_calc_rr.py -I {}_plot2.tif --data_min 10 -d -n  -p Lrg -p Nr -z 0 -Z 20 -s 5 -Z 5'.format(target),shell=True)
        call('drone_calc_rr.py -I {}_plot3.tif --data_min 10 -d -n  -p Lrg -p Nr -z 0 -Z 20 -s 5 -Z 5'.format(target),shell=True)
        call('drone_extract_points.py -I {}.tif -g {}.csv -dn -z 0 -Z 0.3 -s 0.1'.format(target,target),shell=True)
            return
        """
        # Finish process
        sys.stderr.write('Finished process {}.\n\n'.format(self.proc_name))
        sys.stderr.flush()
