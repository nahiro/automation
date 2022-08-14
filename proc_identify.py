import numpy as np
from run_identify import Identify

proc_identify = Identify()
proc_identify.proc_name = 'identify'
proc_identify.proc_title = 'Identify Points'
proc_identify.pnams.append('inp_fnam')
proc_identify.pnams.append('gcp_fnam')
proc_identify.pnams.append('geocor_order')
proc_identify.pnams.append('epsg')
proc_identify.pnams.append('obs_fnam')
proc_identify.pnams.append('i_sheet')
proc_identify.pnams.append('buffer')
proc_identify.pnams.append('bunch_nmin')
proc_identify.pnams.append('bunch_rmax')
proc_identify.pnams.append('bunch_emax')
proc_identify.pnams.append('point_nmin')
proc_identify.pnams.append('point_rmax')
proc_identify.pnams.append('point_dmax')
proc_identify.pnams.append('point_area')
proc_identify.pnams.append('criteria')
proc_identify.pnams.append('rr_param')
proc_identify.pnams.append('rthr')
proc_identify.pnams.append('sthr')
proc_identify.pnams.append('data_range')
proc_identify.pnams.append('neighbor_size')
proc_identify.pnams.append('assign_fnam')
proc_identify.pnams.append('assign_plot1')
proc_identify.pnams.append('assign_plot2')
proc_identify.pnams.append('assign_plot3')
proc_identify.pnams.append('ignore_error')
proc_identify.params['inp_fnam'] = 'Image after Geom. Correction'
proc_identify.params['gcp_fnam'] = 'GCP File (utm2utm)'
proc_identify.params['geocor_order'] = 'Order of Geom. Correction'
proc_identify.params['epsg'] = 'EPSG'
proc_identify.params['obs_fnam'] = 'Observation File'
proc_identify.params['i_sheet'] = 'Observation Sheet Number'
proc_identify.params['buffer'] = 'Buffer Radius (m)'
proc_identify.params['bunch_nmin'] = 'Min Bunch Number in a Plot'
proc_identify.params['bunch_rmax'] = 'Max GPS Distance btw Bunch (m)'
proc_identify.params['bunch_emax'] = 'Max GPS Distance from Line (\u03C3)'
proc_identify.params['point_nmin'] = 'Min Point Number in a Plot'
proc_identify.params['point_rmax'] = 'Max Distance within Point (m)'
proc_identify.params['point_dmax'] = 'Max Distance from Line (m)'
proc_identify.params['point_area'] = 'Point Area (m\u00B2)'
proc_identify.params['criteria'] = 'Selection Criteria'
proc_identify.params['rr_param'] = 'Parameter'
proc_identify.params['rthr'] = 'Redness Ratio Threshold'
proc_identify.params['sthr'] = 'Signal Ratio Threshold'
proc_identify.params['data_range'] = 'DN Range'
proc_identify.params['neighbor_size'] = 'Neighborhood Size (m)'
proc_identify.params['assign_fnam'] = 'Assignment File'
proc_identify.params['assign_plot1'] = 'Assignment for Plot1'
proc_identify.params['assign_plot2'] = 'Assignment for Plot2'
proc_identify.params['assign_plot3'] = 'Assignment for Plot3'
proc_identify.params['ignore_error'] = 'Ignore Error'
proc_identify.param_types['inp_fnam'] = 'string'
proc_identify.param_types['gcp_fnam'] = 'string'
proc_identify.param_types['geocor_order'] = 'string_select'
proc_identify.param_types['epsg'] = 'int'
proc_identify.param_types['obs_fnam'] = 'string'
proc_identify.param_types['i_sheet'] = 'int'
proc_identify.param_types['buffer'] = 'float'
proc_identify.param_types['bunch_nmin'] = 'int'
proc_identify.param_types['bunch_rmax'] = 'float'
proc_identify.param_types['bunch_emax'] = 'float'
proc_identify.param_types['point_nmin'] = 'int'
proc_identify.param_types['point_rmax'] = 'float'
proc_identify.param_types['point_dmax'] = 'float_list'
proc_identify.param_types['point_area'] = 'float_list'
proc_identify.param_types['criteria'] = 'string_select'
proc_identify.param_types['rr_param'] = 'string_select_list'
proc_identify.param_types['rthr'] = 'float_list'
proc_identify.param_types['sthr'] = 'float'
proc_identify.param_types['data_range'] = 'float_list'
proc_identify.param_types['neighbor_size'] = 'float_list'
proc_identify.param_types['assign_fnam'] = 'string'
proc_identify.param_types['assign_plot1'] = 'int_list'
proc_identify.param_types['assign_plot2'] = 'int_list'
proc_identify.param_types['assign_plot3'] = 'int_list'
proc_identify.param_types['ignore_error'] = 'boolean'
proc_identify.param_range['i_sheet'] = (1,100)
proc_identify.param_range['epsg'] = (1,100000)
proc_identify.param_range['buffer'] = (0.0,10.0e3)
proc_identify.param_range['bunch_nmin'] = (1,1000)
proc_identify.param_range['bunch_rmax'] = (0.0,100.0)
proc_identify.param_range['bunch_emax'] = (0.0,100.0)
proc_identify.param_range['point_nmin'] = (1,1000)
proc_identify.param_range['point_rmax'] = (0.0,100.0)
proc_identify.param_range['point_dmax'] = (0.0,100.0)
proc_identify.param_range['point_area'] = (0.0,1.0e50)
proc_identify.param_range['rthr'] = (-1.0e50,1.0e50)
proc_identify.param_range['sthr'] = (-1.0e50,1.0e50)
proc_identify.param_range['data_range'] = (-1.0e50,1.0e50)
proc_identify.param_range['neighbor_size'] = (0.0,1.0e50)
proc_identify.param_range['assign_plot1'] = (-1,30)
proc_identify.param_range['assign_plot2'] = (-1,30)
proc_identify.param_range['assign_plot3'] = (-1,30)
proc_identify.defaults['inp_fnam'] = 'input.tif'
proc_identify.defaults['gcp_fnam'] = 'gcp.dat'
proc_identify.defaults['geocor_order'] = '2nd'
proc_identify.defaults['epsg'] = 32748
proc_identify.defaults['obs_fnam'] = 'observation.xls'
proc_identify.defaults['i_sheet'] = 1
proc_identify.defaults['buffer'] = 10.0
proc_identify.defaults['bunch_nmin'] = 5
proc_identify.defaults['bunch_rmax'] = 10.0
proc_identify.defaults['bunch_emax'] = 2.0
proc_identify.defaults['point_nmin'] = 5
proc_identify.defaults['point_rmax'] = 1.0
proc_identify.defaults['point_dmax'] = [1.0,0.5]
proc_identify.defaults['point_area'] = [0.015,0.105,0.05]
proc_identify.defaults['criteria'] = 'Distance from Line'
proc_identify.defaults['rr_param'] = ['Lrg','S/N']
proc_identify.defaults['rthr'] = [0.0,1.0,0.01]
proc_identify.defaults['sthr'] = 1.0
proc_identify.defaults['data_range'] = [np.nan,np.nan]
proc_identify.defaults['neighbor_size'] = [0.78,0.95]
proc_identify.defaults['assign_fnam'] = ''
proc_identify.defaults['assign_plot1'] = [0,0,0,0,0,0,0,0,0,0]
proc_identify.defaults['assign_plot2'] = [0,0,0,0,0,0,0,0,0,0]
proc_identify.defaults['assign_plot3'] = [0,0,0,0,0,0,0,0,0,0]
proc_identify.defaults['ignore_error'] = False
proc_identify.list_sizes['geocor_order'] = 4
proc_identify.list_sizes['point_dmax'] = 2
proc_identify.list_sizes['point_area'] = 3
proc_identify.list_sizes['criteria'] = 2
proc_identify.list_sizes['rr_param'] = 2
proc_identify.list_sizes['rthr'] = 3
proc_identify.list_sizes['data_range'] = 2
proc_identify.list_sizes['neighbor_size'] = 2
proc_identify.list_sizes['assign_plot1'] = 10
proc_identify.list_sizes['assign_plot2'] = 10
proc_identify.list_sizes['assign_plot3'] = 10
proc_identify.list_labels['geocor_order'] = ['0th','1st','2nd','3rd']
proc_identify.list_labels['point_dmax'] = ['Fit :',' Select :']
proc_identify.list_labels['point_area'] = ['Min :',' Max :',' Avg :']
proc_identify.list_labels['criteria'] = ['Distance from Line','Point Area']
proc_identify.list_labels['rr_param'] = [('Redness :',['Grg','Lrg','Lb','Lg','Lr','Le','Ln','rg','b','g','r','e','n']),(' Signal :',['S/N','S/B'])]
proc_identify.list_labels['rthr'] = ['Min :',' Max :',' Step :']
proc_identify.list_labels['data_range'] = ['Min :',' Max :']
proc_identify.list_labels['neighbor_size'] = ['Inner :',' Outer :']
proc_identify.list_labels['assign_plot1'] = ['  1 :','   2 :','   3 :','   4 :','   5 :','   6 :','   7 :','   8 :','   9 :',' 10 :']
proc_identify.list_labels['assign_plot2'] = ['11 :',' 12 :',' 13 :',' 14 :',' 15 :',' 16 :',' 17 :',' 18 :',' 19 :',' 20 :']
proc_identify.list_labels['assign_plot3'] = ['21 :',' 22 :',' 23 :',' 24 :',' 25 :',' 26 :',' 27 :',' 28 :',' 29 :',' 30 :']
proc_identify.input_types['inp_fnam'] = 'ask_file'
proc_identify.input_types['gcp_fnam'] = 'ask_file'
proc_identify.input_types['geocor_order'] = 'string_select'
proc_identify.input_types['epsg'] = 'box'
proc_identify.input_types['obs_fnam'] = 'ask_file'
proc_identify.input_types['i_sheet'] = 'box'
proc_identify.input_types['buffer'] = 'box'
proc_identify.input_types['bunch_nmin'] = 'box'
proc_identify.input_types['bunch_rmax'] = 'box'
proc_identify.input_types['bunch_emax'] = 'box'
proc_identify.input_types['point_nmin'] = 'box'
proc_identify.input_types['point_rmax'] = 'box'
proc_identify.input_types['point_dmax'] = 'float_list'
proc_identify.input_types['point_area'] = 'float_list'
proc_identify.input_types['criteria'] = 'string_select'
proc_identify.input_types['rr_param'] = 'string_select_list'
proc_identify.input_types['rthr'] = 'float_list'
proc_identify.input_types['sthr'] = 'box'
proc_identify.input_types['data_range'] = 'float_list'
proc_identify.input_types['neighbor_size'] = 'float_list'
proc_identify.input_types['assign_fnam'] = 'ask_file'
proc_identify.input_types['assign_plot1'] = 'int_list'
proc_identify.input_types['assign_plot2'] = 'int_list'
proc_identify.input_types['assign_plot3'] = 'int_list'
proc_identify.input_types['ignore_error'] = 'boolean'
proc_identify.flag_check['inp_fnam'] = False
proc_identify.flag_check['gcp_fnam'] = False
proc_identify.depend_proc['inp_fnam'] = ['geocor']
proc_identify.depend_proc['gcp_fnam'] = ['geocor']
proc_identify.expected['inp_fnam'] = '*.tif'
proc_identify.expected['gcp_fnam'] = 'utm2utm.dat'
proc_identify.expected['obs_fnam'] = '*.xls'
for pnam in proc_identify.pnams:
    proc_identify.values[pnam] = proc_identify.defaults[pnam]
proc_identify.left_frame_width = 250
proc_identify.middle_left_frame_width = 1000
