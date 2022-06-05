import os
import sys
import numpy as np
from subprocess import call
from proc_class import Process

class Indices(Process):

    def run(self):
        # Start process
        super().run()

        # Check files
        if not os.path.exists(self.values['inp_fnam']):
            raise IOError('{}: error, no such file >>> {}'.format(self.proc_name,self.values['inp_fnam']))
        wrk_dir = os.path.join(self.drone_analysis,self.current_block,self.current_date,self.proc_name)
        if not os.path.exists(wrk_dir):
            os.makedirs(wrk_dir)
        if not os.path.isdir(wrk_dir):
            raise ValueError('{}: error, no such folder >>> {}'.format(self.proc_name,wrk_dir))

        # Calculate indices
        command = self.python_path
        command += ' {}'.format(os.path.join(self.scr_dir,'drone_calc_indices.py'))
        command += ' --src_geotiff {}'.format(self.values['inp_fnam'])
        command += ' --dst_geotiff {}'.format(os.path.join(wrk_dir,'{}_{}_indices.tif'.format(self.current_block,self.current_date)))
        command += ' --fignam {}'.format(os.path.join(wrk_dir,'{}_{}_indices.pdf'.format(self.current_block,self.current_date)))
        for param in self.values['out_params']:
            command += ' --param {}'.format(param)
        for band in self.values['norm_bands']:
            command += ' --norm_band'.format(band)
        command += ' --rgi_red_band '.format(self.values['rgi_red_band'])
        if not np.isnan(self.values['data_range'][0]):
            command += ' --data_min="{}"'.format(self.values['data_range'][0])
        if not np.isnan(self.values['data_range'][1]):
            command += ' --data_max="{}"'.format(self.values['data_range'][1])
        command += ' --remove_nan'
        command += ' --debug'
        command += ' --batch'
        sys.stderr.write('\nCalculate indices\n')
        sys.stderr.write(command+'\n')
        sys.stderr.flush()
        call(command,shell=True)

        return
