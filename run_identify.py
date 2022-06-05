import os
import sys
from subprocess import call
from proc_class import Process

class Identify(Process):

    def run(self):
        # Start process
        super().run()

        # Check files
        if not os.path.exists(self.values['inp_fnam']):
            raise IOError('{}: error, no such file >>> {}'.format(self.proc_name,self.values['inp_fnam']))
        if not os.path.exists(self.values['obs_fnam']):
            raise IOError('{}: error, no such file >>> {}'.format(self.proc_name,self.values['obs_fnam']))
        if not os.path.exists(self.values['gcp_fnam']):
            raise IOError('{}: error, no such file >>> {}'.format(self.proc_name,self.values['gcp_fnam']))
        wrk_dir = os.path.join(self.drone_analysis,self.current_block,self.current_date,self.proc_name)
        if not os.path.exists(wrk_dir):
            os.makedirs(wrk_dir)
        if not os.path.isdir(wrk_dir):
            raise ValueError('{}: error, no such folder >>> {}'.format(self.proc_name,wrk_dir))

        orders = {'0th':0,'1st':1,'2nd':2,'3rd':3}
        command = self.python_path
        command += ' {}'.format(os.path.join(self.scr_dir,'read_survey_xls.py'))
        command += ' --inp_fnam {}'.format(self.values['obs_fnam'])
        command += ' --out_fnam {}'.format(self.values[''])
        command += ' --sheet {}'.format(self.values['i_sheet'])
        command += ' --epsg {}'.format(self.values[''])
        command += ' --geocor_fnam {}'.format(self.values['gcp_fnam'])
        command += ' --geocor_geotiff {}'.format(self.values[''])
        command += ' --geocor_npoly {}'.format(orders[self.values['geocor_order']])
        command += ' --optfile {}'.format(os.path.join(wrk_dir,'temp.dat'))



"""
read_survey_xls.py -I "../220508/from_2022_2Feb_to_2022_4Apr/15/CIHEA - 15 (2022).xls" -O 15_2022_03Mar_04.csv -g /home/naohiro/Work/Drone/220316/orthomosaic/ndvi_rms_repeat/P4M_RTK_15_20220304_resized_geocor.dat -G /home/naohiro/Work/Drone/220316/orthomosaic/P4M_RTK_15_20220304_resized.tif -n 3

read_survey_xls.py -I "../220508/from_2022_2Feb_to_2022_4Apr/11B/CIHEA - 11 B (2022).xls" -O 11B_2022_03Mar_01.csv -g /home/naohiro/Work/Drone/220316/orthomosaic/ndvi_rms_repeat/P4M_RTK_11b_20220301_resized_geocor.dat -G /home/naohiro/Work/Drone/220316/orthomosaic/P4M_RTK_11b_20220301_resized.tif -n 3

for target in ['15_2022_03Mar_04','11B_2022_03Mar_01']:
    m = re.search('([^_]+)_([^_]+)_(\d+)[^_]+_([^_]+)',target)
    if not m:
        raise ValueError('Error >>> '+target)
    block = m.group(1)
    year = int(m.group(2))
    month = int(m.group(3))
    day = int(m.group(4))
    date = datetime(year,month,day)
    call('drone_subset.py -I /home/naohiro/Work/Drone/220316/orthomosaic/ndvi_rms_repeat/P4M_RTK_{}_{:%Y%m%d}_geocor.tif -O {}.tif -g {}.csv -dNi -G 1 -S 30'.format(block.lower(),date,target,target),shell=True)
    call('drone_calc_rr.py -I {}_plot1.tif --data_min 10 -d -n  -p Lrg -p Nr -z 0 -Z 20 -s 5 -Z 5'.format(target),shell=True)
    call('drone_calc_rr.py -I {}_plot2.tif --data_min 10 -d -n  -p Lrg -p Nr -z 0 -Z 20 -s 5 -Z 5'.format(target),shell=True)
    call('drone_calc_rr.py -I {}_plot3.tif --data_min 10 -d -n  -p Lrg -p Nr -z 0 -Z 20 -s 5 -Z 5'.format(target),shell=True)
    call('drone_extract_points.py -I {}.tif -g {}.csv -dn -z 0 -Z 0.3 -s 0.1'.format(target,target),shell=True)
        return
"""
