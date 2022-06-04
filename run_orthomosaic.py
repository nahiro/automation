#!/usr/bin/env python
import numpy as np
from subprocess import call
from proc_orthomosaic import proc_orthomosaic
from argparse import ArgumentParser,MetavarTypeHelpFormatter

# Read options
process = proc_orthomosaic
parser = ArgumentParser(formatter_class=lambda prog:MetavarTypeHelpFormatter(prog,max_help_position=200,width=200))
for pnam in process.pnams:
    if process.input_types[pnam] in ['ask_files','ask_folders']:
        parser.add_argument('--{}'.format(pnam),default=None,type=str,help='{} (%(default)s)'.format(process.params[pnam]))
    elif process.param_types[pnam] in ['string','string_select']:
        parser.add_argument('--{}'.format(pnam),default=None,type=str,help='{} (%(default)s)'.format(process.params[pnam]))
    elif process.param_types[pnam] in ['int','int_select']:
        parser.add_argument('--{}'.format(pnam),default=None,type=int,help='{} (%(default)s)'.format(process.params[pnam]))
    elif process.param_types[pnam] in ['float','float_select']:
        parser.add_argument('--{}'.format(pnam),default=None,type=float,help='{} (%(default)s)'.format(process.params[pnam]))
    elif process.param_types[pnam] in ['boolean','boolean_select']:
        parser.add_argument('--{}'.format(pnam),default=None,type=int,help='{} (%(default)s)'.format(process.params[pnam]))
    elif process.param_types[pnam] in ['float_list','float_select_list']:
        parser.add_argument('--{}'.format(pnam),default=None,type=str,help='{} (%(default)s)'.format(process.params[pnam]))
    else:
        parser.add_argument('--{}'.format(pnam),default=None,type=str,help='{} (%(default)s)'.format(process.params[pnam]))
args = parser.parse_args()

for pnam in process.pnams:
    if process.input_types[pnam] in ['ask_files','ask_folders']:
        process.values[pnam] = getattr(args,pnam)
    elif process.param_types[pnam] in ['string','string_select']:
        process.values[pnam] = getattr(args,pnam)
    elif process.param_types[pnam] in ['int','int_select']:
        process.values[pnam] = getattr(args,pnam)
    elif process.param_types[pnam] in ['float','float_select']:
        process.values[pnam] = getattr(args,pnam)
    elif process.param_types[pnam] in ['boolean','boolean_select']:
        process.values[pnam] = bool(getattr(args,pnam))
    elif process.param_types[pnam] in ['float_list','float_select_list']:
        process.values[pnam] = eval(getattr(args,pnam).replace('nan','np.nan'))
    else:
        process.values[pnam] = eval(getattr(args,pnam))
    print('pnam={}, value={}'.format(pnam,process.values[pnam]))
