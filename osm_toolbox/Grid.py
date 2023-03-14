import shapely.geometry as sg
from shapely.ops import prep
from shapely.strtree import STRtree

from .geojson2 import FeatureCollection, FeatureShape

def divide_by_grid(test_features,grid_Features,grid_buffer = 0,cut = False):
    '''
    divide features according to a set of polygons

    params:
        test_features : iterable of featureShapes to be allocated
        grid_features : iterable of featureShapes or shapely objects to be the grid
        grid_buffer : size of buffer around each grid_feature to include in search 
        cut (optional): True if features should be cut off at the edge of the boundary

    return :
        dictionary key = id of grid_feature:{
            "grid": grid feature,
            "features : list of test_features included in the grid cell
        }
    '''
    # test_features is an iterable of featureShape objects
    # buffer and match IDs between grid_features and buffered_grids
    b_grids = dict()
    for grid in grid_Features:
        # gridShape = i.shape if isinstance(featureShape,geojson2.FeatureShape) else grid
        b_grid = grid.buffer(grid_buffer) if grid_buffer != 0 else grid
        entry = {
            "id": id(b_grid),
            "buffered": b_grid,
            "orig_ID" : id(grid),
            "orig_shape": grid
        }
        b_grids[entry["id"]] = entry
        

    grid_tree = STRtree([i["buffered"] for i in b_grids.values()])
    result = {id(grid):{"grid":grid,"features":[]} for grid in grid_Features}
    
    for test in test_features:
        parent_grids = grid_tree.query(test.shape)
        for p in parent_grids:
            if not test.shape.intersects(p):
                # shape only intersects bounding box, not the feature itself
                continue
            if cut == False:
                # append entire shape
                
                b_grids[id(p)]
                b_grids[id(p)]["orig_ID"]
                result[b_grids[id(p)]["orig_ID"]]

                result[b_grids[id(p)]["orig_ID"]]["features"].append(test.copy())
                continue
            if cut == True:
                test_copy = test.copy()
                test_copy.shape = test_copy.shape.intersection(p)
                test_copy.shapeID = id(test_copy.shape)
                result[b_grids[id(p)]["orig_ID"]]["features"].append(test_copy)
    return result

# export with new name
divide_by_polygon = divide_by_grid


def grid_aggregator(grid_pairs,agg_func_dict):
    # grid_pairs --> dict with {"grid":something,"features":[]} < output of divide by grid
    # agg_func_dict --> aggregator functions to use
        # key is output arg
        # value is function taking in series of featureshapes
        # output properties[key] = func(features in grid)
    # return a geojson with geometry of grid and properties of aggregated data based on agg_func_dict
    outFeatures = {}
    for gridID,data in grid_pairs.items():
        entry = { "type": "Feature",
            "geometry": sg.mapping(data["grid"]),
            "properties": {k: v(data["features"]) for k,v in agg_func_dict.items()}
        }
        outFeatures[gridID] = entry
    return outFeatures
    

# throw grids into a tree
# test points intersect against them!