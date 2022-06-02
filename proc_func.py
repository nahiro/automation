import os
import sys
import numpy as np

def check_file(s,t,flag=True):
    try:
        if not flag:
            return True
        elif not os.path.exists(t):
            raise IOError('Error in {}, no such file >>> {}'.format(s,t))
        return True
    except Exception as e:
        sys.stderr.write(str(e)+'\n')
        return False

def check_files(s,t,flag=True):
    try:
        if not flag:
            return True
        else:
            for item in t.split(';'):
                if not os.path.isdir(item):
                    raise IOError('Error in {}, no such file >>> {}'.format(s,item))
        return True
    except Exception as e:
        sys.stderr.write(str(e)+'\n')
        return False

def check_folder(s,t,make=False):
    try:
        if make and not os.path.exists(t):
            os.makedirs(t)
        if not os.path.isdir(t):
            raise IOError('Error in {}, no such folder >>> {}'.format(s,t))
        return True
    except Exception as e:
        sys.stderr.write(str(e)+'\n')
        return False

def check_folders(s,t,make=False):
    try:
        for item in t.split('\n'):
            dnam = item.strip()
            if len(dnam) < 1:
                continue
            if make and not os.path.exists(dnam):
                os.makedirs(dnam)
            if not os.path.isdir(dnam):
                raise IOError('Error in {}, no such folder >>> {}'.format(s,dnam))
        return True
    except Exception as e:
        sys.stderr.write(str(e)+'\n')
        return False

def check_int(s,t,vmin=-sys.maxsize,vmax=sys.maxsize):
    try:
        n = int(t)
        if n < vmin or n > vmax:
            raise ValueError('Error in {}, out of range >>> {}'.format(s,t))
        return True
    except Exception as e:
        sys.stderr.write(str(e)+'\n')
        return False

def check_float(s,t,vmin=-sys.float_info.max,vmax=sys.float_info.max,allow_nan=False):
    try:
        v = float(t)
        if allow_nan and np.isnan(v):
            return True
        if v < vmin or v > vmax:
            raise ValueError('Error in {}, out of range >>> {}'.format(s,t))
        return True
    except Exception as e:
        sys.stderr.write(str(e)+'\n')
        return False
