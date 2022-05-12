from proc_class import Process

proc_identify = Process()
proc_identify.proc_name = 'identify'
proc_identify.proc_title = 'Identify Points'
proc_identify.pnams.append('inp_fnam')
proc_identify.pnams.append('i_sheet')
proc_identify.pnams.append('gcp_fnam')
proc_identify.pnams.append('geocor_order')
proc_identify.pnams.append('epsg')
proc_identify.pnams.append('buffer')
proc_identify.pnams.append('bunch_rmax')
proc_identify.pnams.append('bunch_emax')
proc_identify.pnams.append('bunch_nmin')
proc_identify.pnams.append('rr_param')
proc_identify.pnams.append('neighbor_size')
proc_identify.params['inp_fnam'] = 'Input File'
proc_identify.params['i_sheet'] = 'Input Sheet Number'
proc_identify.params['gcp_fnam'] = 'GCP File'
proc_identify.params['geocor_order'] = 'Order of Geom. Correction'
proc_identify.params['epsg'] = 'EPSG'
proc_identify.params['buffer'] = 'Buffer Radius'
proc_identify.params['bunch_rmax'] = 'Max Bunch Distance'
proc_identify.params['bunch_emax'] = 'Max Distance from Line'
proc_identify.params['bunch_nmin'] = 'Min Bunch# in a Plot'
proc_identify.params['rr_param'] = 'Parameter'
proc_identify.params['neighbor_size'] = 'Neighborhood Area Size'
proc_identify.param_types['inp_fnam'] = 'string'
proc_identify.param_types['i_sheet'] = 'int'
proc_identify.param_types['gcp_fnam'] = 'string'
proc_identify.param_types['geocor_order'] = 'int_select'
proc_identify.param_types['epsg'] = 'int'
proc_identify.param_types['buffer'] = 'double'
proc_identify.param_types['bunch_rmax'] = 'double'
proc_identify.param_types['bunch_emax'] = 'double'
proc_identify.param_types['bunch_nmin'] = 'int'
proc_identify.param_types['rr_param'] = 'string_select_list'
proc_identify.param_types['neighbor_size'] = 'int_list'
proc_identify.param_range['i_sheet'] = (1,100)
proc_identify.param_range['epsg'] = (1,100000)
proc_identify.param_range['buffer'] = (0.0,10.0e3)
proc_identify.param_range['bunch_rmax'] = (0.0,100.0)
proc_identify.param_range['bunch_emax'] = (0.0,100.0)
proc_identify.param_range['bunch_nmin'] = (1,1000)
proc_identify.param_range['neighbor_size'] = (1,10000)
proc_identify.defaults['inp_fnam'] = 'input.xls'
proc_identify.defaults['i_sheet'] = 1
proc_identify.defaults['gcp_fnam'] = 'gcp.dat'
proc_identify.defaults['geocor_order'] = 2
proc_identify.defaults['epsg'] = 32748
proc_identify.defaults['buffer'] = 5.0
proc_identify.defaults['bunch_rmax'] = 10.0
proc_identify.defaults['bunch_emax'] = 2.0
proc_identify.defaults['bunch_nmin'] = 5
proc_identify.defaults['rr_param'] = ['Lrg','S/N']
proc_identify.defaults['neighbor_size'] = [29,35]
proc_identify.list_sizes['geocor_order'] = 4
proc_identify.list_sizes['rr_param'] = 2
proc_identify.list_sizes['neighbor_size'] = 2
proc_identify.list_labels['geocor_order'] = [0,1,2,3]
proc_identify.list_labels['rr_param'] = [('Redness :',['Grg','Lrg','Lb','Lg','Lr','Le','Ln','rg','b','g','r','e','n']),(' Signal :',['S/N','S/B'])]
proc_identify.list_labels['neighbor_size'] = ['Inner :',' Outer :']
proc_identify.input_types['inp_fnam'] = 'ask_file'
proc_identify.input_types['i_sheet'] = 'box'
proc_identify.input_types['gcp_fnam'] = 'ask_file'
proc_identify.input_types['geocor_order'] = 'int_select'
proc_identify.input_types['epsg'] = 'box'
proc_identify.input_types['buffer'] = 'box'
proc_identify.input_types['bunch_rmax'] = 'box'
proc_identify.input_types['bunch_emax'] = 'box'
proc_identify.input_types['bunch_nmin'] = 'box'
proc_identify.input_types['rr_param'] = 'string_select_list'
proc_identify.input_types['neighbor_size'] = 'int_list'
for pnam in proc_identify.pnams:
    proc_identify.values[pnam] = proc_identify.defaults[pnam]
proc_identify.middle_left_frame_width = 450
