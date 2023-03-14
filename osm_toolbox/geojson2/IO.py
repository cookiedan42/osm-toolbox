from .FeatureCollection import FeatureCollection
import json
'''
functions to import geojson files into FeatureCollection Objects 
and to export FeatureCollection Objects to geojson files
'''

def load(filePath) -> FeatureCollection:
    '''
    load a geoJSON file as a FeatureCollection
    '''
    with open(filePath, "r") as fp:
        return FeatureCollection(json.load(fp))


def dump(data: FeatureCollection, filePath):
    '''
    write  a FeatureCollection object to file
    '''
    with open(filePath, "w") as fp:
        json.dump(data.to_geojson(), fp)
