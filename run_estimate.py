import os
import sys
from subprocess import call
from proc_class import Process

class Estimate(Process):

    def run(self):
        # Start process
        super().run()

        # Check files
        if not os.path.exists(self.values['inp_fnam']):
            raise IOError('{}: error, no such file >>> {}'.format(self.proc_name,self.values['inp_fnam']))
        if not os.path.exists(self.values['score_fnam']):
            raise IOError('{}: error, no such file >>> {}'.format(self.proc_name,self.values['score_fnam']))
        if not os.path.exists(self.values['intensity_fnam']):
            raise IOError('{}: error, no such file >>> {}'.format(self.proc_name,self.values['intensity_fnam']))
        etc_dir = os.path.join(self.drone_analysis,self.current_block,self.current_date,self.proc_name)
        wrk_dir = os.path.join(self.drone_analysis,self.proc_name)
        if not os.path.exists(etc_dir):
            os.makedirs(etc_dir)
        if not os.path.isdir(etc_dir):
            raise ValueError('{}: error, no such folder >>> {}'.format(self.proc_name,etc_dir))
        if not os.path.exists(wrk_dir):
            os.makedirs(wrk_dir)
        if not os.path.isdir(wrk_dir):
            raise ValueError('{}: error, no such folder >>> {}'.format(self.proc_name,wrk_dir))

        # Estimate score
        trg_bnam = '{}_{}'.format(self.current_block,self.current_date)
        command = self.python_path
        command += ' {}'.format(os.path.join(self.scr_dir,'drone_score_estimate.py'))
        command += ' --inp_fnam {}'.format(self.values['score_fnam'])
        command += ' --src_geotiff {}'.format(self.values['inp_fnam'])
        command += ' --dst_geotiff {}'.format(os.path.join(etc_dir,'{}_score.tif'.format(trg_bnam)))
        for param,flag in zip(self.list_labels['y_params'],self.values['y_params']):
            if flag:
                command += ' --y_param {}'.format(param)
                command += ' --y_number {}'.format(self.values['score_number'])
        for param,flag,value in zip(self.list_labels['y_params'],self.values['y_params'],self.values['score_max']):
            if flag:
                command += ' --smax {}'.format(value)
        for param,flag,value in zip(self.list_labels['y_params'],self.values['y_params'],self.values['score_step']):
            if flag:
                command += ' --sint {}'.format(value)
        if self.values['digitize']:
            command += ' --digitize'
        command += ' --fignam {}'.format(os.path.join(etc_dir,'{}_score.pdf'.format(trg_bnam)))
        command += ' --remove_nan'
        command += ' --debug'
        command += ' --batch'
        sys.stderr.write('\nEstimate score\n')
        sys.stderr.write(command+'\n')
        sys.stderr.flush()
        call(command,shell=True)

        # Estimate intensity
        command = self.python_path
        command += ' {}'.format(os.path.join(self.scr_dir,'drone_score_estimate.py'))
        command += ' --inp_fnam {}'.format(self.values['intensity_fnam'])
        command += ' --src_geotiff {}'.format(self.values['inp_fnam'])
        command += ' --dst_geotiff {}'.format(os.path.join(etc_dir,'{}_intensity.tif'.format(trg_bnam)))
        for param,flag in zip(self.list_labels['y_params'],self.values['y_params']):
            if flag:
                command += ' --y_param {}'.format(param)
                command += ' --y_number {}'.format(self.values['intensity_number'])
                command += ' --smax 1'
        command += ' --fignam {}'.format(os.path.join(etc_dir,'{}_intensity.pdf'.format(trg_bnam)))
        command += ' --remove_nan'
        command += ' --debug'
        command += ' --batch'
        sys.stderr.write('\nEstimate intensity\n')
        sys.stderr.write(command+'\n')
        sys.stderr.flush()
        call(command,shell=True)

        #drone_score_estimate.py -I P4M_RTK_11b_20220301_geocor_indices_rebin.tif -i drone_score_fit.csv -d
        #drone_damage_calculate.py -I P4M_RTK_11b_20220301_geocor_indices_rebin_estimate.tif -M P4M_RTK_11b_20220301_geocor_mask_rebin.tif -i All_area_polygon_20210914/All_area_polygon_20210914.shp -dn
        # Finish process
        sys.stderr.write('Finished process {}.\n\n'.format(self.proc_name))
        sys.stderr.flush()
        return
