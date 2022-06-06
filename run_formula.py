import os
import sys
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


        command += ('S'+self.values['rr_param'][0] if self.values['rr_param'][0].islower() else self.values['rr_param'][0])


        with open(tmp_fnam,'w') as fp:
            fp.write(self.values['inp_fnams'])
        command = self.python_path
        command += ' {}'.format(os.path.join(self.scr_dir,'drone_score_fit.py'))
        command += ' --inp_list {}'.format(tmp_fnam)
        command += ' --out_fnam {}'.format(os.path.join(wrk_dir,'{}_score_formula.csv'.format(trg_bnam)))


        for param,flag in zip(x_params,self.values['x_params']):
            if flag:
                command += ' --x_param {}'.format(param)


        for param,flag in zip(self.list_labels['x_params'],self.values['x_params']):
            if flag:
                command += ' --norm_band {}'.format(band)


        command += ' --x_param {}'.format(self.values[''])
        command += ' {}'.format(self.values[''])
        command += ' {}'.format(self.values[''])
        command += ' {}'.format(self.values[''])
        command += ' {}'.format(self.values[''])
        command += ' {}'.format(self.values[''])
        command += ' {}'.format(self.values[''])
        command += ' --debug'
        command += ' --batch'

        # Finish process
        sys.stderr.write('Finished process {}.\n\n'.format(self.proc_name))
        sys.stderr.flush()
        return
