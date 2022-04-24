from proc_class import Process

proc_geocor = Process()
proc_geocor.proc_name = 'geocor'
proc_geocor.proc_title = 'Geometric Correction'
proc_geocor.pnams.append('gis_fnam')
proc_geocor.pnams.append('ref_fnam')
proc_geocor.pnams.append('ref_bands')
proc_geocor.pnams.append('ref_pixel')
proc_geocor.pnams.append('ref_range')
proc_geocor.pnams.append('trg_fnam')
proc_geocor.pnams.append('trg_bands')
proc_geocor.pnams.append('trg_ndvi')
proc_geocor.pnams.append('trg_binning')
proc_geocor.pnams.append('trg_range')
proc_geocor.pnams.append('part_sizes')
proc_geocor.pnams.append('gcp_intervals')
proc_geocor.pnams.append('max_shifts')
proc_geocor.pnams.append('margins')
proc_geocor.pnams.append('scan_steps')
proc_geocor.pnams.append('higher_flags')
proc_geocor.pnams.append('boundary_width')
proc_geocor.pnams.append('boundary_nmin')
proc_geocor.pnams.append('boundary_cmins')
proc_geocor.pnams.append('boundary_rmax')
proc_geocor.pnams.append('boundary_emaxs')
proc_geocor.params['gis_fnam'] = 'Polygon File'
proc_geocor.params['ref_fnam'] = 'Reference Image'
proc_geocor.params['ref_bands'] = 'Reference Band'
proc_geocor.params['ref_pixel'] = 'Reference Resample Size'
proc_geocor.params['ref_range'] = 'Reference DN Range'
proc_geocor.params['trg_fnam'] = 'Target Image'
proc_geocor.params['trg_bands'] = 'Target Band'
proc_geocor.params['trg_ndvi'] = 'Target NDVI Flag'
proc_geocor.params['trg_binning'] = 'Target Binning Size'
proc_geocor.params['trg_range'] = 'Target DN Range'
proc_geocor.params['part_sizes'] = 'Partial Image Size'
proc_geocor.params['gcp_intervals'] = 'GCP Interval'
proc_geocor.params['max_shifts'] = 'Max Shift'
proc_geocor.params['margins'] = 'Image Margin'
proc_geocor.params['scan_steps'] = 'Scan Step'
proc_geocor.params['higher_flags'] = 'Higher Order Flag'
proc_geocor.params['boundary_width'] = 'Boundary Width'
proc_geocor.params['boundary_nmin'] = 'Min Boundary Ratio'
proc_geocor.params['boundary_cmins'] = 'Min Contrast'
proc_geocor.params['boundary_rmax'] = 'Max Contrast Spread'
proc_geocor.params['boundary_emaxs'] = 'Max Error'
proc_geocor.param_types['gis_fnam'] = 'string'
proc_geocor.param_types['ref_fnam'] = 'string'
proc_geocor.param_types['ref_bands'] = 'int_list'
proc_geocor.param_types['ref_pixel'] = 'double'
proc_geocor.param_types['ref_range'] = 'double_list'
proc_geocor.param_types['trg_fnam'] = 'string'
proc_geocor.param_types['trg_bands'] = 'int_list'
proc_geocor.param_types['trg_ndvi'] = 'boolean'
proc_geocor.param_types['trg_binning'] = 'int'
proc_geocor.param_types['trg_range'] = 'double_list'
proc_geocor.param_types['part_sizes'] = 'int_list'
proc_geocor.param_types['gcp_intervals'] = 'int_list'
proc_geocor.param_types['max_shifts'] = 'int_list'
proc_geocor.param_types['margins'] = 'int_list'
proc_geocor.param_types['scan_steps'] = 'int_list'
proc_geocor.param_types['higher_flags'] = 'boolean_list'
proc_geocor.param_types['boundary_width'] = 'double'
proc_geocor.param_types['boundary_nmin'] = 'double'
proc_geocor.param_types['boundary_cmins'] = 'double_list'
proc_geocor.param_types['boundary_rmax'] = 'double'
proc_geocor.param_types['boundary_emaxs'] = 'double_list'
proc_geocor.param_range['ref_bands'] = (-10000,10000)
proc_geocor.param_range['ref_pixel'] = (0.01,50.0)
proc_geocor.param_range['ref_range'] = (-1.0e50,1.0e50)
proc_geocor.param_range['trg_bands'] = (-10000,10000)
proc_geocor.param_range['trg_binning'] = (1,64)
proc_geocor.param_range['trg_range'] = (-1.0e50,1.0e50)
proc_geocor.param_range['part_sizes'] = (2,1000000)
proc_geocor.param_range['gcp_intervals'] = (1,1000000)
proc_geocor.param_range['max_shifts'] = (1,1000000)
proc_geocor.param_range['margins'] = (1,1000000)
proc_geocor.param_range['scan_steps'] = (1,1000000)
proc_geocor.param_range['boundary_width'] = (1.0e-6,1.0e6)
proc_geocor.param_range['boundary_nmin'] = (1.0e-6,1.0)
proc_geocor.param_range['boundary_cmins'] = (-1.0e6,1.0e6)
proc_geocor.param_range['boundary_rmax'] = (1.0e-6,1.0e6)
proc_geocor.param_range['boundary_emaxs'] = (1.0e-6,1.0e6)
proc_geocor.defaults['gis_fnam'] = 'All_area_polygon_20210914.shp'
proc_geocor.defaults['ref_fnam'] = 'wv2_180629_pan.tif'
proc_geocor.defaults['ref_bands'] = [-1,-9999]
proc_geocor.defaults['ref_pixel'] = 0.2
proc_geocor.defaults['ref_range'] = [180.0,320.0]
proc_geocor.defaults['trg_fnam'] = 'test.tif'
proc_geocor.defaults['trg_bands'] = [2,4]
proc_geocor.defaults['trg_ndvi'] = True
proc_geocor.defaults['trg_binning'] = 8
proc_geocor.defaults['trg_range'] = [-10000.0,32767.0]
proc_geocor.defaults['part_sizes'] = [250,250,120,120,80]
proc_geocor.defaults['gcp_intervals'] = [125,125,60,60,40]
proc_geocor.defaults['max_shifts'] = [40,25,12,8,8]
proc_geocor.defaults['margins'] = [60,40,18,12,12]
proc_geocor.defaults['scan_steps'] = [2,2,1,1,1]
proc_geocor.defaults['higher_flags'] = [True,True,True]
proc_geocor.defaults['boundary_width'] = 0.6
proc_geocor.defaults['boundary_nmin'] = 0.1
proc_geocor.defaults['boundary_cmins'] = [0.01,1.3]
proc_geocor.defaults['boundary_rmax'] = 1.0
proc_geocor.defaults['boundary_emaxs'] = [3.0,2.0,1.5]
proc_geocor.list_sizes['ref_bands'] = 2
proc_geocor.list_sizes['ref_range'] = 2
proc_geocor.list_sizes['trg_bands'] = 2
proc_geocor.list_sizes['trg_range'] = 2
proc_geocor.list_sizes['part_sizes'] = 5
proc_geocor.list_sizes['gcp_intervals'] = 5
proc_geocor.list_sizes['max_shifts'] = 5
proc_geocor.list_sizes['margins'] = 5
proc_geocor.list_sizes['scan_steps'] = 5
proc_geocor.list_sizes['higher_flags'] = 3
proc_geocor.list_sizes['boundary_cmins'] = 2
proc_geocor.list_sizes['boundary_emaxs'] = 3
proc_geocor.list_labels['ref_bands'] = ['','']
proc_geocor.list_labels['ref_range'] = ['Min :',' Max :']
proc_geocor.list_labels['trg_bands'] = ['','']
proc_geocor.list_labels['trg_range'] = ['Min :',' Max :']
#proc_geocor.list_labels['part_sizes'] = ['1','2','3','4','5']
proc_geocor.list_labels['part_sizes'] = ['','','','','']
proc_geocor.list_labels['gcp_intervals'] = ['','','','','']
proc_geocor.list_labels['max_shifts'] = ['','','','','']
proc_geocor.list_labels['margins'] = ['','','','','']
proc_geocor.list_labels['scan_steps'] = ['','','','','']
proc_geocor.list_labels['higher_flags'] = ['1st','2nd','3rd']
proc_geocor.list_labels['boundary_cmins'] = ['','']
proc_geocor.list_labels['boundary_emaxs'] = ['','','']
for pnam in proc_geocor.pnams:
    proc_geocor.values[pnam] = proc_geocor.defaults[pnam]
proc_geocor.input_types['gis_fnam'] = 'ask_file'
proc_geocor.input_types['ref_fnam'] = 'ask_file'
proc_geocor.input_types['ref_bands'] = 'int_list'
proc_geocor.input_types['ref_pixel'] = 'box'
proc_geocor.input_types['ref_range'] = 'double_list'
proc_geocor.input_types['trg_fnam'] = 'ask_file'
proc_geocor.input_types['trg_bands'] = 'int_list'
proc_geocor.input_types['trg_ndvi'] = 'boolean'
proc_geocor.input_types['trg_binning'] = 'box'
proc_geocor.input_types['trg_range'] = 'double_list'
proc_geocor.input_types['part_sizes'] = 'int_list'
proc_geocor.input_types['gcp_intervals'] = 'int_list'
proc_geocor.input_types['max_shifts'] = 'int_list'
proc_geocor.input_types['margins'] = 'int_list'
proc_geocor.input_types['scan_steps'] = 'int_list'
proc_geocor.input_types['higher_flags'] = 'boolean_list'
proc_geocor.input_types['boundary_width'] = 'box'
proc_geocor.input_types['boundary_nmin'] = 'box'
proc_geocor.input_types['boundary_cmins'] = 'double_list'
proc_geocor.input_types['boundary_rmax'] = 'box'
proc_geocor.input_types['boundary_emaxs'] = 'double_list'
proc_geocor.middle_left_frame_width = 450
