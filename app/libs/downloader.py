import time
from urllib.error import HTTPError
import urllib.request
import os
from pathlib import Path
import logging
from libs.helper import get_url
import pandas as pd

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

def get_tile(crs: list, already_used: list,retry: int = 0):
    if(retry >= 5):
        logging.error('Unable to download {crs} - Skipping...')
        return
        # raise Exception('Tried 5 times but failed.')
    logging.debug(f'coordinates: {crs}')
    tile_file = Path('output/tiles') / \
        Path(f'{crs[0]}_{crs[1]}_{crs[2]}.png')
    if tile_file.exists():
        logging.debug(f'{tile_file.name} already exist. Skipping...')
        return
    if tile_file.name in already_used:
        logging.debug(f'{tile_file.name} is empty based on previous run. Skipping...')
        return
    try:
        _download_tile(x=crs[0], y=crs[1], z=crs[2],
                    tile_server=get_url(), temp_dir='output/tiles/',)
    except HTTPError as e:
        if e.code == 404:
            logging.debug(f'Unable to download - empty {crs} - {e}')
            already_used.append(tile_file.name)
            au_df = pd.DataFrame({'name': already_used})
            au_df.to_csv('output/already_used.csv', index=False)
        elif e.code == 502:
            logging.warning(f'Unable to download {crs} - {e}')
            logging.info('Waiting 5s...')
            time.sleep(5)
            get_tile(crs=crs, retry=retry+1)
            logging.info('Try again...')
        else:
            raise e
