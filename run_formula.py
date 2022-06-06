import os
import sys
import numpy as np
from proc_class import Process

class Formula(Process):

    def run(self):
        # Start process
        super().run()

        # Check files
        for line in self.values['inp_fnams'].splitlines():
            fnam = line.strip()
            if not os.path.exists(fnam):
                raise IOError('{}: error, no such file >>> {}'.format(self.proc_name,fnam))
        wrk_dir = os.path.join(self.drone_analysis,self.proc_name)
        if not os.path.exists(wrk_dir):
            os.makedirs(wrk_dir)
        if not os.path.isdir(wrk_dir):
            raise ValueError('{}: error, no such folder >>> {}'.format(self.proc_name,wrk_dir))

        # Make score formula
        trg_bnam = '{}_{}'.format(self.current_block,self.current_date)
        tmp_fnam = os.path.join(wrk_dir,'temp.dat')
        x_params = [(('S'+param) if param.islower() else param) for param in self.list_labels['x_params']]
        with open(tmp_fnam,'w') as fp:
            fp.write(self.values['inp_fnams'])
        command = self.python_path
        command += ' {}'.format(os.path.join(self.scr_dir,'drone_score_fit.py'))
        command += ' --inp_list {}'.format(tmp_fnam)
        command += ' --out_fnam {}'.format(os.path.join(wrk_dir,'{}_score_formula.csv'.format(trg_bnam)))
        for param,flag in zip(x_params,self.values['x_params']):
            if flag:
                command += ' --x_param {}'.format(param)
        for param,flag in zip(self.list_labels['q_params'],self.values['q_params']):
            if flag:
                command += ' --q_param {}'.format(param)
        for param,flag in zip(self.list_labels['y_params'],self.values['y_params']):
            if flag:
                command += ' --y_param {}'.format(param)
        for param,value in zip(self.list_labels['y_params'],self.values['ythr']):
            if not np.isnan(value):
                command += ' --y_threshold "{}:{}"'.format(param,value)
        for param,value in zip(self.list_labels['y_params'],self.values['score_max']):
            if not np.isnan(value):
                command += ' --y_max "{}:{}"'.format(param,value)
        for param,value in zip(self.list_labels['y_params'],self.values['score_step']):
            if not np.isnan(value):
                command += ' --y_int "{}:{}"'.format(param,value)
        for y_param,label in zip(self.list_labels['y_params'],['yfac{}'.format(i+1) for i in range(len(self.list_labels['y_params']))]):
            for param,value in zip(self.list_labels['y_params'],self.values[label]):
                if not np.isnan(value):
                    command += ' --y_factor "{}:{}:{}"'.format(y_param,param,value)
        command += ' --vmax {}'.format(self.values['vif_max'])
        command += ' --nx_min {}'.format(self.values['n_x'][0])
        command += ' --nx_max {}'.format(self.values['n_x'][1])
        command += ' --ncheck_min {}'.format(self.values['n_multi'])
        command += ' --nmodel_max {}'.format(self.values['n_formula'])
        command += ' --criteria {}'.format(self.values['criteria'])
        command += ' --n_cross {}'.format(self.values['n_cros'])
        command += ' --amin {}'.format(self.values['age_range'][0])
        command += ' --amax {}'.format(self.values['age_range'][1])
        if self.values['mean_fitting']:
            command += ' --mean_fitting'
        command += ' --fignam {}'.format(os.path.join(wrk_dir,'{}_score_formula.pdf'.format(trg_bnam)))
        command += ' --debug'
        command += ' --batch'
        sys.stderr.write('\nMake score formula\n')
        sys.stderr.write(command+'\n')
        sys.stderr.flush()
        call(command,shell=True)

        # Finish process
        sys.stderr.write('Finished process {}.\n\n'.format(self.proc_name))
        sys.stderr.flush()
        return
