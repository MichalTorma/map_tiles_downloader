# Inspired by https://jimmyutterstrom.com/blog/2019/06/05/map-tiles-to-geotiff/
# %%
import logging
import os
import re
from pathlib import Path

from tqdm.notebook import tqdm

from libs.conversions import export_geotiffs, merge_geotiffs
from libs.downloader import get_tile
from libs.helper import (generate_tiles, get_bounds_string_of_input,
                         get_input_polygon, get_xyz, load_tiles)

tqdm.pandas()


# %%
logging.basicConfig(level=logging.INFO)
# %%


def main():
    logging.info('Get input polygon')
    input_polygon = get_input_polygon()
    bounds_string = get_bounds_string_of_input(input_polygon=input_polygon)
    zoom = int(os.environ['ZOOM'])
    logging.info('Generate tiles...')
    generate_tiles(zoom=zoom, bounds_string=bounds_string)
    logging.info('Clip tiles')
    tiles = load_tiles()
    clipped_tiles = tiles.clip(input_polygon)
    logging.info('Extract coordinates')
    clipped_tiles['crs'] = clipped_tiles.id.apply(get_xyz)
    logging.info('Start downloading...')
    clipped_tiles['crs'].progress_apply(lambda x: get_tile(x))
    # for (idx, crs) in clipped_tiles['crs'].iteritems():

    logging.info('Download finished, converting to geotiffs...')
    export_geotiffs()
    logging.info('Finished exporting, merging the result...')
    merge_geotiffs()
    logging.info('Finished.')
    return


# %%
if __name__ == '__main__':
    main()
# %%
# %%
