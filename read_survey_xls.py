#!/usr/bin/env python
import sys
import re
import numpy as np
import pandas as pd
from datetime import datetime
import pyproj
from optparse import OptionParser,IndentedHelpFormatter

# Defaults
SHEET = 0
EPSG = 32748 # UTM zone 48S

# Read options
parser = OptionParser(formatter=IndentedHelpFormatter(max_help_position=200,width=200))
parser.add_option('-I','--inp_fnam',default=None,help='Input file name (%default)')
parser.add_option('-O','--out_fnam',default=None,help='Output file name (%default)')
parser.add_option('-S','--sheet',default=SHEET,type='int',help='Sheet number (%default)')
parser.add_option('-E','--epsg',default=EPSG,help='Output EPSG (%default)')
(opts,args) = parser.parse_args()

def read_gps(s):
    #'S 06°50\'31.62"  E 107°16\'41.50"'
    m = re.search('([nNsS])\s*(\d+)\s*°\s*(\d+)\s*\'\s*([\d\.]+)\s*\"\s*([eEwW])\s*(\d+)\s*°\s*(\d+)\s*\'\s*([\d\.]+)',s)
    if not m:
        raise ValueError('Error, cannot read GPS coordinates >>> {}'.format(s))
    lat = float(m.group(2))+float(m.group(3))/60.0+float(m.group(4))/3600.0
    if m.group(1).upper() == 'S':
        lat *= -1
    lon = float(m.group(6))+float(m.group(7))/60.0+float(m.group(8))/3600.0
    if m.group(5).upper() == 'W':
        lon *= -1
    return lon,lat

if int(pyproj.__version__[0]) > 1:
    def transform_wgs84_to_utm(longitude,latitude):
        return pyproj.Transformer.from_crs(4326,opts.epsg,always_xy=True).transform(longitude,latitude)
else:
    def transform_wgs84_to_utm(longitude,latitude):
        inProj = pyproj.Proj(init='epsg:4326')
        outProj = pyproj.Proj(init='epsg:{}'.format(opts.epsg))
        return pyproj.transform(inProj,outProj,longitude,latitude)
    
xl = pd.ExcelFile(opts.inp_fnam)
if opts.sheet > 0:
    sheets = xl.sheet_names
    if len(sheets) <= opts.sheet:
        raise ValueError('Error, len(sheets)={}, opts.sheet={}'.format(len(sheets),opts.sheet))
    df = pd.read_excel(xl,header=None,sheet_name=sheets[opts.sheet])
else:
    df = pd.read_excel(xl,header=None)
ny,nx = df.shape

location = None
date = None
trans_date = None
variety = None
village = None
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
            location = m.group(1).strip().replace(' ','')
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
if location is None:
    raise ValueError('Error, failed in finding location.')
if date is None:
    raise ValueError('Error, failed in finding date.')
dtim = datetime.strptime(date,'%d.%m.%Y')
if opts.out_fnam is None:
    opts.out_fnam = '{}_{:%Y-%m-%d}_blb.csv'.format(location,dtim)

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

number_bunch = []
plot_bunch = []
lon_bunch = []
lat_bunch = []
blb_bunch = []
lon_plot = {}
lat_plot = {}
plot = None
for i in range(row_number_str,row_number_end):
    v1 = df.iloc[i,col_plot_1]
    v2 = df.iloc[i,col_plot_2]
    if not np.isnan(v1):
        if v1 != v2:
            raise ValueError('Error, different plot number, v1={}, v2={}'.format(v1,v2))
        plot = v1
    number_bunch.append(df.iloc[i,col_number_1])
    plot_bunch.append(plot)
    lon,lat = read_gps(df.iloc[i,col_gps_bunch])
    lon_bunch.append(lon)
    lat_bunch.append(lat)
    blb = df.iloc[i,col_blb_bunch]
    if np.isnan(blb):
        blb = 0
    blb_bunch.append(blb)
    if not plot in lon_plot:
        lon_plot[plot] = []
        lat_plot[plot] = []
    try:
        lon,lat = read_gps(df.iloc[i,col_gps_paddy])
        lon_plot[plot].append(lon)
        lat_plot[plot].append(lat)
    except Exception:
        continue
x_bunch,y_bunch = transform_wgs84_to_utm(lon_bunch,lat_bunch)
if len(lon_plot) < 1 or len(lon_plot) != len(lat_plot):
    raise ValueError('Error, len(lon_plot)={}, len(lat_plot)={}'.format(len(lon_plot),len(lat_plot)))
plots = np.unique(plot_bunch)
x_plot = {}
y_plot = {}
for plot in plots:
    if len(lon_plot[plot]) < 1 or len(lon_plot[plot]) != len(lat_plot[plot]):
        raise ValueError('Error, len(lon_plot[{}])={}, len(lat_plot[{}])={}'.format(plot,len(lon_plot[plot]),plot,len(lat_plot[plot])))
    x,y = transform_wgs84_to_utm(lon_plot[plot],lat_plot[plot])
    x_plot[plot] = x
    y_plot[plot] = y
date_plot = {}
dtim_plot = {}
for plot in plots:
    # Plot 1. 04.01.2022 Plot 2. 04.01.2022 Plot 3. 04.01.2022
    m = re.search('Plot\s*{}[\D]+([\d\.]+)\s*'.format(plot),trans_date)
    if not m:
        raise ValueError('Error, failed in finding Plant Date for Plot{} >>> {}'.format(plot,trans_date))
    date_plot[plot] = m.group(1)
    dtim_plot[plot] = datetime.strptime(date_plot[plot],'%d.%m.%Y')

with open(opts.out_fnam,'w') as fp:
    fp.write('# Location: {}\n'.format(location))
    fp.write('# Date: {:%Y-%m-%d}\n'.format(dtim))
    for plot in plots:
        fp.write('# Plot{}: {:%Y-%m-%d}'.format(plot,dtim_plot[plot]))
        for i in range(len(x_plot[plot])):
            fp.write(' {:12.4f} {:13.4f}'.format(x_plot[plot][i],y_plot[plot][i]))
        fp.write('\n')
    fp.write('# Variety: {}\n'.format(variety))
    fp.write('# Village: {}\n'.format(village))
    fp.write('#------------------------\n')
    fp.write('# Bunch Number, Plot Paddy, Easting, Northing, Damaged by BLB\n')
    for i in range(len(plot_bunch)):
        fp.write('{:3d} {:3d} {:12.4f} {:13.4f} {:3d}\n'.format(number_bunch[i],plot_bunch[i],x_bunch[i],y_bunch[i],blb_bunch[i]))
