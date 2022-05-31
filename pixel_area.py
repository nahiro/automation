#!/usr/bin/env python
import sys
try:
    import gdal
except Exception:
    from osgeo import gdal
import numpy as np
from skimage.measure import points_in_poly
import shapefile
from shapely.geometry import Point,Polygon
import matplotlib.pyplot as plt
from matplotlib.path import Path
import matplotlib.patches as patches
from matplotlib.backends.backend_pdf import PdfPages
from argparse import ArgumentParser,RawTextHelpFormatter

# Default values
DATNAM = 'pixel_area.dat'
FIGNAM = 'pixel_area.pdf'

# Read options
parser = ArgumentParser(formatter_class=lambda prog:RawTextHelpFormatter(prog,max_help_position=200,width=200))
parser.add_argument('-f','--img_fnam',default=None,help='Image file name (%(default)s)')
parser.add_argument('-s','--shp_fnam',default=None,help='Shape file name (%(default)s)')
parser.add_argument('-b','--blk_fnam',default=None,help='Block file name (%(default)s)')
parser.add_argument('-B','--block',default=None,help='Block name (%(default)s)')
parser.add_argument('--buffer',default=None,type=float,help='Buffer distance (%(default)s)')
parser.add_argument('--radius',default=None,type=float,help='Radius to be considered (%(default)s)')
parser.add_argument('--xmgn',default=None,type=float,help='X margin (%(default)s)')
parser.add_argument('--ymgn',default=None,type=float,help='Y margin (%(default)s)')
parser.add_argument('--use_index',default=False,action='store_true',help='Use index instead of OBJECTID (%(default)s)')
parser.add_argument('--use_objectid',default=False,action='store_true',help='Use OBJECTID instead of Block (%(default)s)')
parser.add_argument('-d','--debug',default=False,action='store_true',help='Debug mode (%(default)s)')
parser.add_argument('-c','--check',default=False,action='store_true',help='Check mode (%(default)s)')
parser.add_argument('-o','--datnam',default=DATNAM,help='Output data name (%(default)s)')
parser.add_argument('-F','--fignam',default=FIGNAM,help='Output figure name for debug (%(default)s)')
args = parser.parse_args()

ds = gdal.Open(args.img_fnam)
data = ds.ReadAsArray()
if ds.RasterCount < 2:
    data_shape = data.shape
else:
    data_shape = data[0].shape
data_trans = ds.GetGeoTransform() # maybe obtained from tif_tags['ModelTransformationTag']
data_xmin = data_trans[0]
data_xstp = data_trans[1]
data_xmax = data_xmin+data_xstp*data_shape[1]
data_ymax = data_trans[3]
data_ystp = data_trans[5]
data_ymin = data_ymax+data_ystp*data_shape[0]
indy,indx = np.indices(data_shape)
xp = data_trans[0]+(indx+0.5)*data_trans[1]+(indy+0.5)*data_trans[2]
yp = data_trans[3]+(indx+0.5)*data_trans[4]+(indy+0.5)*data_trans[5]
data_points = np.hstack((xp.reshape(-1,1),yp.reshape(-1,1)))
ds = None
xstp = abs(data_xstp)
ystp = abs(data_ystp)
xhlf = 0.5*xstp
yhlf = 0.5*ystp
pixel_area = xstp*ystp
if args.radius is None:
    args.radius = max(xstp,ystp)
if args.xmgn is None:
    args.xmgn = xstp*6.0
if args.ymgn is None:
    args.ymgn = ystp*6.0

r = shapefile.Reader(args.shp_fnam)

if args.blk_fnam is not None:
    block = {}
    with open(args.blk_fnam,'r') as fp:
        for line in fp:
            item = line.split()
            block.update({int(item[0]):item[1]})
    if len(block) != len(r):
        raise ValueError('Error, len(block)={}, len(r)={}'.format(len(block),len(r)))

if args.debug or args.check:
    plt.interactive(True)
    fig = plt.figure(1,facecolor='w',figsize=(6,3.5))
    plt.subplots_adjust(top=0.85,bottom=0.20,left=0.15,right=0.95)
    pdf = PdfPages(args.fignam)
with open(args.datnam,'w') as fp:
    for ii,shaperec in enumerate(r.iterShapeRecords()):
        #if ii%100 == 0:
        #    sys.stderr.write('{}\n'.format(ii))
        #    sys.stderr.flush()
        rec = shaperec.record
        shp = shaperec.shape
        if args.use_index:
            object_id = ii+1
        else:
            object_id = rec.OBJECTID
        if len(shp.points) < 1:
            sys.stderr.write('Warning, len(shp.points)={}, ii={}\n'.format(len(shp.points),ii))
            continue
        path_original = Path(shp.points)
        if args.buffer is not None:
            poly_buffer = Polygon(shp.points).buffer(args.buffer)
        else:
            poly_buffer = Polygon(shp.points)
        if poly_buffer.area <= 0.0:
            sys.stderr.write('Warning, poly_buffer.area={} >>> FID {}, OBJECTID {}\n'.format(poly_buffer.area,ii,object_id))
            continue
        xmin_buffer,ymin_buffer,xmax_buffer,ymax_buffer = poly_buffer.bounds
        if (xmin_buffer > data_xmax+args.radius) or (xmax_buffer < data_xmin-args.radius) or (ymin_buffer > data_ymax+args.radius) or (ymax_buffer < data_ymin-args.radius):
            continue
        flags = []
        flags_within = np.full(data_shape,False)
        path_search = []
        if poly_buffer.type == 'MultiPolygon':
            sys.stderr.write('Warning, poly_buffer.type={} >>> FID {}, OBJECTID {}\n'.format(poly_buffer.type,ii,object_id))
            for p in poly_buffer:
                p_search = np.array(p.buffer(args.radius).exterior.coords.xy).swapaxes(0,1)
                path_search.append(p_search)
                if len(flags) < 1:
                    flags = points_in_poly(data_points,p_search).reshape(data_shape)
                else:
                    flags |= points_in_poly(data_points,p_search).reshape(data_shape)
                if p.area > pixel_area*100:
                    poly_within = p.buffer(-args.radius)
                    if poly_within.area <= 0.0:
                        pass
                    elif poly_within.type == 'MultiPolygon':
                        for p2 in poly_within:
                            p_within = np.array(p2.exterior.coords.xy).swapaxes(0,1)
                            flags_within |= points_in_poly(data_points,p_within).reshape(data_shape)
                    else:
                        path_within = np.array(poly_within.exterior.coords.xy).swapaxes(0,1)
                        flags_within |= points_in_poly(data_points,path_within).reshape(data_shape)
        else:
            path_search = np.array(poly_buffer.buffer(args.radius).exterior.coords.xy).swapaxes(0,1)
            flags = points_in_poly(data_points,path_search).reshape(data_shape)
            if poly_buffer.area > pixel_area*100:
                poly_within = poly_buffer.buffer(-args.radius)
                if poly_within.area <= 0.0:
                    pass
                elif poly_within.type == 'MultiPolygon':
                    for p in poly_within:
                        p_within = np.array(p.exterior.coords.xy).swapaxes(0,1)
                        flags_within |= points_in_poly(data_points,p_within).reshape(data_shape)
                else:
                    path_within = np.array(poly_within.exterior.coords.xy).swapaxes(0,1)
                    flags_within |= points_in_poly(data_points,path_within).reshape(data_shape)
        if args.debug or args.check:
            flags_inside = []
            flags_near = []
            path_pixels = []
        inds = []
        rats = []
        err = False
        for ix,iy in zip(indx[flags],indy[flags]):
            if flags_within[iy,ix]:
                inds.append(np.ravel_multi_index((iy,ix),data_shape))
                rats.append(1.0)
                if args.debug or args.check:
                    flags_inside.append(True)
                    flags_near.append(True)
                    xc = xp[iy,ix]
                    yc = yp[iy,ix]
                    path_pixel = Path([(xc-xhlf,yc-yhlf),(xc-xhlf,yc+yhlf),(xc+xhlf,yc+yhlf),(xc+xhlf,yc-yhlf),(xc-xhlf,yc-yhlf)])
                    path_pixels.append(path_pixel)
            else:
                xc = xp[iy,ix]
                yc = yp[iy,ix]
                pc = Point(xc,yc)
                poly_pixel = Polygon([(xc-xhlf,yc-yhlf),(xc-xhlf,yc+yhlf),(xc+xhlf,yc+yhlf),(xc+xhlf,yc-yhlf),(xc-xhlf,yc-yhlf)])
                try:
                    poly_intersect = poly_buffer.intersection(poly_pixel)
                except Exception:
                    sys.stderr.write('Warning, error occured at (ix,iy)=({},{}), ii={}\n'.format(ix,iy,ii))
                    err = True
                    continue
                rat = poly_intersect.area/poly_pixel.area
                if rat > 1.0e-10:
                    inds.append(np.ravel_multi_index((iy,ix),data_shape))
                    rats.append(rat)
                if args.debug or args.check:
                    flags_inside.append(pc.within(poly_buffer))
                    flags_near.append(rat > 1.0e-10)
                    path_pixel = Path([(xc-xhlf,yc-yhlf),(xc-xhlf,yc+yhlf),(xc+xhlf,yc+yhlf),(xc+xhlf,yc-yhlf),(xc-xhlf,yc-yhlf)])
                    path_pixels.append(path_pixel)
        if err:
            continue
        inds = np.array(inds)
        rats = np.array(rats)
        x1,y1,x2,y2 = shp.bbox
        xctr = 0.5*(x1+x2)
        yctr = 0.5*(y1+y2)
        ictr = np.argmin(np.square(xp-xctr)+np.square(yp-yctr))
        if not ictr in inds:
            sys.stderr.write('Warning, center pixel is not included >>> FID: {}, OBJECTID: {}\n'.format(ii,object_id))
        # output results ###
        if args.use_objectid:
            fp.write('{} {} {}'.format(object_id,object_id,len(inds)))
        elif args.blk_fnam is not None:
            fp.write('{} {} {}'.format(object_id,block[object_id],len(inds)))
        elif args.block is not None:
            fp.write('{} {} {}'.format(object_id,args.block,len(inds)))
        else:
            fp.write('{} {}'.format(object_id,len(inds)))
        isort = np.argsort(rats)[::-1]
        for ind,rat in zip(inds[isort],rats[isort]):
            fp.write(' {:d} {:.6e}'.format(ind,rat))
        fp.write('\n')
        ####################
        if args.debug or (args.check and not ictr in inds):
            fig.clear()
            ax1 = plt.subplot(111)
            ax1.set_title('OBJECTID: {}'.format(object_id))
            for path_pixel in path_pixels:
                patch = patches.PathPatch(path_pixel,facecolor='none',lw=1)
                ax1.add_patch(patch)
            patch = patches.PathPatch(path_original,facecolor='none',lw=2)
            ax1.add_patch(patch)
            if poly_buffer.area <= 0.0:
                pass
            elif poly_buffer.type == 'MultiPolygon':
                for p_search in path_search:
                    patch = patches.PathPatch(Path(p_search),facecolor='none',lw=2,ls='--')
                    ax1.add_patch(patch)
            else:
                patch = patches.PathPatch(Path(path_search),facecolor='none',lw=2,ls='--')
                ax1.add_patch(patch)
            if args.buffer is not None:
                if poly_buffer.area <= 0.0:
                    pass
                elif poly_buffer.type == 'MultiPolygon':
                    for p in poly_buffer:
                        p_buffer = Path(np.array(p.exterior.coords.xy).swapaxes(0,1))
                        patch = patches.PathPatch(p_buffer,facecolor='none',edgecolor='#888888',lw=2)
                        ax1.add_patch(patch)
                else:
                    path_buffer = Path(np.array(poly_buffer.exterior.coords.xy).swapaxes(0,1))
                    patch = patches.PathPatch(path_buffer,facecolor='none',edgecolor='#888888',lw=2)
                    ax1.add_patch(patch)
            ax1.plot(xp,yp,'o',color='#888888')
            for j,(x,y) in enumerate(zip(xp[flags],yp[flags])):
                if flags_inside[j]:
                    ax1.plot(x,y,'ro')
                elif flags_near[j]:
                    ax1.plot(x,y,'mo')
                ax1.text(x,y,str(j),ha='center',va='center')
            ax1.plot([xctr],[yctr],'rx',ms=10)
            xmin = 1.0e10
            xmax = -1.0e10
            ymin = 1.0e10
            ymax = -1.0e10
            for pp in shp.points:
                ax1.plot(pp[0],pp[1],'bo')
                xmin = min(xmin,pp[0])
                xmax = max(xmax,pp[0])
                ymin = min(ymin,pp[1])
                ymax = max(ymax,pp[1])
            ax1.set_xlim(xmin-args.xmgn,xmax+args.xmgn)
            ax1.set_ylim(ymin-args.ymgn,ymax+args.ymgn)
            ax1.ticklabel_format(useOffset=False,style='plain')
            plt.savefig(pdf,format='pdf')
            plt.draw()
            plt.pause(0.1)
if args.debug or args.check:
    pdf.close()
