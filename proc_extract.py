from run_extract import Extract

proc_extract = Extract()
proc_extract.proc_name = 'extract'
proc_extract.proc_title = 'Extract Indices'
proc_extract.pnams.append('inp_fnam')
proc_extract.pnams.append('obs_fnam')
proc_extract.pnams.append('i_sheet')
proc_extract.pnams.append('gps_fnam')
proc_extract.pnams.append('region_size')
proc_extract.params['inp_fnam'] = 'Input File'
proc_extract.params['obs_fnam'] = 'Observation File'
proc_extract.params['i_sheet'] = 'Observation Sheet Number'
proc_extract.params['gps_fnam'] = 'Point File'
proc_extract.params['region_size'] = 'Extract Region Radius (m)'
proc_extract.param_types['inp_fnam'] = 'string'
proc_extract.param_types['obs_fnam'] = 'string'
proc_extract.param_types['i_sheet'] = 'int'
proc_extract.param_types['gps_fnam'] = 'string'
proc_extract.param_types['region_size'] = 'float_list'
proc_extract.param_range['i_sheet'] = (1,100)
proc_extract.param_range['region_size'] = (0.0,1.0e3)
proc_extract.defaults['inp_fnam'] = 'input.tif'
proc_extract.defaults['obs_fnam'] = 'observation.xls'
proc_extract.defaults['i_sheet'] = 1
proc_extract.defaults['gps_fnam'] = 'gps.csv'
proc_extract.defaults['region_size'] = [0.2,0.5]
proc_extract.list_sizes['region_size'] = 2
proc_extract.list_labels['region_size'] = ['Inner :',' Outer :']
proc_extract.input_types['inp_fnam'] = 'ask_file'
proc_extract.input_types['obs_fnam'] = 'ask_file'
proc_extract.input_types['i_sheet'] = 'box'
proc_extract.input_types['gps_fnam'] = 'ask_file'
proc_extract.input_types['region_size'] = 'float_list'
proc_extract.flag_check['inp_fnam'] = False
for pnam in proc_extract.pnams:
    proc_extract.values[pnam] = proc_extract.defaults[pnam]
proc_extract.middle_left_frame_width = 1000
