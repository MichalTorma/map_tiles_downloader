
from math import atan, degrees, log, sinh, tan, radians, cos, pi
from pathlib import Path
from osgeo import gdal
import re
import logging
import os
import subprocess
import tempfile


def x_to_lon_edges(x, z):
    tile_count = pow(2, z)
    unit = 360 / tile_count
    lon1 = -180 + x * unit
    lon2 = lon1 + unit
    return(lon1, lon2)


def mercatorToLat(mercatorY):
    return(degrees(atan(sinh(mercatorY))))


def y_to_lat_edges(y, z):
    tile_count = pow(2, z)
    unit = 1 / tile_count
    relative_y1 = y * unit
    relative_y2 = relative_y1 + unit
    lat1 = mercatorToLat(pi * (1 - 2 * relative_y1))
    lat2 = mercatorToLat(pi * (1 - 2 * relative_y2))
    return(lat1, lat2)


def tile_edges(x, y, z):
    lat1, lat2 = y_to_lat_edges(y, z)
    lon1, lon2 = x_to_lon_edges(x, z)
    return[lon1, lat1, lon2, lat2]


def georeference_raster_tile(x, y, z, path: Path):
    bounds = tile_edges(x, y, z)
    filename, _ = os.path.splitext(path.name)
    output_file = path.parent / f'{filename}.tif'
    gdal.Translate(output_file.as_posix(),
                   path.as_posix(),
                   outputSRS='EPSG:4326',
                   outputBounds=bounds)


def export_geotiffs():
    tiles = Path('output/tiles').glob('*.png')
    for tile in tiles:
        crs = re.search(r'(\d+)_(\d+)_(\d+)', tile.name).groups()
        crs = [int(x) for x in crs]
        georeference_raster_tile(x=crs[0], y=crs[1], z=crs[2], path=tile)
        logging.debug(crs)


# def merge_geotiffs():
#     merge_command = ['gdal_merge.py', '-o', 'output/result.tif',
#                      '-co',  'COMPRESS=LZW',  '-co',  'BIGTIFF=YES',
#                      '-co',  'PREDICTOR=2',  '-co',  'TILED=YES', '-co',  'SPARSE_OK=TRUE', 'output/tiles/*.tif']

#     for file in Path('output/tiles').glob('*.tif'):
#         merge_command.append(file.as_posix())

#     subprocess.call(merge_command)
# import subprocess
# from pathlib import Path
# import tempfile

import subprocess
from pathlib import Path

def merge_geotiffs():
    # Function to merge a list of files
    def merge_files(file_list, output_file):
        merge_command = ['gdal_merge.py', '-o', output_file,
                         '-co', 'COMPRESS=LZW', '-co', 'BIGTIFF=YES',
                         '-co', 'PREDICTOR=2', '-co', 'TILED=YES', '-co', 'SPARSE_OK=TRUE']
        merge_command.extend(file_list)
        result = subprocess.run(merge_command, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error merging files into {output_file}:")
            print(result.stderr)
        else:
            print(f"Successfully merged files into {output_file}")

    # Get all TIFF files
    all_tiff_files = list(Path('output/tiles').glob('*.tif'))

    # Define batch size
    batch_size = 5000

    # Merge in batches
    intermediate_files = []
    for i in range(0, len(all_tiff_files), batch_size):
        batch_files = all_tiff_files[i:i+batch_size]
        intermediate_output = f'output/intermediate_{i//batch_size}.tif'
        merge_files([file.as_posix() for file in batch_files], intermediate_output)
        intermediate_files.append(intermediate_output)

    # Merge all intermediate files into the final output
    merge_files(intermediate_files, 'output/result.tif')

    # # Cleanup intermediate files
    # for file in intermediate_files:
    #     Path(file).unlink()
