#!/usr/bin/env python
import os
from subprocess import call
from proc_class import Process

class Orthomosaic(Process):

    def run(self):
        # Start process
        super().run()

        # Check folders
        dnams = []
        for line in self.values['inpdirs'].splitlines():
            dnam = line.strip()
            if (len(dnam) < 1) or (dnam[0] == '#'):
                continue
            if not os.path.isdir(dnam):
                raise IOError('{}: error, no such folder >>> "{}"'.format(self.proc_name,dnam))
            dnams.append(dnam)
        trg_bnam = '{}_{}'.format(self.current_block,self.current_date)
        wrk_dir = os.path.join(self.drone_analysis,self.current_block,self.current_date,self.proc_name)
        if not os.path.exists(wrk_dir):
            os.makedirs(wrk_dir)
        if not os.path.isdir(wrk_dir):
            raise ValueError('{}: error, no such folder >>> {}'.format(self.proc_name,wrk_dir))

        # Make orthomosaic image
        tmp_fnam = os.path.join(wrk_dir,'temp.dat')
        with open(tmp_fnam,'w') as fp:
            fp.write('\n'.join(fnams))
        command = self.python_path
        command += ' {}'.format(os.path.join(self.scr_dir,'make_orthomosaic.py'))
        command += ' --inp_list {}'.format(tmp_fnam)
        command += ''
        sys.stderr.write('\nMake orthomosaic image\n')
        sys.stderr.write(command+'\n')
        sys.stderr.flush()
        call(command,shell=True)
        if os.path.exists(tmp_fnam):
            os.remove(tmp_fnam)

        # Finish process
        sys.stderr.write('Finished process {}.\n\n'.format(self.proc_name))
        sys.stderr.flush()
        return
#command = proccess.values['metashape_path']
