import os
import sys
import configparser
#from proc_orthomosaic import proc_orthomosaic

config_defaults = dict(os.environ)
config_defaults.update({
# main
'blocks':['1A','1B','2A','2B','3A','3B','4A','4B','5','6','7A','7B','8A','8B','9A','9B','10A','10B','11A','11B','12','13','14A','14B','15'],
'date_format': 'yyyy-mm&mmm-dd',
'inidir':'%(USERPROFILE)s/Work/Drone',
'browse_image':'%(USERPROFILE)s/Pictures/browse.png',
'main_window_width':500,
'main_top_frame_height':60,
'main_left_frame_width':30,
'main_right_frame_width':100,
'main_left_cnv_height':21,
'main_right_cnv_height':21,
'main_center_btn_width':20
})
config = configparser.ConfigParser(config_defaults)
config['main'] = {}
if (len(sys.argv) > 1) and os.path.exists(sys.argv[1]):
    fnam = sys.argv[1]
    config.read(fnam,encoding='utf-8')

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

#proc_orthomosaic.values['inpdirs'] = 'this_is_a_test'
