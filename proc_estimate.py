from run_estimate import Estimate

proc_estimate = Estimate()
proc_estimate.proc_name = 'estimate'
proc_estimate.proc_title = 'Estimate Damage'
proc_estimate.pnams.append('inp_fnam')
proc_estimate.pnams.append('pv_fnam')
proc_estimate.pnams.append('pv_number')
proc_estimate.pnams.append('pm_fnam')
proc_estimate.pnams.append('pm_number')
proc_estimate.pnams.append('digitize')
proc_estimate.pnams.append('y_params')
proc_estimate.pnams.append('score_max')
proc_estimate.pnams.append('score_step')
proc_estimate.pnams.append('gis_fnam')
proc_estimate.pnams.append('buffer')
proc_estimate.pnams.append('region_size')
proc_estimate.params['inp_fnam'] = 'Input File'
proc_estimate.params['pv_fnam'] = 'Point-value Formula'
proc_estimate.params['pv_number'] = 'Point-value Formula Number'
proc_estimate.params['pm_fnam'] = 'Plot-mean Formula'
proc_estimate.params['pm_number'] = 'Plot-mean Formula Number'
proc_estimate.params['digitize'] = 'Digitize Score'
proc_estimate.params['y_params'] = 'Output Variable'
proc_estimate.params['score_max'] = 'Max Output Score'
proc_estimate.params['score_step'] = 'Score Step for Digitization'
proc_estimate.params['gis_fnam'] = 'Polygon File'
proc_estimate.params['buffer'] = 'Buffer Radius (m)'
proc_estimate.params['region_size'] = 'Average Region Size (m)'
proc_estimate.param_types['inp_fnam'] = 'string'
proc_estimate.param_types['pv_fnam'] = 'string'
proc_estimate.param_types['pv_number'] = 'int'
proc_estimate.param_types['pm_fnam'] = 'string'
proc_estimate.param_types['pm_number'] = 'int'
proc_estimate.param_types['digitize'] = 'boolean'
proc_estimate.param_types['y_params'] = 'boolean_list'
proc_estimate.param_types['score_max'] = 'int_list'
proc_estimate.param_types['score_step'] = 'int_list'
proc_estimate.param_types['gis_fnam'] = 'string'
proc_estimate.param_types['buffer'] = 'float'
proc_estimate.param_types['region_size'] = 'float'
proc_estimate.param_range['pv_number'] = (1,10000)
proc_estimate.param_range['pm_number'] = (1,10000)
proc_estimate.param_range['score_max'] = (1,65535)
proc_estimate.param_range['score_step'] = (1,65535)
proc_estimate.param_range['buffer'] = (0.0,10.0e3)
proc_estimate.param_range['region_size'] = (0.0,1.0e3)
proc_estimate.defaults['inp_fnam'] = 'input.tif'
proc_estimate.defaults['pv_fnam'] = 'pv_formula.csv'
proc_estimate.defaults['pv_number'] = 1
proc_estimate.defaults['pm_fnam'] = 'pm_formula.csv'
proc_estimate.defaults['pm_number'] = 1
proc_estimate.defaults['digitize'] = True
proc_estimate.defaults['y_params'] = [True,False,False,False,False,False]
proc_estimate.defaults['score_max'] = [9,9,1,1,1,9]
proc_estimate.defaults['score_step'] = [2,2,1,1,1,2]
proc_estimate.defaults['gis_fnam'] = 'All_area_polygon_20210914.shp'
proc_estimate.defaults['buffer'] = 1.0
proc_estimate.defaults['region_size'] = 1.0
proc_estimate.list_sizes['y_params'] = 6
proc_estimate.list_sizes['score_max'] = 6
proc_estimate.list_sizes['score_step'] = 6
proc_estimate.list_labels['y_params'] = ['BLB','Blast','Borer','Rat','Hopper','Drought']
proc_estimate.list_labels['score_max'] = ['BLB :',' Blast :',' Borer :',' Rat :',' Hopper :',' Drought :']
proc_estimate.list_labels['score_step'] = ['BLB :',' Blast :',' Borer :',' Rat :',' Hopper :',' Drought :']
proc_estimate.input_types['inp_fnam'] = 'ask_file'
proc_estimate.input_types['pv_fnam'] = 'ask_file'
proc_estimate.input_types['pv_number'] = 'box'
proc_estimate.input_types['pm_fnam'] = 'ask_file'
proc_estimate.input_types['pm_number'] = 'box'
proc_estimate.input_types['digitize'] = 'boolean'
proc_estimate.input_types['y_params'] = 'boolean_list'
proc_estimate.input_types['score_max'] = 'int_list'
proc_estimate.input_types['score_step'] = 'int_list'
proc_estimate.input_types['gis_fnam'] = 'ask_file'
proc_estimate.input_types['buffer'] = 'box'
proc_estimate.input_types['region_size'] = 'box'
proc_estimate.flag_check['inp_fnam'] = False
proc_estimate.depend_proc['inp_fnam'] = ['indices']
proc_estimate.expected['inp_fnam'] = 'indices.tif'
proc_estimate.expected['pv_fnam'] = '*.csv'
proc_estimate.expected['pm_fnam'] = '*.csv'
proc_estimate.expected['gis_fnam'] = '*.shp'
for pnam in proc_estimate.pnams:
    proc_estimate.values[pnam] = proc_estimate.defaults[pnam]
proc_estimate.left_frame_width = 210
proc_estimate.middle_left_frame_width = 1000
