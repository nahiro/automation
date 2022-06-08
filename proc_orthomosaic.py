import os
import sys
import numpy as np
from run_orthomosaic import Orthomosaic

proc_orthomosaic = Orthomosaic()
proc_orthomosaic.proc_name = 'orthomosaic'
proc_orthomosaic.proc_title = 'Make Orthomosaic'
proc_orthomosaic.pnams.append('metashape_path')
proc_orthomosaic.pnams.append('inpdirs')
proc_orthomosaic.pnams.append('qmin')
proc_orthomosaic.pnams.append('xmp_flag')
proc_orthomosaic.pnams.append('calib_flag')
proc_orthomosaic.pnams.append('panel_fnam')
proc_orthomosaic.pnams.append('align_level')
proc_orthomosaic.pnams.append('preselect')
proc_orthomosaic.pnams.append('point_limit')
proc_orthomosaic.pnams.append('cam_flags')
proc_orthomosaic.pnams.append('optimize_flag')
proc_orthomosaic.pnams.append('cam_params')
proc_orthomosaic.pnams.append('depth_map')
proc_orthomosaic.pnams.append('epsg')
proc_orthomosaic.pnams.append('pixel_size')
proc_orthomosaic.pnams.append('output_type')
proc_orthomosaic.params['metashape_path'] = 'Metashape Path'
proc_orthomosaic.params['inpdirs'] = 'Input Folders'
proc_orthomosaic.params['qmin'] = 'Min Image Quality'
proc_orthomosaic.params['xmp_flag'] = 'Load XMP Meta Data'
proc_orthomosaic.params['calib_flag'] = 'Reflectance Calibration'
proc_orthomosaic.params['panel_fnam'] = 'Panel Reflectance File'
proc_orthomosaic.params['align_level'] = 'Alignment Accuracy'
proc_orthomosaic.params['preselect'] = 'Preselection'
proc_orthomosaic.params['point_limit'] = 'Point Limit'
proc_orthomosaic.params['cam_flags'] = 'Adaptive Fitting'
proc_orthomosaic.params['optimize_flag'] = 'Optimize Camera'
proc_orthomosaic.params['cam_params'] = 'Optimize Parameters'
proc_orthomosaic.params['depth_map'] = 'Depth Map'
proc_orthomosaic.params['epsg'] = 'EPSG'
proc_orthomosaic.params['pixel_size'] = 'Pixel Size (m)'
proc_orthomosaic.params['output_type'] = 'Output type'
proc_orthomosaic.param_types['metashape_path'] = 'string'
proc_orthomosaic.param_types['inpdirs'] = 'string'
proc_orthomosaic.param_types['qmin'] = 'float'
proc_orthomosaic.param_types['xmp_flag'] = 'boolean_list'
proc_orthomosaic.param_types['calib_flag'] = 'boolean_list'
proc_orthomosaic.param_types['panel_fnam'] = 'string'
proc_orthomosaic.param_types['align_level'] = 'string_select'
proc_orthomosaic.param_types['preselect'] = 'boolean_list'
proc_orthomosaic.param_types['point_limit'] = 'int_list'
proc_orthomosaic.param_types['cam_flags'] = 'boolean_list'
proc_orthomosaic.param_types['optimize_flag'] = 'boolean'
proc_orthomosaic.param_types['cam_params'] = 'boolean_list'
proc_orthomosaic.param_types['depth_map'] = 'string_select_list'
proc_orthomosaic.param_types['epsg'] = 'int'
proc_orthomosaic.param_types['pixel_size'] = 'float'
proc_orthomosaic.param_types['output_type'] = 'string_select'
proc_orthomosaic.param_range['qmin'] = (0.0,1.0)
proc_orthomosaic.param_range['point_limit'] = (1,1000000)
proc_orthomosaic.param_range['epsg'] = (1,100000)
proc_orthomosaic.param_range['pixel_size'] = (0.0,1.0e6)
proc_orthomosaic.defaults['metashape_path'] = os.path.normpath(os.path.join(os.environ.get('PROGRAMFILES'),'Agisoft/Metashape Pro/metashape.exe'))
proc_orthomosaic.defaults['inpdirs'] = 'input'
proc_orthomosaic.defaults['qmin'] = 0.5
proc_orthomosaic.defaults['xmp_flag'] = [True,True,True,True]
proc_orthomosaic.defaults['calib_flag'] = [False,True]
proc_orthomosaic.defaults['panel_fnam'] = ''
proc_orthomosaic.defaults['align_level'] = 'High'
proc_orthomosaic.defaults['preselect'] = [True,True]
proc_orthomosaic.defaults['point_limit'] = [40000,4000]
proc_orthomosaic.defaults['cam_flags'] = [False,False]
proc_orthomosaic.defaults['optimize_flag'] = True
proc_orthomosaic.defaults['cam_params'] = [True,True,True,True,False,True,True,True,True,False,False,True]
proc_orthomosaic.defaults['depth_map'] = ['Medium','Aggressive']
proc_orthomosaic.defaults['epsg'] = 32748
proc_orthomosaic.defaults['pixel_size'] = 0.025
proc_orthomosaic.defaults['output_type'] = 'Float32'
proc_orthomosaic.list_sizes['xmp_flag'] = 4
proc_orthomosaic.list_sizes['calib_flag'] = 2
proc_orthomosaic.list_sizes['align_level'] = 3
proc_orthomosaic.list_sizes['preselect'] = 2
proc_orthomosaic.list_sizes['point_limit'] = 2
proc_orthomosaic.list_sizes['cam_flags'] = 2
proc_orthomosaic.list_sizes['cam_params'] = 12
proc_orthomosaic.list_sizes['depth_map'] = 2
proc_orthomosaic.list_sizes['output_type'] = 2
proc_orthomosaic.list_labels['xmp_flag'] = ['Calibration','Orientation','Accuracy','Antenna']
proc_orthomosaic.list_labels['calib_flag'] = ['Reflectance Panel  ','Sun Sensor']
proc_orthomosaic.list_labels['align_level'] = ['High','Medium','Low']
proc_orthomosaic.list_labels['preselect'] = ['Generic','Reference']
proc_orthomosaic.list_labels['point_limit'] = ['Key :',' Tie :']
proc_orthomosaic.list_labels['cam_flags'] = ['Align','Optimize']
proc_orthomosaic.list_labels['cam_params'] = ['f','k1','k2','k3','k4','cx','cy','p1','p2','b1','b2','correction']
proc_orthomosaic.list_labels['depth_map'] = [('Quality :',['High','Medium','Low']),(' Filter :',['None','Mild','Moderate','Aggressive'])]
proc_orthomosaic.list_labels['output_type'] = ['Float32','UInt16']
proc_orthomosaic.input_types = {}
proc_orthomosaic.input_types['metashape_path'] = 'ask_file'
proc_orthomosaic.input_types['inpdirs'] = 'ask_folders'
proc_orthomosaic.input_types['qmin'] = 'box'
proc_orthomosaic.input_types['xmp_flag'] = 'boolean_list'
proc_orthomosaic.input_types['calib_flag'] = 'boolean_list'
proc_orthomosaic.input_types['panel_fnam'] = 'ask_file'
proc_orthomosaic.input_types['align_level'] = 'string_select'
proc_orthomosaic.input_types['preselect'] = 'boolean_list'
proc_orthomosaic.input_types['point_limit'] = 'int_list'
proc_orthomosaic.input_types['cam_flags'] = 'boolean_list'
proc_orthomosaic.input_types['optimize_flag'] = 'boolean'
proc_orthomosaic.input_types['cam_params'] = 'boolean_list'
proc_orthomosaic.input_types['depth_map'] = 'string_select_list'
proc_orthomosaic.input_types['epsg'] = 'box'
proc_orthomosaic.input_types['pixel_size'] = 'box'
proc_orthomosaic.input_types['output_type'] = 'string_select'
proc_orthomosaic.flag_check['panel_fnam'] = False
for pnam in proc_orthomosaic.pnams:
    proc_orthomosaic.values[pnam] = proc_orthomosaic.defaults[pnam]
