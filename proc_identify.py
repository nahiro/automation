from proc_class import Process

proc_identify = Process()
proc_identify.proc_name = 'identify'
proc_identify.proc_title = 'Identify Points'
proc_identify.pnams.append('inp_fnam')
proc_identify.pnams.append('gcp_fnam')
proc_identify.pnams.append('geocor_order')
proc_identify.params['inp_fnam'] = 'Input File'
proc_identify.params['gcp_fnam'] = 'GCP File'
proc_identify.params['geocor_order'] = 'Order of Geom. Correction'
proc_identify.param_types['inp_fnam'] = 'string'
proc_identify.param_types['gcp_fnam'] = 'string'
proc_identify.param_types['geocor_order'] = 'int_select'
proc_identify.defaults['inp_fnam'] = 'input.xls'
proc_identify.defaults['gcp_fnam'] = 'gcp.dat'
proc_identify.defaults['geocor_order'] = 2
proc_identify.list_sizes['geocor_order'] = 4
proc_identify.list_labels['geocor_order'] = [0,1,2,3]
proc_identify.input_types['inp_fnam'] = 'ask_file'
proc_identify.input_types['gcp_fnam'] = 'ask_file'
proc_identify.input_types['geocor_order'] = 'int_select'
for pnam in proc_identify.pnams:
    proc_identify.values[pnam] = proc_identify.defaults[pnam]
