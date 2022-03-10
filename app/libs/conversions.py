from math import log, tan, radians, cos, pi


def _sec(x):
    return(1/cos(x))


def latlon_to_xyz(lat, lon, z):
    tile_count = pow(2, z)
    x = (lon + 180) / 360
    y = (1 - log(tan(radians(lat)) + _sec(radians(lat))) / pi) / 2
    return(tile_count*x, tile_count*y)