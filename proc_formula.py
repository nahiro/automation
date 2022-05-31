import numpy as np
from proc_class import Process

proc_formula = Process()
proc_formula.proc_name = 'formula'
proc_formula.proc_title = 'Make Formula'
proc_formula.pnams.append('inp_fnams')
proc_formula.pnams.append('age_range')
proc_formula.pnams.append('nx')
proc_formula.pnams.append('x_params')
proc_formula.pnams.append('q_params')
proc_formula.pnams.append('y_params')
proc_formula.pnams.append('smax')
proc_formula.pnams.append('ythr')
proc_formula.pnams.append('yfac1')
proc_formula.pnams.append('yfac2')
proc_formula.pnams.append('yfac3')
proc_formula.pnams.append('yfac4')
proc_formula.pnams.append('yfac5')
proc_formula.pnams.append('yfac6')
proc_formula.pnams.append('criteria')
proc_formula.pnams.append('vmax')
proc_formula.pnams.append('n_cros')
proc_formula.pnams.append('mmax')
proc_formula.params['inp_fnams'] = 'Input Files'
proc_formula.params['age_range'] = 'Age Range (day)'
proc_formula.params['nx'] = 'Explanatory Variable Number'
proc_formula.params['x_params'] = 'Explanatory Variable Candidate'
proc_formula.params['q_params'] = 'Identification Parameter'
proc_formula.params['y_params'] = 'Objective Variable'
proc_formula.params['smax'] = 'Max Input Score'
proc_formula.params['ythr'] = 'Threshold for Training Data'
proc_formula.params['yfac1'] = 'Conversion Factor for BLB'
proc_formula.params['yfac2'] = 'Conversion Factor for Blast'
proc_formula.params['yfac3'] = 'Conversion Factor for StemBorer'
proc_formula.params['yfac4'] = 'Conversion Factor for Rat'
proc_formula.params['yfac5'] = 'Conversion Factor for Hopper'
proc_formula.params['yfac6'] = 'Conversion Factor for Drought'
proc_formula.params['criteria'] = 'Selection Criteria'
proc_formula.params['vmax'] = 'Max Variance Inflation Factor'
proc_formula.params['n_cros'] = 'Cross Validation Number'
proc_formula.params['mmax'] = 'Max Formula Number'
proc_formula.param_types['inp_fnams'] = 'string'
proc_formula.param_types['age_range'] = 'double_list'
proc_formula.param_types['nx'] = 'int_select_list'
proc_formula.param_types['x_params'] = 'boolean_list'
proc_formula.param_types['q_params'] = 'boolean_list'
proc_formula.param_types['y_params'] = 'boolean_list'
proc_formula.param_types['smax'] = 'int_list'
proc_formula.param_types['ythr'] = 'double_list'
proc_formula.param_types['yfac1'] = 'double_list'
proc_formula.param_types['yfac2'] = 'double_list'
proc_formula.param_types['yfac3'] = 'double_list'
proc_formula.param_types['yfac4'] = 'double_list'
proc_formula.param_types['yfac5'] = 'double_list'
proc_formula.param_types['yfac6'] = 'double_list'
proc_formula.param_types['criteria'] = 'string_select'
proc_formula.param_types['vmax'] = 'double'
proc_formula.param_types['n_cros'] = 'int'
proc_formula.param_types['mmax'] = 'int'
#proc_formula.param_range['nx'] = (1,14)
proc_formula.param_range['age_range'] = (-1000.0,1000.0)
proc_formula.param_range['smax'] = (1,65535)
proc_formula.param_range['ythr'] = (0.0,1.0e3)
proc_formula.param_range['yfac1'] = (0.0,1.0e5)
proc_formula.param_range['yfac2'] = (0.0,1.0e5)
proc_formula.param_range['yfac3'] = (0.0,1.0e5)
proc_formula.param_range['yfac4'] = (0.0,1.0e5)
proc_formula.param_range['yfac5'] = (0.0,1.0e5)
proc_formula.param_range['yfac6'] = (0.0,1.0e5)
proc_formula.param_range['vmax'] = (0.0,1.0e5)
proc_formula.param_range['n_cros'] = (2,1000)
proc_formula.param_range['mmax'] = (1,1000)
proc_formula.defaults['inp_fnams'] = 'input.csv'
proc_formula.defaults['age_range'] = [-100.0,150.0]
proc_formula.defaults['nx'] = [1,2]
proc_formula.defaults['x_params'] = [False,False,False,False,False,True,True,True,True,True,True,True,False,True]
proc_formula.defaults['q_params'] = [True,True,True,True]
proc_formula.defaults['y_params'] = [True,False,False,False,False,False]
proc_formula.defaults['smax'] = [9,9,1,1,1,9]
proc_formula.defaults['ythr'] = [0.2,0.2,0.2,0.2,0.2,0.2]
proc_formula.defaults['yfac1'] = [1.0,np.nan,np.nan,np.nan,np.nan,np.nan]
proc_formula.defaults['yfac2'] = [np.nan,1.0,np.nan,np.nan,np.nan,np.nan]
proc_formula.defaults['yfac3'] = [np.nan,np.nan,1.0,np.nan,np.nan,np.nan]
proc_formula.defaults['yfac4'] = [np.nan,np.nan,np.nan,1.0,np.nan,np.nan]
proc_formula.defaults['yfac5'] = [np.nan,np.nan,np.nan,np.nan,1.0,np.nan]
proc_formula.defaults['yfac6'] = [np.nan,np.nan,np.nan,np.nan,np.nan,1.0]
proc_formula.defaults['criteria'] = 'RMSE_test'
proc_formula.defaults['vmax'] = 5.0
proc_formula.defaults['n_cros'] = 5
proc_formula.defaults['mmax'] = 3
proc_formula.list_sizes['age_range'] = 2
proc_formula.list_sizes['nx'] = 2
proc_formula.list_sizes['x_params'] = 14
proc_formula.list_sizes['q_params'] = 4
proc_formula.list_sizes['y_params'] = 6
proc_formula.list_sizes['smax'] = 6
proc_formula.list_sizes['ythr'] = 6
proc_formula.list_sizes['yfac1'] = 6
proc_formula.list_sizes['yfac2'] = 6
proc_formula.list_sizes['yfac3'] = 6
proc_formula.list_sizes['yfac4'] = 6
proc_formula.list_sizes['yfac5'] = 6
proc_formula.list_sizes['yfac6'] = 6
proc_formula.list_sizes['criteria'] = 7
proc_formula.list_labels['age_range'] = ['Min :',' Max :']
proc_formula.list_labels['nx'] = [('Min :',[1,2,3,4,5,6,7,8,9,10,11,12,13,14]),(' Max :',[1,2,3,4,5,6,7,8,9,10,11,12,13,14])]
proc_formula.list_labels['x_params'] = ['b','g','r','e','n','Nb','Ng','Nr','Ne','Nn','NDVI','GNDVI','RGI','NGRI']
proc_formula.list_labels['q_params'] = ['Location','PlotPaddy','PlantDate','Age']
proc_formula.list_labels['y_params'] = ['BLB','Blast','StemBorer','Rat','Hopper','Drought']
proc_formula.list_labels['smax'] = ['BLB :',' Blast :',' StemBorer :',' Rat :',' Hopper :',' Drought :']
proc_formula.list_labels['ythr'] = ['BLB :',' Blast :',' StemBorer :',' Rat :',' Hopper :',' Drought :']
proc_formula.list_labels['yfac1'] = ['','','','','','']
proc_formula.list_labels['yfac2'] = ['','','','','','']
proc_formula.list_labels['yfac3'] = ['','','','','','']
proc_formula.list_labels['yfac4'] = ['','','','','','']
proc_formula.list_labels['yfac5'] = ['','','','','','']
proc_formula.list_labels['yfac6'] = ['','','','','','']
proc_formula.list_labels['criteria'] = ['RMSE_test','R2_test','AIC_test','RMSE_train','R2_train','AIC_train','BIC_train']
proc_formula.input_types['inp_fnams'] = 'ask_files'
proc_formula.input_types['age_range'] = 'double_list'
proc_formula.input_types['nx'] = 'int_select_list'
proc_formula.input_types['x_params'] = 'boolean_list'
proc_formula.input_types['q_params'] = 'boolean_list'
proc_formula.input_types['y_params'] = 'boolean_list'
proc_formula.input_types['smax'] = 'int_list'
proc_formula.input_types['ythr'] = 'double_list'
proc_formula.input_types['yfac1'] = 'double_list'
proc_formula.input_types['yfac2'] = 'double_list'
proc_formula.input_types['yfac3'] = 'double_list'
proc_formula.input_types['yfac4'] = 'double_list'
proc_formula.input_types['yfac5'] = 'double_list'
proc_formula.input_types['yfac6'] = 'double_list'
proc_formula.input_types['criteria'] = 'string_select'
proc_formula.input_types['vmax'] = 'box'
proc_formula.input_types['n_cros'] = 'box'
proc_formula.input_types['mmax'] = 'box'
#proc_formula.flag_fill['x_params'] = True
#proc_formula.flag_fill['q_params'] = True
#proc_formula.flag_fill['y_params'] = True
for pnam in proc_formula.pnams:
    proc_formula.values[pnam] = proc_formula.defaults[pnam]
proc_formula.left_frame_width = 200
proc_formula.middle_left_frame_width = 1000
