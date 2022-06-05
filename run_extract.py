from proc_class import Process

class Extract(Process):

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
        wrk_dir = os.path.join(self.drone_analysis,self.current_block,self.current_date,self.proc_name)
        if not os.path.exists(wrk_dir):
            os.makedirs(wrk_dir)
        if not os.path.isdir(wrk_dir):
            raise ValueError('{}: error, no such folder >>> {}'.format(self.proc_name,wrk_dir))

        # Read data
        trg_bnam = '{}_{}'.format(self.current_block,self.current_date)
        command = self.python_path
        command += ' {}'.format(os.path.join(self.scr_dir,'read_survey_xls.py'))
        command += ' --inp_fnam {}'.format(self.values['obs_fnam'])
        command += ' --sheet {}'.format(self.values['i_sheet'])
        command += ' --ref_fnam {}'.format(self.values['gps_fnam'])
        command += ' --epsg {}'.format(self.values['epsg'])
        command += ' --out_fnam {}'.format(os.path.join(wrk_dir,'{}_observation.csv'.format(trg_bnam)))
        sys.stderr.write('\nRead observation data\n')
        sys.stderr.write(command+'\n')
        sys.stderr.flush()
        call(command,shell=True)
        df = pd.read_csv(os.path.join(wrk_dir,'{}_observation.csv'.format(trg_bnam)),comment='#')
        df.columns = df.columns.str.strip()
        plot_bunch = df['PlotPaddy'].values
        plots = np.unique(plot_bunch)

        # Extract indices
        command = self.python_path
        command += ' {}'.format(os.path.join(self.scr_dir,'rebin_gtiff.py'))


        #call('drone_extract_values.py -I {}_plot1_indices.tif -I {}_plot2_indices.tif -I {}_plot3_indices.tif -g {}_extract.csv'.format(target,target,target,target),shell=True)

        # Finish process
        sys.stderr.write('Finished process {}.\n\n'.format(self.proc_name))
        sys.stderr.flush()
        return
