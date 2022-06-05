import os
import sys
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
        command += ' --src_geotiff {}'.format(self.values[''])
        command += ' --dst_geotiff {}'.format(self.values[''])
        command += ' --gps_fnam {}'.format(self.values[''])
        command += ' --bunch_rmax {}'.format(self.values[''])
        command += ' --bunch_emax {}'.format(self.values[''])
        command += ' --bunch_nmin {}'.format(self.values[''])
        command += ' --buffer {}'.format(self.values[''])
        command += ' --gamma 1'
        command += ' --fact 30'
        command += ' --interp_point'
        command += ' --remove_nan'
        command += ' --debug'
        command += ' --batch'

"""
    call('drone_subset.py -I /home/naohiro/Work/Drone/220316/orthomosaic/ndvi_rms_repeat/P4M_RTK_{}_{:%Y%m%d}_geocor.tif -O {}.tif -g {}.csv -dNi -G 1 -S 30'.format(block.lower(),date,target,target),shell=True)
    call('drone_calc_rr.py -I {}_plot1.tif --data_min 10 -d -n  -p Lrg -p Nr -z 0 -Z 20 -s 5 -Z 5'.format(target),shell=True)
    call('drone_calc_rr.py -I {}_plot2.tif --data_min 10 -d -n  -p Lrg -p Nr -z 0 -Z 20 -s 5 -Z 5'.format(target),shell=True)
    call('drone_calc_rr.py -I {}_plot3.tif --data_min 10 -d -n  -p Lrg -p Nr -z 0 -Z 20 -s 5 -Z 5'.format(target),shell=True)
    call('drone_extract_points.py -I {}.tif -g {}.csv -dn -z 0 -Z 0.3 -s 0.1'.format(target,target),shell=True)
        return
"""
        # Finish process
        sys.stderr.write('Finished process {}.\n\n'.format(self.proc_name))
        sys.stderr.flush()
