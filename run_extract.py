import os
import sys
from proc_class import Process

class Extract(Process):

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
        if not os.path.exists(self.values['obs_fnam']):
            raise IOError('{}: error, no such file >>> {}'.format(self.proc_name,self.values['obs_fnam']))
        if not os.path.exists(self.values['gps_fnam']):
            raise IOError('{}: error, no such file >>> {}'.format(self.proc_name,self.values['gps_fnam']))
        trg_bnam = '{}_{}'.format(self.current_block,self.current_date)
        wrk_dir = os.path.join(self.drone_analysis,self.proc_name)
        if not os.path.exists(wrk_dir):
            os.makedirs(wrk_dir)
        if not os.path.isdir(wrk_dir):
            raise ValueError('{}: error, no such folder >>> {}'.format(self.proc_name,wrk_dir))

        # Read data
        command = self.python_path
        command += ' "{}"'.format(os.path.join(self.scr_dir,'read_survey_xls.py'))
        command += ' --inp_fnam "{}"'.format(self.values['obs_fnam'])
        command += ' --sheet {}'.format(self.values['i_sheet'])
        command += ' --ref_fnam "{}"'.format(self.values['gps_fnam'])
        command += ' --epsg {}'.format(self.values['epsg'])
        command += ' --out_fnam "{}"'.format(os.path.join(wrk_dir,'{}_observation.csv'.format(trg_bnam)))
        self.run_command(command,message='<<< Read observation data >>>')

        # Extract indices
        command = self.python_path
        command += ' "{}"'.format(os.path.join(self.scr_dir,'drone_extract_values.py'))
        command += ' --src_geotiff "{}"'.format(self.values['inp_fnam'])
        command += ' --csv_fnam "{}"'.format(os.path.join(wrk_dir,'{}_observation.csv'.format(trg_bnam)))
        command += ' --ext_fnam "{}"'.format(os.path.join(wrk_dir,'{}_extract.csv'.format(trg_bnam)))
        command += ' --inner_radius {}'.format(self.values['region_size'][0])
        command += ' --outer_radius {}'.format(self.values['region_size'][1])
        command += ' --fignam "{}"'.format(os.path.join(wrk_dir,'{}_extract.pdf'.format(trg_bnam)))
        command += ' --ax1_zmin="{}"'.format(self.ax1_zmin)
        command += ' --ax1_zmax="{}"'.format(self.ax1_zmax)
        command += ' --ax1_zstp="{}"'.format(self.ax1_zstp)
        command += ' --ax1_title "{}"'.format(trg_bnam)
        command += ' --remove_nan'
        command += ' --debug'
        command += ' --batch'
        self.run_command(command,message='<<< Extract indices >>>')

        # Finish process
        sys.stderr.write('Finished process {}.\n\n'.format(self.proc_name))
        sys.stderr.flush()
        return
