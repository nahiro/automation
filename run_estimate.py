from proc_class import Process

class Estimate(Process):

    def run(self):
        # Start process
        super().run()

        # Check files
        if not os.path.exists(self.values['gis_fnam']):
            raise IOError('{}: error, no such file >>> {}'.format(self.proc_name,self.values['gis_fnam']))
        if not os.path.exists(self.values['ref_fnam']):
            raise IOError('{}: error, no such file >>> {}'.format(self.proc_name,self.values['ref_fnam']))
        if not os.path.exists(self.values['trg_fnam']):
            raise IOError('{}: error, no such file >>> {}'.format(self.proc_name,self.values['trg_fnam']))
        ref_bnam,ref_enam = os.path.splitext(os.path.basename(self.values['ref_fnam']))
        trg_bnam = '{}_{}'.format(self.current_block,self.current_date)
        wrk_dir = os.path.join(self.drone_analysis,self.current_block,self.current_date,self.proc_name)
        if not os.path.exists(wrk_dir):
            os.makedirs(wrk_dir)
        if not os.path.isdir(wrk_dir):
            raise ValueError('{}: error, no such folder >>> {}'.format(self.proc_name,wrk_dir))

        #drone_score_estimate.py -I P4M_RTK_11b_20220301_geocor_indices_rebin.tif -i drone_score_fit.csv -d
        # Finish process
        sys.stderr.write('Finished process {}.\n\n'.format(self.proc_name))
        sys.stderr.flush()
        return
