import os
import sys
import configparser
from proc_orthomosaic import proc_orthomosaic

config = configparser.ConfigParser(defaults={
# main
'blocks':['1A','1B','2A','2B','3A','3B','4A','4B','5','6','7A','7B','8A','8B','9A','9B','10A','10B','11A','11B','12','13','14A','14B','15'],
'date_format': 'yyyy-mm&mmm-dd',
})
config['main'] = {}
if (len(sys.argv) > 1) and os.path.exists(sys.argv[1]):
    fnam = sys.argv[1]
    config.read(fnam,encoding='utf-8')

blocks = eval(config['main'].get('blocks'))
date_format = config['main'].get('date_format')
proc_orthomosaic.values['inpdirs'] = 'this_is_a_test'
