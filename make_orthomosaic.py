import os
import sys
import time
import Metashape
from argparse import ArgumentParser,RawTextHelpFormatter

# Defaults
QMIN = 0.5
EPSG = 32748 # UTM zone 48S

# Read options
parser = ArgumentParser(formatter_class=lambda prog:RawTextHelpFormatter(prog,max_help_position=200,width=200))
parser.add_argument('-I','--inp_dnam',default=None,help='Input folder name (%(default)s)')
parser.add_argument('-O','--out_dnam',default=None,help='Output folder name (%(default)s)')
parser.add_argument('--panel_fnam',default=None,help='Panel reflectance file name (%(default)s)')
parser.add_argument('-q','--qmin',default=QMIN,type=float,help='Min image quality (%(default)s)')
parser.add_argument('-E','--epsg',default=EPSG,type=int,help='Output EPSG (%(default)s)')
args = parser.parse_args()

# Checking compatibility
compatible_major_version = '1.7'
found_major_version = '.'.join(Metashape.app.version.split('.')[:2])
if found_major_version != compatible_major_version:
    raise Exception('Incompatible Metashape version: {} != {}'.format(found_major_version,compatible_major_version))

def find_files(folder,types):
    return [entry.path for entry in os.scandir(folder) if (entry.is_file() and os.path.splitext(entry.name)[1].lower() in types)]

if len(sys.argv) < 3:
    sys.stderr.write('Usage: general_workflow.py <image_folder> <output_folder>\n')
    sys.exit(1)

image_folder = sys.argv[1]
output_folder = sys.argv[2]

photos = find_files(image_folder,['.jpg','.jpeg','.tif','.tiff'])

doc = Metashape.Document()
Metashape.app.gpu_mask = 1
Metashape.app.cpu_enable = True
doc.save(output_folder+'/project.psx')

chunk = doc.addChunk()

chunk.addPhotos(photos,layout=Metashape.MultiplaneLayout,strip_extensions=True,load_xmp_calibration=True,load_xmp_orientation=True,load_xmp_accuracy=True,load_xmp_antenna=True,load_rpc_txt=True)
doc.save()

sys.stderr.write(str(len(chunk.cameras))+' images loaded\n')

for sensor in doc.chunk.sensors:
    sensor.fixed_params=['F','Cx','Cy','K1','K2','K3','P1','P2']

chunk.calibrateReflectance(use_reflectance_panels=False,use_sun_sensor=True)
doc.save()

chunk.matchPhotos(downscale=1,generic_preselection=False,reference_preselection=True,reference_preselection_mode=Metashape.ReferencePreselectionSource,reset_matches=True,keypoint_limit=40000,tiepoint_limit=4000,mask_tiepoints=False,guided_matching=False)
doc.save()

chunk.alignCameras(adaptive_fitting=False,reset_alignment=True)
doc.save()

#chunk.optimizeCameras(fit_f=True,fit_k1=True,fit_k2=True,fit_k3=True,
#fit_k4=False,fit_cx=True,fit_cy=True,fit_p1=True,fit_p2=True,fit_b1=False,
#fit_b2=False,adaptive_fitting=False,tiepoint_covariance=False,fit_corrections=True)
#doc.save()

chunk.buildDepthMaps(downscale=4,filter_mode=Metashape.AggressiveFiltering,reuse_depth=True)
doc.save()

#chunk.buildModel(source_data=Metashape.DepthMapsData)
#doc.save()

#chunk.buildUV(page_count=2,texture_size=4096)
#doc.save()

#chunk.buildTexture(size=4096,ghosting_filter=True)
#doc.save()

has_transform=chunk.transform.scale and chunk.transform.rotation and chunk.transform.translation

if has_transform:
    chunk.buildDenseCloud(point_colors=True,point_confidence=True)
    doc.save()

    proj = Metashape.OrthoProjection()
    proj.crs = Metashape.CoordinateSystem('EPSG::32748')
    chunk.buildDem(source_data=Metashape.DenseCloudData,projection=proj,interpolation=Metashape.EnabledInterpolation)
    doc.save()

    chunk.buildOrthomosaic(surface_data=Metashape.ElevationData,projection=proj,blending_mode=Metashape.MosaicBlending,refine_seamlines=False,fill_holes=True,cull_faces=False)
    doc.save()

# export results
chunk.exportReport(output_folder+'/report.pdf')

#if chunk.model:
#    chunk.exportModel(output_folder+'/model.obj')

#if chunk.dense_cloud:
#    chunk.exportPoints(output_folder+'/dense_cloud.las',source_data=Metashape.DenseCloudData)

#if chunk.elevation:
#    chunk.exportRaster(output_folder+'/dem.tif',source_data=Metashape.ElevationData)

if chunk.orthomosaic:
    chunk.exportRaster(output_folder+'/orthomosaic.tif',source_data=Metashape.OrthomosaicData)

sys.stderr.write('Processing finished, results saved to '+output_folder+'.\n')
