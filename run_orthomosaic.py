#!/usr/bin/env python
import os
import sys
import numpy as np
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
            fp.write('\n'.join(dnams))
        command = '"{}"'.format(self.values['metashape_path'])
        command += ' -r {}'.format(os.path.join(self.scr_dir,'make_orthomosaic.py'))
        command += ' --inp_list {}'.format(tmp_fnam)
        command += ' --out_dnam {}'.format(wrk_dir)
        command += ' --out_fnam {}'.format('{}.tif'.format(trg_bnam))
        command += ' --panel_fnam "{}"'.format(self.values['panel_fnam'])
        command += ' --qmin {}'.format(self.values['qmin'])
        command += ' --align_level {}'.format(self.values['align_level'])
        command += ' --key_limit {}'.format(self.values['point_limit'][0])
        command += ' --tie_limit {}'.format(self.values['point_limit'][1])
        for param,flag in zip(self.list_labels['cam_params'][:-1],self.values['cam_params'][:-1]):
            if flag:
                command += ' --camera_param {}'.format(param)
        command += ' --depth_map_quality {}'.format(self.values['depth_map'][0])
        command += ' --filter_mode {}'.format(self.values['depth_map'][1])
        command += ' --epsg {}'.format(self.values['epsg'])
        command += ' --pixel_size {}'.format(self.values['pixel_size'])
        for factor in self.values['scale_factor']:
            if not np.isnan(factor):
                command += ' --scale_factor {}'.format(factor)
        command += ' --output_type {}'.format(self.values['output_type'])
        if self.values['calib_flag'][0]:
            command += ' --use_panel'
        if not self.values['calib_flag'][1]:
            command += ' --ignore_sunsensor'
        if not self.values['xmp_flag'][0]:
            command += ' --ignore_xmp_calibration'
        if not self.values['xmp_flag'][1]:
            command += ' --ignore_xmp_orientation'
        if not self.values['xmp_flag'][2]:
            command += ' --ignore_xmp_accuracy'
        if not self.values['xmp_flag'][3]:
            command += ' --ignore_xmp_antenna'
        if not self.values['preselect'][0]:
            command += ' --disable_generic_preselection'
        if not self.values['preselect'][1]:
            command += ' --disable_reference_preselection'
        if not self.values['optimize_flag']:
            command += ' --disable_camera_optimization'
        if not self.values['cam_params'][-1]:
            command += ' --disable_fit_correction {}'
        if self.values['cam_flags'][0]:
            command += ' --adaptive_fitting_align'
        if self.values['cam_flags'][1]:
            command += ' --adaptive_fitting_optimize'
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
