import json
import osmium as osm
from typing import Dict
from collections.abc import Iterable

# from .. import 
# general togeoJSON
'''
1) check all areas
1.1) from way --> extract tags, draw polygon on next pass
1.2...) from relation --> recurse members

2) areas 2
2.1) write areas and mark for exclusion in next passes

3.1) for remaining ways --> get path
3.2 ) for multi lines ><
'''


def writeGeoJSON(features: Iterable, destPath: str):
    '''
    take in an iterable of feature dictionaries formatted for geojson
    write features to a geojson file as destPath
    '''
    
    with open(destPath, "w") as fp:
        json.dump({
            "type": "FeatureCollection",
            "features": list(features)
        }, fp)


def node_to_point(sourcePath: str, destPath: str = None, whitelistIDs: Iterable = None) -> Dict:
    geojson = {
        "type": "FeatureCollection",
        "features": []
    }
    # default whitelist is to allow all passed data through
    if whitelistIDs == None:
        def idFilter(x): return True
    else:
        whiteList = set(whitelistIDs)
        def idFilter(x): return x.id in whiteList

    def nodeFunc(feature):
        if not idFilter(feature):
            return

        entry = {
            "type": "Feature",
            "geometry": json.loads(osm.geom.GeoJSONFactory().create_point(feature)),
            "properties": {f"osm_{tag.k}": tag.v for tag in feature.tags}
        }
        entry["properties"]['osm_id'] = f"n{feature.id}"
        # entry["properties"]['timestamp'] = datetime_to_timestamp(
        #     feature.timestamp)
        # entry['id'] = f"n{feature.id}"
        geojson['features'].append(entry)
        return

    osm.make_simple_handler(node=nodeFunc).apply_file(
        sourcePath, locations=True)

    if destPath != None:
        with open(destPath, "w") as jsFile:
            json.dump(geojson, jsFile)
    return geojson


def way_to_linestring(sourcePath: str, destPath: str = None, whitelistIDs: Iterable = None,skipError=False) -> Dict:
    '''
    convert all way features in the .pbf file into geojson lines
    params:
        sourcePath : source .pbf file to get ways from
        destPath : (optional) file to write geojson data to
    '''
    # one pass of lines --> get coords and tags, write to common dict
    # optional second arg for writeback
    if whitelistIDs == None:
        def idFilter(x): return True
    else:
        whiteList = set(whitelistIDs)
        def idFilter(x): return x.id in whiteList

    geojson = {
        "type": "FeatureCollection",
        "features": []
    }

    def wayFunc(feature):
        if not idFilter(feature):
            return
        try:
            entry = {
                "type": "Feature",
                "geometry": json.loads(osm.geom.GeoJSONFactory().create_linestring(feature)),
                "properties": {f"osm_{tag.k}": tag.v for tag in feature.tags}
            }
        except Exception as e:
            print(str(feature.id) + " : " + str(e))
            if skipError:
                return 
            else:
                raise e
            

        entry["properties"]['osm_id'] = f"w{feature.id}"
        # entry["properties"]['timestamp'] = datetime_to_timestamp(
        #     feature.timestamp)
        # entry['id'] = f"w{feature.id}"
        geojson['features'].append(entry)
        return

    osm.make_simple_handler(way=wayFunc).apply_file(sourcePath, locations=True)

    if destPath != None:
        with open(destPath, "w") as jsFile:
            json.dump(geojson, jsFile)
    return geojson


def area_to_polygon(sourcePath: str, destPath: str = None, whitelistIDs: Iterable = None) -> Dict:
    '''
    take areas from a pbf file and export as a geojson of (multi)polygons
    optional destPath for writing out geojson
    optional whitelistIDs for selected data
    '''
    if whitelistIDs == None:
        def idFilter(x): return True
    else:
        whiteList = set(whitelistIDs)
        def idFilter(x): return x.id in whiteList

    geojson = {
        "type": "FeatureCollection",
        "features": []
    }

    relationToClear = set()

    def areaFunc(feature):
        if not idFilter(feature):
            return
        if not feature.from_way():
            # note areas that might have children/ inner rings
            relationToClear.add(feature.orig_id())
        entry = {
            "type": "Feature",
            "geometry": json.loads(osm.geom.GeoJSONFactory().create_multipolygon(feature)),
            "properties": {f"{tag.k}": tag.v for tag in feature.tags}
        }
        entry["properties"]['osm_id'] = f"a{feature.id}"
        entry["properties"]['orig_id'] = f"{'w' if feature.from_way() else 'r'}{feature.orig_id()}"        
        # entry["properties"]['timestamp'] = datetime_to_timestamp(
        #     feature.timestamp)
        geojson['features'].append(entry)
        return

    osm.make_simple_handler(area=areaFunc).apply_file(
        sourcePath, locations=True)


    waysToClear = set()
    def relationFunc(feature):
        if feature.id in relationToClear:
            waysToClear.update([i.ref for i in feature.members])

    osm.make_simple_handler(relation=relationFunc).apply_file(
        sourcePath, locations=True)


    waysToClear = [f"w{i}" for i in waysToClear]
    geojson["features"] = [i for i in geojson["features"] if i['properties']['orig_id'] not in waysToClear]


    if destPath != None:
        with open(destPath, "w") as jsFile:
            json.dump(geojson, jsFile)
    return geojson


def pbf_togeojson_lines(sourcePath: str) -> Dict:
    '''
    take in a .pbf file containing only lines and multilines
    return a geojson dictionary representation of the data
    
    # not extracting ways which are part of relations as their own thing
    '''
    # relations --> get tag
    #               get members
    relations = dict()
    # extract all relations

    def relationFunc(feature):
        relations[feature.id] = dict()
        relations[feature.id]["tags"] = {tag.k: tag.v for tag in feature.tags}
        relations[feature.id]["members"] = [
            (mem.type, mem.ref) for mem in feature.members]

    osm.make_simple_handler(relation=relationFunc).apply_file(sourcePath)
    # safe to assume that all are directly connected?
    # TODO: work in a recursive way of settling multi-line-strings

    # get list of non-line ways
    # key = wayID, value = parent relation
    relationWays = dict()
    for k, v in relations.items():
        for member in v["members"]:
            relationWays[member[1]] = k

    # one more pass
    # ways --> directly write way
    # relations --> add to his parent
    def wayFunc(feature):
        if feature.id in relationWays.keys():
            # append to parent multiline
            return
        # write to geojson

    osm.make_simple_handler(way=wayFunc).apply_file(sourcePath)

    # way --> get tag
    #       > get geometry

    # inital ways --> dictionary indexed by osm_id
    # remove and add to multiline relations as needed
    pass
