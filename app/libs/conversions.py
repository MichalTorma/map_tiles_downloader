
from math import atan, degrees, log, sinh, tan, radians, cos, pi
from pathlib import Path
import gdal
import logging
import os
import subprocess


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
        logging.info(crs)


def merge_geotiffs():
    merge_command = ['gdal_merge.py', '-o', 'output/result.tif']

    for file in Path('output/tiles').glob('*.tif'):
        merge_command.append(file.as_posix())

    subprocess.call(merge_command)
