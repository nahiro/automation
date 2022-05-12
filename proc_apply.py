from proc_class import Process

proc_apply = Process()
proc_apply.proc_name = 'apply'
proc_apply.proc_title = 'Estimate Damage'
proc_apply.pnams.append('inp_fnam')
proc_apply.pnams.append('score_fnam')
proc_apply.pnams.append('score_number')
proc_apply.pnams.append('intensity_fnam')
proc_apply.pnams.append('intensity_number')
proc_apply.pnams.append('y_params')
proc_apply.pnams.append('gis_fnam')
proc_apply.pnams.append('buffer')
proc_apply.pnams.append('region_size')
proc_apply.params['inp_fnam'] = 'Input File'
proc_apply.params['score_fnam'] = 'Score Formula File'
proc_apply.params['score_number'] = 'Score Formula Number'
proc_apply.params['intensity_fnam'] = 'Intensity Formula File'
proc_apply.params['intensity_number'] = 'Intensity Formula Number'
proc_apply.params['y_params'] = 'Output Variable'
proc_apply.params['gis_fnam'] = 'Polygon File'
proc_apply.params['buffer'] = 'Buffer Radius (m)'
proc_apply.params['region_size'] = 'Average Region Size (m)'
proc_apply.param_types['inp_fnam'] = 'string'
proc_apply.param_types['score_fnam'] = 'string'
proc_apply.param_types['score_number'] = 'int'
proc_apply.param_types['intensity_fnam'] = 'string'
proc_apply.param_types['intensity_number'] = 'int'
proc_apply.param_types['y_params'] = 'boolean_list'
proc_apply.param_types['gis_fnam'] = 'string'
proc_apply.param_types['buffer'] = 'double'
proc_apply.param_types['region_size'] = 'double'
proc_apply.param_range['score_number'] = (1,10000)
proc_apply.param_range['intensity_number'] = (1,10000)
proc_apply.param_range['buffer'] = (0.0,10.0e3)
proc_apply.param_range['region_size'] = (0.0,1.0e3)
proc_apply.defaults['inp_fnam'] = 'input.tif'
proc_apply.defaults['score_fnam'] = 'score_formula.csv'
proc_apply.defaults['score_number'] = 1
proc_apply.defaults['intensity_fnam'] = 'intensity_formula.csv'
proc_apply.defaults['intensity_number'] = 1
proc_apply.defaults['y_params'] = [True,False,False,False,False,False]
proc_apply.defaults['gis_fnam'] = 'All_area_polygon_20210914.shp'
proc_apply.defaults['buffer'] = 1.0
proc_apply.defaults['region_size'] = 1.0
proc_apply.list_sizes['y_params'] = 6
proc_apply.list_labels['y_params'] = ['BLB','Blast','StemBorer','Rat','Hopper','Drought']
proc_apply.input_types['inp_fnam'] = 'ask_file'
proc_apply.input_types['score_fnam'] = 'ask_file'
proc_apply.input_types['score_number'] = 'box'
proc_apply.input_types['intensity_fnam'] = 'ask_file'
proc_apply.input_types['intensity_number'] = 'box'
proc_apply.input_types['y_params'] = 'boolean_list'
proc_apply.input_types['gis_fnam'] = 'ask_file'
proc_apply.input_types['buffer'] = 'box'
proc_apply.input_types['region_size'] = 'box'
for pnam in proc_apply.pnams:
    proc_apply.values[pnam] = proc_apply.defaults[pnam]
proc_apply.middle_left_frame_width = 650
