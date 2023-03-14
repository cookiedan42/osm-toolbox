# import osmium
import os
import unittest
import osmium
import datetime

import shapely.geometry as sg

#TODO: add test cases for ways, areas and relations

class Test_base(unittest.TestCase):

    def test_write(self):
        from osm_toolbox.osm_pbf import PBFwriter, count_pbf_features
        testPath = "./tests/test_data/test_write.osm.pbf"

        os.makedirs("./tests/test_data",exist_ok = True) 
        with PBFwriter(testPath) as w:
            lon = 103
            lat = 1.3
            w.add_node(
                osmium.osm.mutable.Node(
                    id = 100,
                    visible= True,
                    location=(lon,lat)
                    )
                )
        # test against osm
        assert count_pbf_features(testPath)["nodes"] == 1


    def test_proximity(self):
        from osm_toolbox.osm_pbf import PBFwriter, Proximity_Filter
        testPath = "./tests/test_data/test_proximity.osm.pbf"

        os.makedirs("./tests/test_data",exist_ok = True) 
        with PBFwriter(testPath) as w:
            for lon in range(10):
                for lat in range(10):            
                    w.add_node(
                        osmium.osm.mutable.Node(
                            id = lon*100 + lat,
                            location=(lon,lat)
                            )
                        )
        # test against osm
        result = Proximity_Filter([sg.Point(5,5)],0.1,{"node"}).filter(testPath)
        assert result["node"] == {505}

        result = Proximity_Filter([sg.Point(5,5)],1.001,{"node"}).filter(testPath)
        print(result)
        assert result["node"] == {505,405,504,605,506}

    def test_proximity_projection(self):
        #TODO: use proper coordinate range that applies to svy21
 
        from osm_toolbox.osm_pbf import PBFwriter, Proximity_Filter
        from osm_toolbox.transformers import shapely_wgs84_svy21
        testPath = "./tests/test_data/test_proximity.osm.pbf"

        os.makedirs("./tests/test_data",exist_ok = True) 
        with PBFwriter(testPath) as w:
            for lon in range(10):
                for lat in range(10):            
                    w.add_node(
                        osmium.osm.mutable.Node(
                            id = lon*100 + lat,
                            location=(lon,lat)
                            )
                        )
        # test against osm
        result = Proximity_Filter(
            [shapely_wgs84_svy21(sg.Point(5,5))]
            ,1
            ,{"node"}
            ,transform_Func=shapely_wgs84_svy21
        ).filter(testPath)
        assert result["node"] == {505}
        # result = Proximity_Filter([shapely_wgs84_svy21(sg.Point(5,5))],1,{"node"},transform_Func=shapely_wgs84_svy21).filter(testPath)
        # assert result["node"] == {505,405,504,605,506}


if __name__ == '__main__':
    unittest.main()
