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
        command += ' --dst_geotiff {}'.format(os.path.join(wrk_dir,))
        command += ' --param {}'.format()
        command += ' --norm_band'.format()
        command += ' --rgi_red_band '.format()
        command += ' --data_min="{}"'.format()
        command += ' --data_max="{}"'.format()

#python drone_calc_indices.py -I 15_2022_03Mar_04_plot1.tif -d -n
#python drone_calc_indices.py -I 15_2022_03Mar_04_plot2.tif -d -n
#python drone_calc_indices.py -I 15_2022_03Mar_04_plot3.tif -d -n

        return
