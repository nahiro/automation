import os
import shutil
import re
from datetime import datetime

def set_obs_fnam(block,dstr,field_dir,date_format='yyyy-mm&mmm-dd'):
    obs_fnam = os.path.join(field_dir,block,'Excel_File','{}_{}.xls'.format(block,dstr))
    if os.path.exists(obs_fnam):
        return 0
    elif not os.path.isdir(field_dir):
        return -1
    date_fmt = date_format.replace('yyyy','%Y').replace('yy','%y').replace('mmm','%b').replace('mm','%m').replace('dd','%d').replace('&','')
    dtim = datetime.strptime(dstr,date_fmt)
    for f in sorted(os.listdir(field_dir)):
        obs_block = None
        obs_date = None
        try:
            # pattern 1: day[. ,-]month[. ,-]year[. ,-]block.xls
            m = re.search('^(\d+)[\s\.\-,]+(\d+)[\s\.\-,]+(\d+)[\s\.\-,]+(\S.*)\.xls',f.lower())
            if m:
                day = int(m.group(1))
                month = int(m.group(2))
                year = int(m.group(3))
                obs_block = m.group(4).replace(' ','').strip().upper()
                obs_date = datetime(year,month,day)
            else:
                # pattern 2: cihea - block (yyyymmdd).xls
                m = re.search('[^-]+\-([^(]+)\(\s*(\d+)\s*\)\s*\.xls',f.lower())
                if m:
                    obs_block = m.group(1).replace(' ','').strip().upper()
                    obs_date = datetime.strptime(m.group(2),'%Y%m%d')
        except Exception:
            continue
        if obs_block is None or obs_date is None:
            continue
        if (obs_block == block) or ('Block-'+obs_block == block):
            obs_dstr = obs_date.strftime(date_fmt)
            if obs_dstr == dstr:
                fnam = os.path.join(field_dir,f)
                dnam = os.path.dirname(obs_fnam)
                if not os.path.exists(dnam):
                    os.makedirs(dnam)
                if not os.path.exists(dnam):
                    raise IOError('Error, no such folder >>> {}'.format(dnam))
                shutil.move(fnam,obs_fnam)
                return 1
