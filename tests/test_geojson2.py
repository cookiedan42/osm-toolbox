from context import *

import unittest
from datetime import datetime
import json


class Test_read_write(unittest.TestCase):
    def test_import(self):
        from osm_toolbox import geojson2

    def test_read_write(self):
        from osm_toolbox import geojson2
        lon = 1
        lat = 1
        test_geoJSON = {
            "type": "FeatureCollection",
            "features": [{
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [lon, lat]
                },
                "properties": {}
            }]
        }

        test_obj = geojson2.FeatureCollection(test_geoJSON)
        geojson2.dump(test_obj, "./tests/test_data/geojsontest.geojson")
        with open("./tests/test_data/geojsontest.geojson", "r") as fp:
            assert json.load(fp) == test_geoJSON

    def test_repr(self):
        from osm_toolbox import geojson2
        lon = 1
        lat = 1
        test_geoJSON = {
            "type": "FeatureCollection",
            "features": [{
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [lon, lat]
                },
                "properties": {}
            }]
        }
        test_obj = geojson2.FeatureCollection(test_geoJSON)
        # print(list(test_obj.features())[0])
        # print(test_obj)
        
    def test_from_shape(self):
        from osm_toolbox import geojson2
        import shapely.geometry as sg
        fs = geojson2.FeatureShape.from_Shape(sg.Point(1,1),{"testVar":1,"test2":"school"})
        # fs2 = geojson2.FeatureShape({        })



if __name__ == '__main__':
    unittest.main()
