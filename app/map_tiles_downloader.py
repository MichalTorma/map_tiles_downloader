# Inspired by https://jimmyutterstrom.com/blog/2019/06/05/map-tiles-to-geotiff/ 
#%%
from libs.conversions import latlon_to_xyz
from libs.downloader import download_tile
import os
import subprocess
import geopandas as gpd
from glob import glob
#%%
def generate_tiles(zoom: int, bounds_string: str):
    command = f"echo \"{bounds_string}\" | mercantile tiles {zoom} | mercantile shapes > ~/app/tiles{os.sep}tiles.geojson"
    subprocess.run(command, shell=True, check=True)

# def get_tiles(zoom: int):
# %%
def get_input_polygon():
    files = glob('./input/*.geojson')
    if len(files) != 1:
        raise Exception('Exactly one geojson input file should be in the input')
    file = files[0]
    input = gpd.read_file(file)
    if len(input) != 1:
        raise Exception('Only one (multi)polygon allowed in the input geojson file')
    return input
# %%
def get_bounds_string_of_input(input_polygon):
    input_geometry = input_polygon.iloc[0].geometry
    b = input_geometry.bounds
    bounds_string = f'[{b[0]}, {b[1]}, {b[2]}, {b[3]}]'
    return bounds_string

# %%
def load_tiles():
    return gpd.read_file('./tiles/tiles.geojson')
# %%
def main():
    input_polygon = get_input_polygon()
    bounds_string = get_bounds_string_of_input(input_polygon=input_polygon)
    zoom = int(os.environ['ZOOM'])
    generate_tiles(zoom=zoom, bounds_string=bounds_string)
    tiles = load_tiles()
    res = tiles.clip(input_polygon)
    return res, tiles

# %%
