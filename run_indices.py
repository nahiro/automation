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
        trg_bnam = '{}_{}'.format(self.current_block,self.current_date)
        out_params = [(('S'+param) if len(param) == 1 else param) for param in self.list_labels['out_params']]
        command = self.python_path
        command += ' {}'.format(os.path.join(self.scr_dir,'drone_calc_indices.py'))
        command += ' --src_geotiff {}'.format(self.values['inp_fnam'])
        command += ' --dst_geotiff {}'.format(os.path.join(wrk_dir,'{}_indices.tif'.format(trg_bnam)))
        command += ' --fignam {}'.format(os.path.join(wrk_dir,'{}_indices.pdf'.format(trg_bnam)))
        for param,flag in zip(out_params,self.values['out_params']):
            if flag:
                command += ' --param {}'.format(param)
        for band,flag in zip(self.list_labels['norm_bands'],self.values['norm_bands']):
            if flag:
                command += ' --norm_band {}'.format(band)
        command += ' --rgi_red_band {}'.format(self.values['rgi_red_band'])
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

        # Finish process
        sys.stderr.write('Finished process {}.\n\n'.format(self.proc_name))
        sys.stderr.flush()
        return
