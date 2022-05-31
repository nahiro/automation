import os
import sys
import configparser
from proc_orthomosaic import proc_orthomosaic

# Set folder&file names
HOME = os.environ.get('USERPROFILE')
if HOME is None:
    HOME = os.environ.get('HOME')
main_inidir = os.path.join(HOME,'Work','Drone')
if not os.path.isdir(main_inidir):
    main_inidir = os.path.join(HOME,'Documents')
main_browse_image = os.path.join(HOME,'Pictures','browse.png')

# Set defaults
config_defaults = {
#----------- main -----------
'blocks'                    : ['1A','1B','2A','2B','3A','3B','4A','4B','5','6','7A','7B','8A','8B','9A','9B','10A','10B','11A','11B','12','13','14A','14B','15'],
'date_format'               : 'yyyy-mm&mmm-dd',
'inidir'                    : main_inidir,
'browse_image'              : main_browse_image,
'main_window_width'         : 500,
'main_top_frame_height'     : 60,
'main_left_frame_width'     : 30,
'main_right_frame_width'    : 100,
'main_left_cnv_height'      : 21,
'main_right_cnv_height'     : 21,
'main_center_btn_width'     : 20,
#----------- orthomosaic -----------
'inpdirs'                   : 'input',
'outdir'                    : 'output',
'qmin'                      : 0.5,
'calib_flag'                : [False,True],
'panel_fnam'                : '',
'align_level'               : 'High',
'preselect'                 : [True,True],
'point_limit'               : [40000,4000],
'cam_flags'                 : [True,True],
'optimize_flag'             : True,
'cam_params'                : [True,True,True,True,False,True,True,True,False,False],
'depth_map'                 : ['Medium','Aggressive'],
'epsg'                      : 32748,
'pixel_size'                : 0.025,
'scale_factor'              : 10.0,
'output_type'               : 'Int16',
#----------- geocor -----------
'gis_fnam'                  : 'All_area_polygon_20210914.shp',
'ref_fnam'                  : 'wv2_180629_pan.tif',
'ref_bands'                 : [-1,-9999],
'ref_pixel'                 : 0.2,
'ref_range'                 : [180.0,320.0],
'trg_fnam'                  : 'test.tif',
'trg_bands'                 : [2,4],
'trg_ndvi'                  : True,
'trg_binning'               : 0.2,
'trg_range'                 : [-10000.0,32767.0],
'init_shifts'               : [0.0,0.0],
'part_sizes'                : [50.0,50.0,25.0,25.0,15.0],
'gcp_intervals'             : [25.0,25.0,12.5,12.5,7.5],
'max_shifts'                : [8.0,5.0,2.5,1.5,1.5],
'margins'                   : [12.0,7.5,3.75,2.25,2.25],
'scan_steps'                : [2,2,1,1,1],
'higher_flags'              : [True,True,True],
'geocor_order'              : '2nd',
'boundary_width'            : 0.6,
'boundary_nmin'             : 0.1,
'boundary_cmins'            : [0.01,1.3],
'boundary_rmax'             : 1.0,
'boundary_emaxs'            : [3.0,2.0,1.5],
#----------- indices -----------
'inp_fnam'                  : 'input.tif',
'out_params'                : [False,False,False,False,False,True,True,True,True,True,True,True,False,True],
'norm_bands'                : [True,True,True,True,True],
'rgi_red_band'              : 'e',
'data_range'                : [np.nan,np.nan],
#----------- identify -----------
'inp_fnam'                  : 'input.xls',
'i_sheet'                   : 1,
'gcp_fnam'                  : 'gcp.dat',
'geocor_order'              : '2nd',
'epsg'                      : 32748,
'buffer'                    : 5.0,
'bunch_nmin'                : 5,
'bunch_rmax'                : 10.0,
'bunch_emax'                : 2.0,
'point_nmin'                : 5,
'point_rmax'                : 1.0,
'point_dmax'                : [1.0,0.5],
'point_area'                : [0.015,0.105,0.05],
'criteria'                  : 'Distance from Line',
'rr_param'                  : ['Lrg','S/N'],
'rthr'                      : [0.0,1.0,0.01],
'sthr'                      : 1.0,
'data_range'                : [np.nan,np.nan],
'neighbor_size'             : [0.78,0.95],
#----------- extract -----------
'inp_fnams'                 : 'input.tif',
'gps_fnam'                  : 'gps.csv',
'region_size'               : [0.2,0.5],
#----------- formula -----------
'inp_fnams'                 : 'input.csv',
'age_range'                 : [-100.0,150.0],
'n_x'                       : [1,2],
'x_params'                  : [False,False,False,False,False,True,True,True,True,True,True,True,False,True],
'q_params'                  : [True,True,True,True],
'y_params'                  : [True,False,False,False,False,False],
'score_max'                 : [9,9,1,1,1,9],
'ythr'                      : [0.2,0.2,0.2,0.2,0.2,0.2],
'yfac1'                     : [1.0,np.nan,np.nan,np.nan,np.nan,np.nan],
'yfac2'                     : [np.nan,1.0,np.nan,np.nan,np.nan,np.nan],
'yfac3'                     : [np.nan,np.nan,1.0,np.nan,np.nan,np.nan],
'yfac4'                     : [np.nan,np.nan,np.nan,1.0,np.nan,np.nan],
'yfac5'                     : [np.nan,np.nan,np.nan,np.nan,1.0,np.nan],
'yfac6'                     : [np.nan,np.nan,np.nan,np.nan,np.nan,1.0],
'criteria'                  : 'RMSE_test',
'n_multi'                   : 1,
'vif_max'                   : 5.0,
'n_cros'                    : 5,
'n_formula'                 : 3,
#----------- estimate -----------
'inp_fnams'                 : 'input.tif',
'gps_fnam'                  : 'gps.csv',
'region_size'               : [0.2,0.5],
}
config = configparser.ConfigParser(config_defaults)
config['main'] = {}

# Read configuration
if (len(sys.argv) > 1) and os.path.exists(sys.argv[1]):
    fnam = sys.argv[1]
    config.read(fnam,encoding='utf-8')

# Configure parameters
#----------- main -----------
blocks = eval(config['main'].get('blocks'))
date_format = config['main'].get('date_format')
inidir = config['main'].get('inidir')
browse_image = config['main'].get('browse_image')
window_width = config['main'].getint('main_window_width')
top_frame_height = config['main'].getint('main_top_frame_height')
left_frame_width = config['main'].getint('main_left_frame_width')
right_frame_width = config['main'].getint('main_right_frame_width')
left_cnv_height = config['main'].getint('main_left_cnv_height')
right_cnv_height = config['main'].getint('main_right_cnv_height')
center_btn_width = config['main'].getint('main_center_btn_width')
#----------- orthomosaic -----------
#proc_orthomosaic.values['inpdirs'] = config[].get('inpdirs')
#----------- geocor -----------
#----------- indices -----------
#----------- identify -----------
#----------- extract -----------
#----------- formula -----------
#----------- estimate -----------

