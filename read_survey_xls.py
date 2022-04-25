import pandas as pd
import sys
import re
import numpy as np
from pyproj import Proj,transform
from datetime import datetime

location = None
date = None
trans_date = None
variety = None
village = None
plot_bunch = None
gps_bunch = None
blb_bunch = None
gps_plot = None

def read_gps(s):
    #'S 06°50\'31.62"  E 107°16\'41.50"'
    m = re.search('([nNsS])\s*(\d+)\s*°\s*(\d+)\s*\'\s*([\d\.]+)\s*\"\s*([eEwW])\s*(\d+)\s*°\s*(\d+)\s*\'\s*([\d\.]+)',s)
    if not m:
        raise ValueError('Error, cannot read GPS coordinates >>> {}'.format(s))
    n = float(m.group(2))+float(m.group(3))/60.0+float(m.group(4))/3600.0
    if m.group(1).upper() == 'S':
        n *= -1
    e = float(m.group(6))+float(m.group(7))/60.0+float(m.group(8))/3600.0
    if m.group(5).upper() == 'W':
        e *= -1
    return n,e

def transform_wgs84_to_utm(longitude,latitude):
    inProj = Proj(init='epsg:4326')
    outProj = Proj(init='epsg:32748')
    return transform(inProj,outProj,longitude,latitude)
    
fnam = 'CIHEA - 11 B (20220311).xls'
xl = pd.ExcelFile(fnam)
sheets = xl.sheet_names
df = pd.read_excel(xl,header=None)
ny,nx = df.shape
for i in range(ny):
    line = ''
    for j in range(nx):
        v = df.iloc[i,j]
        if isinstance(v,str):
            line += v
        elif len(line) > 0 and line[-1] != ',':
            line += ','
    if location is None:
        m = re.search('Location[^:]*:\s*([^,]+)\s*,',line)
        if m:
            location = m.group(1).strip()
    if date is None:
        m = re.search('Time Observation[^:]*:\s*([^,]+)\s*,',line)
        if m:
            date = m.group(1).strip()
    if trans_date is None:
        m = re.search('Plant Date[^:]*:\s*([^,]+)\s*,',line)
        if m:
            trans_date = m.group(1).strip()
    if variety is None:
        m = re.search('Variety[^:]*:\s*([^,]+)\s*,',line)
        if m:
            variety = m.group(1).strip()
    if village is None:
        m = re.search('Village[^:]*:\s*(.*)\s*,\s*Village',line)
        if m:
            village = m.group(1).strip()

row_number_str = None
col_number_1 = 0
for i in range(ny-1):
    v1 = df.iloc[i,col_number_1]
    v2 = df.iloc[i+1,col_number_1]
    if isinstance(v1,str) and isinstance(v2,str):
        v1 = v1.strip()
        v2 = v2.strip()
        if v1 == 'Bunch' and v2 == 'Number':
            row_number_str = i+2
            break
if row_number_str is None:
    raise ValueError('Error, failed in finding row_number_str.')

col_number_2 = None
for j in range(col_number_1+1,nx-1):
    v1 = df.iloc[row_number_str-2,j]
    v2 = df.iloc[row_number_str-1,j]
    if isinstance(v1,str) and isinstance(v2,str):
        v1 = v1.strip()
        v2 = v2.strip()
        if v1 == 'Bunch' and v2 == 'Number':
            col_number_2 = j
            break
if col_number_2 is None:
    raise ValueError('Error, failed in finding col_number_2.')

row_number_end = None
for i in range(row_number_str+1,ny):
    v = df.iloc[i,col_number_1]
    if isinstance(v,str):
        v = v.strip()
        if v == 'Total':
            row_number_end = i
            break
if row_number_end is None:
    raise ValueError('Error, failed in finding row_number_end.')

v = df.iloc[row_number_end,col_number_2]
if not isinstance(v,str) or v.strip() != 'Total':
    raise ValueError('Error, failed in finding row_number_end >>> {}'.format(v))

col_gps_bunch = None
for j in range(1,col_number_2):
    v1 = df.iloc[row_number_str-2,j]
    v2 = df.iloc[row_number_str-1,j]
    if isinstance(v1,str) and isinstance(v2,float):
        v1 = v1.strip()
        if v1 == 'GPS' and np.isnan(v2):
            col_gps_bunch = j
            break
if col_gps_bunch is None:
    raise ValueError('Error, failed in finding col_gps_bunch.')

col_plot_1 = None
for j in range(1,col_number_2):
    v1 = df.iloc[row_number_str-2,j]
    v2 = df.iloc[row_number_str-1,j]
    if isinstance(v1,str) and isinstance(v2,str):
        v1 = v1.strip()
        v2 = v2.strip()
        if v1 == 'Plot' and v2 == 'Paddy':
            col_plot_1 = j
            break
if col_plot_1 is None:
    raise ValueError('Error, failed in finding col_plot_1.')

col_blb_bunch = None
for j in range(col_number_2+1,nx):
    v1 = df.iloc[row_number_str-2,j]
    v2 = df.iloc[row_number_str-1,j]
    if isinstance(v1,str) and isinstance(v2,str):
        v1 = v1.strip()
        v2 = v2.strip()
        if 'damage' in v1.lower() and v2 == 'BLB':
            col_blb_bunch = j
            break
if col_blb_bunch is None:
    raise ValueError('Error, failed in finding col_blb_bunch.')

col_plot_2 = None
for j in range(col_number_2+1,nx):
    v1 = df.iloc[row_number_str-2,j]
    v2 = df.iloc[row_number_str-1,j]
    if isinstance(v1,str) and isinstance(v2,float):
        v1 = v1.strip()
        if v1 == 'Plot Paddy' and np.isnan(v2):
            col_plot_2 = j
            break
if col_plot_2 is None:
    raise ValueError('Error, failed in finding col_plot_2.')

col_gps_paddy = None
for j in range(col_number_2+1,nx):
    v1 = df.iloc[row_number_str-2,j]
    v2 = df.iloc[row_number_str-1,j]
    if isinstance(v1,str) and isinstance(v2,str):
        v1 = v1.strip()
        v2 = v2.strip()
        if v1 == 'GPS' and v2 == 'Plot Paddy':
            col_gps_paddy = j
            break
if col_gps_paddy is None:
    raise ValueError('Error, failed in finding col_gps_paddy.')


plot_bunch = []
lon_bunch = []
lat_bunch = []
blb_bunch = []
plot = None
for i in range(row_number_str,row_number_end):
    v1 = df.iloc[i,col_plot_1]
    v2 = df.iloc[i,col_plot_2]
    if not np.isnan(v1):
        if v1 != v2:
            raise ValueError('Error, different plot number, v1={}, v2={}'.format(v1,v2))
        plot = v1
    plot_bunch.append(plot)
    lat,lon = read_gps(df.iloc[i,col_gps_bunch])
    lon_bunch.append(lon)
    lat_bunch.append(lat)
    blb = df.iloc[i,col_blb_bunch]
    if np.isnan(blb):
        blb = 0
    blb_bunch.append(blb)
