import numpy as np
from proc_class import Process

proc_indices = Process()
proc_indices.proc_name = 'indices'
proc_indices.proc_title = 'Calculate Indices'
proc_indices.pnams.append('inp_fnam')
proc_indices.pnams.append('out_params')
proc_indices.pnams.append('norm_bands')
proc_indices.pnams.append('rgi_red_band')
proc_indices.pnams.append('data_range')
proc_indices.params['inp_fnam'] = 'Input File'
proc_indices.params['out_params'] = 'Output Parameters'
proc_indices.params['norm_bands'] = 'Bands for Normalization'
proc_indices.params['rgi_red_band'] = 'Band for RGI'
proc_indices.params['data_range'] = 'DN Range'
proc_indices.param_types['inp_fnam'] = 'string'
proc_indices.param_types['out_params'] = 'boolean_list'
proc_indices.param_types['norm_bands'] = 'boolean_list'
proc_indices.param_types['rgi_red_band'] = 'string'
proc_indices.param_types['data_range'] = 'float_list'
proc_indices.param_range['data_range'] = (-1.0e50,1.0e50)
proc_indices.defaults['inp_fnam'] = 'input.tif'
proc_indices.defaults['out_params'] = [False,False,False,False,False,True,True,True,True,True,True,True,False,True]
proc_indices.defaults['norm_bands'] = [True,True,True,True,True]
proc_indices.defaults['rgi_red_band'] = 'e'
proc_indices.defaults['data_range'] = [np.nan,np.nan]
proc_indices.list_sizes['out_params'] = 14
proc_indices.list_sizes['norm_bands'] = 5
proc_indices.list_sizes['rgi_red_band'] = 5
proc_indices.list_sizes['data_range'] = 2
proc_indices.list_labels['out_params'] = ['b','g','r','e','n','Nb','Ng','Nr','Ne','Nn','NDVI','GNDVI','RGI','NGRI']
proc_indices.list_labels['norm_bands'] = ['b','g','r','e','n']
proc_indices.list_labels['rgi_red_band'] = ['b','g','r','e','n']
proc_indices.list_labels['data_range'] = ['Min :',' Max :']
proc_indices.input_types['inp_fnam'] = 'ask_file'
proc_indices.input_types['out_params'] = 'boolean_list'
proc_indices.input_types['norm_bands'] = 'boolean_list'
proc_indices.input_types['rgi_red_band'] = 'string_select'
proc_indices.input_types['data_range'] = 'float_list'
proc_indices.flag_check['inp_fnam'] = False
for pnam in proc_indices.pnams:
    proc_indices.values[pnam] = proc_indices.defaults[pnam]
proc_indices.middle_left_frame_width = 1000
