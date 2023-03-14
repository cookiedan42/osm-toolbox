'''
augmented shapely STR-packed R-tree
returns featureShape objects instead of shape objects or IDs!
'''
from shapely.strtree import STRtree as shapely_STRtree

class STRtree:
    # contains a shapely str tree for shapes
    # contains a lookup table for properties
    # return results of lookup table when needed

    def __init__(self,arr):
        '''
        take in an iterable of featureShapes to populate the R-tree
        '''
        self.lookup = {v.shapeID:v.copy() for v in arr}
        self.tree = shapely_STRtree([v.shape for v in self.lookup.values()])


    def query(self,test_feature,strict=False):
        '''
        query tree_features that intersect test_feature
        use bounding box if strict == False
        uses intersect if strict == True
        '''
        shapes = self.tree.query(test_feature.shape)

        if strict:
            shapes = [i for i in shapes if i.intersects(test_feature.shape)]
        shapeIDs = [id(i) for i in shapes]
        return [self.lookup[i].copy() for i in shapeIDs]


    def nearest(self,test_feature):
        '''
        return the nearest tree_feature to test_feature
        '''
        shape = self.tree.nearest(test_feature.shape)
        shapeID = id(shape)
        return self.lookup[shapeID].copy()