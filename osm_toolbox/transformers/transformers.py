from shapely.ops import transform
from typing import Any
import pyproj



svy21 = pyproj.CRS("EPSG:3414")
wgs84 = pyproj.CRS('EPSG:4326')


# use static definitions to avoid recomputation
# perfomance gain of 400 seconds to <1 second when transforming 5012 bus stops
__wgs84_svy21_ = pyproj.Transformer.from_crs(wgs84, svy21, always_xy=True).transform
def coord_wgs84_svy21(xx: Any, yy: Any,*args,**kwargs):
    '''
    pyproj Transformer.transform locked to wgs84 -> svy21
    '''
    return __wgs84_svy21_(xx,yy,*args,**kwargs)

# transform x,y coords
def shapely_wgs84_svy21(shape):
    '''
    take   a shapely object in wgs84 projection
    return a shapely object in svy21 projection 
    '''
    return transform(coord_wgs84_svy21, shape)


__svy21_wgs84_ = pyproj.Transformer.from_crs( svy21, wgs84, always_xy=True).transform
def coord_svy21_wgs84(xx: Any, yy: Any,*args,**kwargs):
    '''
    pyproj Transformer.transform locked to svy21 -> wgs84
    '''
    return __svy21_wgs84_(xx,yy,*args,**kwargs)

def shapely_svy21_wgs84(shape):
    '''
    take   a shapely object in svy21 projection
    return a shapely object in wgs84 projection 
    '''
    return transform(__svy21_wgs84_, shape)