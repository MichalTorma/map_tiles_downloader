from importlib.resources import path
import os
from pathlib import Path
import subprocess
import geopandas as gpd
from glob import glob
import random
import re
# %%


def get_input_polygon():
    files = glob('./input/*.geojson')
    if len(files) != 1:
        raise Exception(
            'Exactly one geojson input file should be in the input')
    file = files[0]
    input = gpd.read_file(file)
    if len(input) != 1:
        raise Exception(
            'Only one (multi)polygon allowed in the input geojson file')
    return input
# %%


def get_bounds_string_of_input(input_polygon):
    input_geometry = input_polygon.iloc[0].geometry
    b = input_geometry.bounds
    bounds_string = f'[{b[0]}, {b[1]}, {b[2]}, {b[3]}]'
    return bounds_string

# %%


def load_tiles(mask):
    return gpd.read_file('/tmp/tiles.geojson', mask=mask)
# %%


def get_url():
    servers = ['a', 'b', 'c']
    server = random.choice(servers)
    url = os.environ['URL'].replace('{server}', server)
    return url

# %%


def generate_tiles(zoom: int, bounds_string: str):
    tiles_path = Path('/tmp/')
    tiles_path.mkdir(parents=True, exist_ok=True)
    tiles_file = tiles_path / 'tiles.geojson'
    command = f"echo \"{bounds_string}\" | mercantile tiles {zoom} | mercantile shapes > {tiles_file.as_posix()}"
    subprocess.run(command, shell=True, check=True)

# %%


def get_xyz(str_id: str):
    res = re.search(r'([0-9]+)\D+([0-9]+)\D+([0-9]+)', str_id)
    res_list = res.groups()
    res_list = [int(x) for x in res_list]
    return res_list
