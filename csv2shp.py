import os
import sys
import numpy as np
import pandas as pd
import shapefile
try:
    import ogr
    import osr
except Exception:
    from osgeo import ogr,osr

if len(sys.argv) < 2:
    sys.stderr.write('Usage: {} csv_file\n'.format(os.path.basename(sys.argv[0])))
    sys.exit()
else:
    fnam = sys.argv[1]
bnam,enam = os.path.splitext(os.path.basename(fnam))
if not os.path.exists(bnam):
    os.makedirs(bnam)
if not os.path.isdir(bnam):
    raise IOError('Error, no such directory >>> {}'.format(bnam))
gnam = os.path.join(bnam,'{}.shp'.format(bnam))
pnam = os.path.join(bnam,'{}.prj'.format(bnam))

df = pd.read_csv(fnam,comment='#')
df.columns = df.columns.str.strip()
df['Location'] = df['Location'].str.strip()
df['BunchNumber'] = df['BunchNumber'].astype(int)
df['PlotPaddy'] = df['PlotPaddy'].astype(int)
if 'EastingI' in df.columns and 'NorthingI' in df.columns:
    xcol = 'EastingI'
    ycol = 'NorthingI'
elif 'EastingG' in df.columns and 'NorthingG' in df.columns:
    xcol = 'EastingG'
    ycol = 'NorthingG'
elif 'EastingO' in df.columns and 'NorthingO' in df.columns:
    xcol = 'EastingO'
    ycol = 'NorthingO'
else:
    xcol = 'Easting'
    ycol = 'Northing'
df[xcol] = df[xcol].astype(float)
df[ycol] = df[ycol].astype(float)
with shapefile.Writer(gnam,shapefile.POINT) as fp:
    fp.field('Location','C')
    fp.field('BunchNumber','N')
    fp.field('PlotPaddy','N')
    for index,row in df.iterrows():
        #Location, BunchNumber, PlotPaddy, EastingI, NorthingI, PlantDate, Age, Tiller, BLB, Blast, Borer, Rat, Hopper, Drought
        #          11B,   1,   1,  751618.0529,  9243020.8440, 2022-01-04,    90,  45,   3,   0,  18,   0,   0,   0
        fp.point(row[xcol],row[ycol])
        fp.record(*[row['Location'],row['BunchNumber'],row['PlotPaddy']])
spatialRef = osr.SpatialReference()
spatialRef.ImportFromEPSG(32748)
spatialRef.MorphToESRI()
with open(pnam,'w') as fp:
    fp.write(spatialRef.ExportToWkt())
