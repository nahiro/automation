import os
import sys
import time
#import Metashape
from argparse import ArgumentParser,RawTextHelpFormatter

# Constants
METASHAPE_VERSION = '1.7'
DOWNSCALE = {'High':1,'Midium':4,'Low':16}
ALIGN_LEVELS = ['High','Medium','Low']
FILTER_MODES = ['None','Mild','Moderate','Aggressive']
FILTER = {'None':Metashape.NoFiltering,
          'Mild':Metashape.MildFiltering,
          'Moderate':Metashape.ModerateFiltering,
          'Aggressive':Metashape.AggressiveFiltering}
CAMERA_PARAMS = ['f','k1','k2','k3','k4','cx','cy','p1','p2','b1','b2']
DEPTH_MAP_QUALITIES = ['High','Medium','Low']
OUTPUT_TYPES = ['UInt16','Int16','Float32']

# Defaults
QMIN = 0.5
ALIGN_LEVEL = 'High'
KEY_LIMIT = 40000
TIE_LIMIT = 4000
CAMERA_PARAM = ['f','k1','k2','k3','cx','cy','p1','p2']
DEPTH_MAP_QUALITY = 'Medium'
FILTER_MODE = 'Aggressive'
EPSG = 32748 # UTM zone 48S
PIXEL_SIZE = 0.025 # m
SCALE_FACTOR = 1.0
OUTPUT_TYPE = 'Float32'

# Read options
parser = ArgumentParser(formatter_class=lambda prog:RawTextHelpFormatter(prog,max_help_position=200,width=200))
parser.add_argument('-I','--inp_dnam',default=None,help='Input folder name (%(default)s)')
parser.add_argument('-O','--out_dnam',default=None,help='Output folder name (%(default)s)')
parser.add_argument('--panel_fnam',default=None,help='Panel reflectance file name (%(default)s)')
parser.add_argument('-q','--qmin',default=QMIN,type=float,help='Min image quality (%(default)s)')
parser.add_argument('--align_level',default=ALIGN_LEVEL,help='Image alignment accuracy (%(default)s)')
parser.add_argument('-l','--key_limit',default=KEY_LIMIT,type=int,help='Keypoint limit (%(default)s)')
parser.add_argument('-L','--tie_limit',default=TIE_LIMIT,type=int,help='Tiepoint limit (%(default)s)')
parser.add_argument('--camera_param',default=None,action='append',help='Camera model parameter ({})'.format(CAMERA_PARAM))
parser.add_argument('--depth_map_quality',default=DEPTH_MAP_QUALITY,help='Depth map quality (%(default)s)')
parser.add_argument('--filter_mode',default=FILTER_MODE,help='Depth map filtering mode (%(default)s)')
parser.add_argument('-E','--epsg',default=EPSG,type=int,help='Output EPSG (%(default)s)')
parser.add_argument('-s','--pixel_size',default=PIXEL_SIZE,type=float,help='Pixel size in m (%(default)s)')
parser.add_argument('-f','--scale_factor',default=SCALE_FACTOR,type=float,help='Scale factor (%(default)s)')
parser.add_argument('-o','--output_type',default=OUTPUT_TYPE,help='Output type (%(default)s)')
parser.add_argument('--use_panel',default=False,action='store_true',help='Use reflectance panel (%(default)s)')
parser.add_argument('--ignore_sunsensor',default=False,action='store_true',help='Ignore sun sensor (%(default)s)')
parser.add_argument('--ignore_xmp_calibration',default=False,action='store_true',help='Ignore calibration in XMP meta data (%(default)s)')
parser.add_argument('--ignore_xmp_orientation',default=False,action='store_true',help='Ignore orientation in XMP meta data (%(default)s)')
parser.add_argument('--ignore_xmp_accuracy',default=False,action='store_true',help='Ignore accuracy in XMP meta data (%(default)s)')
parser.add_argument('--ignore_xmp_antenna',default=False,action='store_true',help='Ignore GPS/INS offset in XMP meta data (%(default)s)')
parser.add_argument('--disable_generic_preselection',default=False,action='store_true',help='Disable generic preselection (%(default)s)')
parser.add_argument('--disable_reference_preselection',default=False,action='store_true',help='Disable reference preselection (%(default)s)')
parser.add_argument('--disable_camera_optimization',default=False,action='store_true',help='Disable camera optimization (%(default)s)')
parser.add_argument('--adaptive_fitting_align',default=False,action='store_true',help='Adaptive fitting during align cameras (%(default)s)')
parser.add_argument('--adaptive_fitting_optimize',default=False,action='store_true',help='Adaptive fitting during optimize cameras (%(default)s)')
args = parser.parse_args()
if not args.align_level in ALIGN_LEVELS:
    raise ValueError('Error, unsupported alignment accuracy >>> {}'.format(args.align_level))
if args.camera_param is None:
    args.camera_param = CAMERA_PARAM
for param in args.camera_param:
    if not param in CAMERA_PARAMS:
        raise ValueError('Error, unknown camera model parameter >>> {}'.format(param))
if not args.depth_map_quality in DEPTH_MAP_QUALITIES:
    raise ValueError('Error, unsupported depth map quality >>> {}'.format(args.depth_map_quality))
if not args.filter_mode in FILTER_MODES:
    raise ValueError('Error, unknown depth map filter mode >>> {}'.format(args.filter_mode))
if not args.output_type in OUTPUT_TYPES:
    raise ValueError('Error, unsupported output type >>> {}'.format(args.output_type))

# Checking compatibility
compatible_major_version = METASHAPE_VERSION
found_major_version = '.'.join(Metashape.app.version.split('.')[:2])
if found_major_version != compatible_major_version:
    raise Exception('Incompatible Metashape version: {} != {}'.format(found_major_version,compatible_major_version))

def find_files(folder,types):
    return [entry.path for entry in os.scandir(folder) if (entry.is_file() and os.path.splitext(entry.name)[1].lower() in types)]

image_folder = sys.argv[1]
output_folder = sys.argv[2]

photos = find_files(image_folder,['.jpg','.jpeg','.tif','.tiff'])

doc = Metashape.Document()
Metashape.app.gpu_mask = 1
Metashape.app.cpu_enable = True
doc.save(os.path.join(args.out_dnam,'project.psx'))

chunk = doc.addChunk()

chunk.addPhotos(photos,
                layout=Metashape.MultiplaneLayout,
                strip_extensions=True,
                load_xmp_calibration=not args.ignore_xmp_calibrationTrue,
                load_xmp_orientation=not args.ignore_xmp_orientation,
                load_xmp_accuracy=not args.ignore_xmp_accuracy,
                load_xmp_antenna=not args.ignore_xmp_antenna,
                load_rpc_txt=True)
doc.save()

sys.stderr.write(str(len(chunk.cameras))+' images loaded\n')

chunk.estimateImageQuality(cameras=chunk.cameras)
for camera in chunk.cameras:
    if float(camera.photo.meta['Image/Quality']) < args.qmin:
        camera.enabled = False

if args.disable_camera_optimization:
    params = [param.capitalize() for param in CAMERA_PARAMS]
    for sensor in doc.chunk.sensors:
        sensor.fixed_params = params
else:
    params = [param.capitalize() for param in CAMERA_PARAMS if param not in args.camera_param]
    if len(params) > 0:
        for sensor in doc.chunk.sensors:
            sensor.fixed_params = params

if args.use_panel:
    for sensor in chunk.sensors:
        sensor.normalize_sensitivity = True
    chunk.locateReflectancePanels()
    if args.panel_fnam is not None:
        chunk.loadReflectancePanelCalibration(path=args.panel_fnam)
    chunk.calibrateReflectance(use_reflectance_panels=args.use_panel,use_sun_sensor=not args.ignore_sunsensor)
else:
    chunk.calibrateReflectance(use_reflectance_panels=args.use_panel,use_sun_sensor=not args.ignore_sunsensor)
doc.save()

chunk.matchPhotos(downscale=DOWNSCALE[args.align_level],
                  generic_preselection=not args.disable_generic_preselection,
                  reference_preselection=not args.disable_reference_preselection,
                  reference_preselection_mode=Metashape.ReferencePreselectionSource,
                  reset_matches=True,
                  keypoint_limit=args.key_limit,
                  tiepoint_limit=args.tie_limit,
                  mask_tiepoints=False,
                  guided_matching=False)
doc.save()

chunk.alignCameras(adaptive_fitting=args.adaptive_fitting_align,reset_alignment=True)
doc.save()

if not args.disable_camera_optimization:
    chunk.optimizeCameras(fit_f='f' in args.camera_param,
                          fit_k1='k1' in args.camera_param,
                          fit_k2='k2' in args.camera_param,
                          fit_k3='k3' in args.camera_param,
                          fit_k4='k4' in args.camera_param,
                          fit_cx='cx' in args.camera_param,
                          fit_cy='cy' in args.camera_param,
                          fit_p1='p1' in args.camera_param,
                          fit_p2='p2' in args.camera_param,
                          fit_b1='b1' in args.camera_param,
                          fit_b2='b2' in args.camera_param,
                          adaptive_fitting=args.adaptive_fitting_optimize,
                          tiepoint_covariance=False,
                          fit_corrections=True)
    doc.save()

chunk.buildDepthMaps(downscale=DOWNSCALE[args.depth_map_quality],
                     filter_mode=FILTER[args.filter_mode],
                     reuse_depth=True)
doc.save()

#chunk.buildModel(source_data=Metashape.DepthMapsData)
#doc.save()

#chunk.buildUV(page_count=2,texture_size=4096)
#doc.save()

#chunk.buildTexture(size=4096,ghosting_filter=True)
#doc.save()

has_transform = chunk.transform.scale and chunk.transform.rotation and chunk.transform.translation

if has_transform:
    chunk.buildDenseCloud(point_colors=True,point_confidence=True)
    doc.save()

    proj = Metashape.OrthoProjection()
    proj.crs = Metashape.CoordinateSystem('EPSG::{}'.format(args.epsg))
    chunk.buildDem(source_data=Metashape.DenseCloudData,projection=proj,interpolation=Metashape.EnabledInterpolation)
    doc.save()

    chunk.buildOrthomosaic(surface_data=Metashape.ElevationData,
                           projection=proj,
                           blending_mode=Metashape.MosaicBlending,
                           refine_seamlines=False,
                           fill_holes=True,
                           cull_faces=False)
    doc.save()

# export results
chunk.exportReport(os.path.join(args.out_dnam,'report.pdf'))

#if chunk.model:
#    chunk.exportModel(os.path.join(args.out_dnam,'model.obj'))

#if chunk.dense_cloud:
#    chunk.exportPoints(os.path.join(args.out_dnam,'dense_cloud.las'),source_data=Metashape.DenseCloudData)

#if chunk.elevation:
#    chunk.exportRaster(os.path.join(args.out_dnam,'dem.tif'),source_data=Metashape.ElevationData)

if chunk.orthomosaic:
    chunk.exportRaster(os.path.join(args.out_dnam,'orthomosaic.tif'),
                       source_data=Metashape.OrthomosaicData,
                       save_alpha=False)

sys.stderr.write('Processing finished, results saved to '+args.out_dnam+'.\n')
