import os
import sys
import numpy as np
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
'main.blocks'               : ['1A','1B','2A','2B','3A','3B','4A','4B','5','6','7A','7B','8A','8B','9A','9B','10A','10B','11A','11B','12','13','14A','14B','15'],
'main.date_format'          : 'yyyy-mm&mmm-dd',
'main.inidir'               : main_inidir,
'main.browse_image'         : main_browse_image,
'main.window_width'         : 500,
'main.top_frame_height'     : 60,
'main.left_frame_width'     : 30,
'main.right_frame_width'    : 100,
'main.left_cnv_height'      : 21,
'main.right_cnv_height'     : 21,
'main.center_btn_width'     : 20,
#----------- orthomosaic -----------
'orthomosaic.inpdirs'       : 'input',
'orthomosaic.outdir'        : 'output',
'orthomosaic.qmin'          : 0.5,
'orthomosaic.calib_flag'    : [False,True],
'orthomosaic.panel_fnam'    : '',
'orthomosaic.align_level'   : 'High',
'orthomosaic.preselect'     : [True,True],
'orthomosaic.point_limit'   : [40000,4000],
'orthomosaic.cam_flags'     : [True,True],
'orthomosaic.optimize_flag' : True,
'orthomosaic.cam_params'    : [True,True,True,True,False,True,True,True,False,False],
'orthomosaic.depth_map'     : ['Medium','Aggressive'],
'orthomosaic.epsg'          : 32748,
'orthomosaic.pixel_size'    : 0.025,
'orthomosaic.scale_factor'  : 10.0,
'orthomosaic.output_type'   : 'Int16',
#----------- geocor -----------
'geocor.gis_fnam'           : 'All_area_polygon_20210914.shp',
'geocor.ref_fnam'           : 'wv2_180629_pan.tif',
'geocor.ref_bands'          : [-1,-9999],
'geocor.ref_pixel'          : 0.2,
'geocor.ref_range'          : [180.0,320.0],
'geocor.trg_fnam'           : 'test.tif',
'geocor.trg_bands'          : [2,4],
'geocor.trg_ndvi'           : True,
'geocor.trg_binning'        : 0.2,
'geocor.trg_range'          : [-10000.0,32767.0],
'geocor.init_shifts'        : [0.0,0.0],
'geocor.part_sizes'         : [50.0,50.0,25.0,25.0,15.0],
'geocor.gcp_intervals'      : [25.0,25.0,12.5,12.5,7.5],
'geocor.max_shifts'         : [8.0,5.0,2.5,1.5,1.5],
'geocor.margins'            : [12.0,7.5,3.75,2.25,2.25],
'geocor.scan_steps'         : [2,2,1,1,1],
'geocor.higher_flags'       : [True,True,True],
'geocor.geocor_order'       : '2nd',
'geocor.boundary_width'     : 0.6,
'geocor.boundary_nmin'      : 0.1,
'geocor.boundary_cmins'     : [0.01,1.3],
'geocor.boundary_rmax'      : 1.0,
'geocor.boundary_emaxs'     : [3.0,2.0,1.5],
#----------- indices -----------
'indices.inp_fnam'          : 'input.tif',
'indices.out_params'        : [False,False,False,False,False,True,True,True,True,True,True,True,False,True],
'indices.norm_bands'        : [True,True,True,True,True],
'indices.rgi_red_band'      : 'e',
'indices.data_range'        : [np.nan,np.nan],
#----------- identify -----------
'identify.inp_fnam'         : 'input.xls',
'identify.i_sheet'          : 1,
'identify.gcp_fnam'         : 'gcp.dat',
'identify.geocor_order'     : '2nd',
'identify.epsg'             : 32748,
'identify.buffer'           : 5.0,
'identify.bunch_nmin'       : 5,
'identify.bunch_rmax'       : 10.0,
'identify.bunch_emax'       : 2.0,
'identify.point_nmin'       : 5,
'identify.point_rmax'       : 1.0,
'identify.point_dmax'       : [1.0,0.5],
'identify.point_area'       : [0.015,0.105,0.05],
'identify.criteria'         : 'Distance from Line',
'identify.rr_param'         : ['Lrg','S/N'],
'identify.rthr'             : [0.0,1.0,0.01],
'identify.sthr'             : 1.0,
'identify.data_range'       : [np.nan,np.nan],
'identify.neighbor_size'    : [0.78,0.95],
#----------- extract -----------
'extract.inp_fnams'         : 'input.tif',
'extract.gps_fnam'          : 'gps.csv',
'extract.region_size'       : [0.2,0.5],
#----------- formula -----------
'formula.inp_fnams'         : 'input.csv',
'formula.age_range'         : [-100.0,150.0],
'formula.n_x'               : [1,2],
'formula.x_params'          : [False,False,False,False,False,True,True,True,True,True,True,True,False,True],
'formula.q_params'          : [True,True,True,True],
'formula.y_params'          : [True,False,False,False,False,False],
'formula.score_max'         : [9,9,1,1,1,9],
'formula.ythr'              : [0.2,0.2,0.2,0.2,0.2,0.2],
'formula.yfac1'             : [1.0,np.nan,np.nan,np.nan,np.nan,np.nan],
'formula.yfac2'             : [np.nan,1.0,np.nan,np.nan,np.nan,np.nan],
'formula.yfac3'             : [np.nan,np.nan,1.0,np.nan,np.nan,np.nan],
'formula.yfac4'             : [np.nan,np.nan,np.nan,1.0,np.nan,np.nan],
'formula.yfac5'             : [np.nan,np.nan,np.nan,np.nan,1.0,np.nan],
'formula.yfac6'             : [np.nan,np.nan,np.nan,np.nan,np.nan,1.0],
'formula.criteria'          : 'RMSE_test',
'formula.n_multi'           : 1,
'formula.vif_max'           : 5.0,
'formula.n_cros'            : 5,
'formula.n_formula'         : 3,
#----------- estimate -----------
'estimate.inp_fnams'        : 'input.tif',
'estimate.gps_fnam'         : 'gps.csv',
'estimate.region_size'      : [0.2,0.5],
}
config = configparser.ConfigParser(config_defaults)
config['main'] = {}

# Read configuration
if (len(sys.argv) > 1) and os.path.exists(sys.argv[1]):
    fnam = sys.argv[1]
    config.read(fnam,encoding='utf-8')

# Configure parameters
#----------- main -----------
blocks = eval(config['main'].get('main.blocks'))
date_format = config['main'].get('main.date_format')
inidir = config['main'].get('main.inidir')
browse_image = config['main'].get('main.browse_image')
window_width = config['main'].getint('main.window_width')
top_frame_height = config['main'].getint('main.top_frame_height')
left_frame_width = config['main'].getint('main.left_frame_width')
right_frame_width = config['main'].getint('main.right_frame_width')
left_cnv_height = config['main'].getint('main.left_cnv_height')
right_cnv_height = config['main'].getint('main.right_cnv_height')
center_btn_width = config['main'].getint('main.center_btn_width')
#----------- orthomosaic -----------
#proc_orthomosaic.values['inpdirs'] = config[].get('inpdirs')
#----------- geocor -----------
#----------- indices -----------
#----------- identify -----------
#----------- extract -----------
#----------- formula -----------
#----------- estimate -----------

