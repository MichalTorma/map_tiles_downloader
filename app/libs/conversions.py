
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
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def merge_files(file_list, output_file):
    logging.info(f"Merging {len(file_list)} files into {output_file}...")
    merge_command = ['gdal_merge.py', '-o', output_file,
                     '-co', 'COMPRESS=LZW', '-co', 'BIGTIFF=YES',
                     '-co', 'PREDICTOR=2', '-co', 'TILED=YES', '-co', 'SPARSE_OK=TRUE']
    merge_command.extend(file_list)
    result = subprocess.run(merge_command, capture_output=True, text=True)
    if result.returncode != 0:
        logging.error(f"Error merging files into {output_file}: {result.stderr}")
    else:
        logging.info(f"Successfully merged files into {output_file}")

def merge_geotiffs():
    logging.info("Starting the merge process...")

    # Get all TIFF files
    all_tiff_files = list(Path('output/tiles').glob('*.tif'))
    logging.info(f"Found {len(all_tiff_files)} GeoTIFF files to merge.")

    # Group files by Y coordinate
    files_by_y = {}
    for file in all_tiff_files:
        _, y, _ = file.stem.split('_')
        if y not in files_by_y:
            files_by_y[y] = []
        files_by_y[y].append(file)

    # Merge files by rows (Y axis)
    intermediate_files_by_y = []
    for y, files in files_by_y.items():
        intermediate_output_y = f'output/intermediate_y_{y}.tif'
        logging.info(f"Processing Y-coordinate group {y} with {len(files)} files.")
        merge_files([file.as_posix() for file in files], intermediate_output_y)
        intermediate_files_by_y.append(intermediate_output_y)

    # Merge all intermediate Y files into the final output
    logging.info(f"Merging {len(intermediate_files_by_y)} intermediate files into the final output.")
    merge_files(intermediate_files_by_y, 'output/result.tif')

    logging.info("Merge process completed.")

    # Cleanup intermediate files (uncomment if needed)
    # for file in intermediate_files_by_y:
    #     Path(file).unlink()

if __name__ == "__main__":
    merge_geotiffs()
