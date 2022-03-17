import time
from urllib.error import HTTPError
import urllib.request
import os
from pathlib import Path
import logging
from libs.helper import get_url

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

def get_tile(crs: list, retry: int = 0):
    if(retry >= 5):
        logging.error('Unable to download {crs} - Skipping...')
        return
        # raise Exception('Tried 5 times but failed.')
    logging.debug(f'coordinates: {crs}')
    tile_file = Path('output/tiles') / \
        Path(f'{crs[0]}_{crs[1]}_{crs[2]}.png')
    if tile_file.exists():
        return
    try:
        _download_tile(x=crs[0], y=crs[1], z=crs[2],
                    tile_server=get_url(), temp_dir='output/tiles/',)
    except HTTPError as e:
        if e.code == 404:
            logging.debug(f'Unable to download {crs} - {e}')
        elif e.code == 502:
            logging.warning(f'Unable to download {crs} - {e}')
            logging.info('Waiting 5s...')
            time.sleep(5)
            get_tile(crs=crs, retry=retry+1)
            logging.info('Try again...')
        else:
            raise e
