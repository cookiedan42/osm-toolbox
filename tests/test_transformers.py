# from context import *
import unittest
import osm_toolbox.transformers as transformers
import pyproj

class Test_import(unittest.TestCase):

    def coord_transformers(self):
        # import osm_toolbox
        x,y = 103.8,1.3
        ref = (pyproj.Transformer 
            .from_crs(
                pyproj.CRS('EPSG:4326'), 
                pyproj.CRS("EPSG:3414"), 
                always_xy=True)
            .transform(x,y))
        test = transformers.coord_wgs84_svy21(x,y)
        assert ref == test


        x,y = 103.8,1.3

        ref = (pyproj.Transformer 
            .from_crs(
                pyproj.CRS("EPSG:3414"), 
                pyproj.CRS('EPSG:4326'), 
                always_xy=True)
            .transform(x,y))
        test = transformers.coord_svy21_wgs84(x,y)
        assert ref == test


    def point_transform(self):
        pass

    def line_transform(self):
        pass

    def polygon_transform(self):
        pass