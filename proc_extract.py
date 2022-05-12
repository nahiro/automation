from proc_class import Process

proc_extract = Process()
proc_extract.proc_name = 'extract'
proc_extract.proc_title = 'Extract Indices'
proc_extract.pnams.append('inp_fnams')
proc_extract.pnams.append('gps_fnam')
proc_extract.pnams.append('region_size')
proc_extract.params['inp_fnams'] = 'Input Files'
proc_extract.params['gps_fnam'] = 'Point File'
proc_extract.params['region_size'] = 'Extract Region Radius (m)'
proc_extract.param_types['inp_fnams'] = 'string'
proc_extract.param_types['gps_fnam'] = 'string'
proc_extract.param_types['region_size'] = 'double_list'
proc_extract.param_range['region_size'] = (0.0,1.0e3)
proc_extract.defaults['inp_fnams'] = 'input.tif'
proc_extract.defaults['gps_fnam'] = 'gps.csv'
proc_extract.defaults['region_size'] = [0.2,0.5]
proc_extract.list_sizes['region_size'] = 2
proc_extract.list_labels['region_size'] = ['Inner :',' Outer :']
proc_extract.input_types['inp_fnams'] = 'ask_files'
proc_extract.input_types['gps_fnam'] = 'ask_file'
proc_extract.input_types['region_size'] = 'double_list'
for pnam in proc_extract.pnams:
    proc_extract.values[pnam] = proc_extract.defaults[pnam]
proc_extract.middle_left_frame_width = 450
