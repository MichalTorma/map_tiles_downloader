import urllib.request
import os
from pathlib import Path
import logging

def _download_tile(x: int, y: int, z: int, tile_server: str, temp_dir: Path):
    url = tile_server.replace(
        "{x}", str(x)).replace(
        "{y}", str(y)).replace(
        "{z}", str(z))
    path = temp_dir / Path(f'{x}_{y}_{z}.png')
    logging.debug(f'Downloading x:{x} y:{y} z:{z}')
    logging.debug(f'URL: {url}')
    urllib.request.urlretrieve(url, path)
    return(path)

def get_tile(crs: list):
    logging.debug(f'coordinates: {crs}')
    tile_file = Path('output/tiles') / \
        Path(f'{crs[0]}_{crs[1]}_{crs[2]}.png')
    if tile_file.exists():
        return
    try:
        _download_tile(x=crs[0], y=crs[1], z=crs[2],
                    tile_server=get_url(), temp_dir='output/tiles/',)
    except:
        logging.debug(f'Unable to download {crs}')
        pass