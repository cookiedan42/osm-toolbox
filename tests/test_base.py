import osm_toolbox
import unittest
from datetime import datetime

class Test_base(unittest.TestCase):
    def test_timeStamps(self):
        from osm_toolbox import sg_govt
        dt = datetime.strptime("2021/01/01 11:11:11+00:00", "%Y/%m/%d %H:%M:%S%z")
        d2 = sg_govt.datetime_to_timestamp(dt)
        d3 = sg_govt.timestamp_to_datetime(d2)
        self.assertEqual(dt,d3)

if __name__ == '__main__':
    unittest.main()