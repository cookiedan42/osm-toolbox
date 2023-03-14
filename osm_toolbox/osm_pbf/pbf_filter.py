import osmium
import os
from typing import Dict
from collections.abc import Iterable
# from shapely.strtree import STRtree
from shapely.ops import unary_union
from shapely.prepared import prep
import shapely.wkt as wkt
from osmium.geom import WKTFactory
from .Writer import PBFwriter
from enum import Enum

class FilterResult():
    '''
    filter result is a restricted dictionary-like datastructure
    keys limited to {node,way,area,relation}

    '''
    def __init__(self,node=set(),way=set(),area=set(),relation=set()):
        self.node = set(node)
        self.way = set(way)
        self.area = set(area)
        self.relation= set(relation)
        self.store = {
            "node":self.node,
            "way":self.area,
            "area":self.area,
            "relation":self.relation,
        }
        
    def __getitem__(self,key):
        if key not in {"node","way","area","relation"}:
            raise Exception("invalid Key")
        #else
        return self.store[key]
    
    def items(self):
        return self.store.items()
    def keys(self):
        return self.store.keys()
    def values(self):
        return self.store.values()




class DefaultValues():
    IDENTITY = lambda x:x
    NO_ARG= None

class OSMtype():
    '''remove magic values from functions'''
    NODE = "node"
    WAY = "way"
    AREA = "area"
    RELATION = "relation"

class Proximity_Filter():
    def __init__(self, features: Iterable, bufferDistance,
                 featureType: Iterable = {"node","way","area"},
                       transform_Func=DefaultValues.IDENTITY):
        '''
        filter .osm.pbf file by features proximity to an iterable of shapely data
        params:
            sourcePath : path to source.osm.pbd file to filter
            features : iterable of shapely features to test proximity against
            bufferDistance : exclude features further than buffer distance
            (optional) featureType : types of features to return {"node","way","area"}
            (optional) transform_Func : function that takes in a shapely object and returns a reprojected shapely object
                - transform_Func is applied to features in the .osm.pbf file
        return:
            dictionary of feature ID of kept features
            {"node":set(id of nodes),
            "way":set(id of ways),
            "area:set(id of areas)}
        '''
        self.ref_multiPoly = prep(unary_union(
            [i.buffer(bufferDistance) for i in features]))
        self.transform_Func = transform_Func
        self.featureType = featureType
        # transformFunc

    def nodeCallback(self,result):
        # return node callback func
        if OSMtype.NODE not in self.featureType:
            return None
        def callback(feature):
            testWKT = WKTFactory().create_point(feature)
            testShape = self.transform_Func(wkt.loads(testWKT))
            if self.ref_multiPoly.intersects(testShape):
                result[OSMtype.NODE].add(feature.id)
        return callback

    def wayCallback(self,result):
        if OSMtype.WAY not in self.featureType:
            return None
        def callback(feature):
            testWKT = WKTFactory().create_linestring(feature)
            testShape = self.transform_Func(wkt.loads(testWKT))
            if self.ref_multiPoly.intersects(testShape):
                result[OSMtype.WAY].add(feature.id)
        return callback

    def areaCallback(self,result):
        if OSMtype.AREA not in self.featureType:
            return None
        def callback(feature):
            testWKT = WKTFactory().create_multipolygon(feature)
            testShape = self.transform_Func(wkt.loads(testWKT))
            if self.ref_multiPoly.intersects(testShape):
                result[OSMtype.AREA].add(feature.id)
        return callback
    
    def relationCallback(self,result):
        # relationCallback is not really relevant for this filter
        return None

    def apply_file(self,sourcePath:str):
        # result = {
        #     k: set() for k in self.featureType if k in 
        #     {OSMtype.NODE, OSMtype.WAY, OSMtype.AREA}
        # }
        result = FilterResult()
        osmium.make_simple_handler(
        node = self.nodeCallback(result),
        way  = self.wayCallback(result),
        area = self.areaCallback(result)
        ).apply_file(sourcePath)
        return result




def filter_byProximity(sourcePath: str, features: Iterable, bufferDistance: float,
                       featureType: Iterable = {"node","way","area"},
                       transform_Func=DefaultValues.IDENTITY) -> dict:
    '''
    expose Proximity_Filter as a function
    filter .osm.pbf file by features proximity to an iterable of shapely data
    params:
        sourcePath : path to source.osm.pbd file to filter
        features : iterable of shapely features to test proximity against
        bufferDistance : exclude features further than buffer distance
        (optional) featureType : types of features to return {"node","way","area"}
        (optional) transformFunc : function that takes in a shapely object and returns a reprojected shapely object
    return:
        dictionary of feature ID of kept features
        {"node":set(id of nodes),
         "way":set(id of ways),
         "area:set(id of areas)}
    '''
    callbacks = Proximity_Callbacks(features,bufferDistiance,featureType,transform_Func)
    return callbacks.apply_file(sourcePath)

def get_copy_ID( sourcePath:str, data: Dict = None,
                 node: Iterable=set(), way: Iterable=set(),
                 relation:Iterable=set(), area:Iterable=set()):
    '''
    taking iterables of osmID by type, return all the osmIDs that are required to represent this data
    params:
        filePath : path to source.osm.pbf file
        data : dict of iterables {"node":[],"way":[],...}
                data takes higher precedence over other 
        node : iterable of node IDs
        way : iterable of way IDs
        relation : iterable of relation IDs
        area : iterable of area IDs
    returns :
        dictionary of all IDs that need to be copied
        {"node":set(),"way":set(),"relation":set()}
    '''
    # copy each of the input sets
    if data == None:
        node = set(node)
        way = set(way)
        relation = set(relation)
        area = set(area)
    else: #data is a dictionary
        node = data.get(OSMtype.NODE,set())
        way = data.get(OSMtype.WAY,set())
        relation = data.get(OSMtype.RELATION,set())
        area = data.get(OSMtype.AREA,set())

    toWrite = {
        OSMtype.NODE:node,
        OSMtype.WAY:way,
        OSMtype.RELATION:relation
        }

    # resolve areas
    if len(area) > 0:
        def areaFunc(feature):
            if feature.id in area:
                if feature.from_way():  # from way
                    way.add(feature.orig_id())
                else:   # from relation
                    relation.add(feature.orig_id())
        # extract areas and add into way and relation
        osmium.make_simple_handler(area=areaFunc).apply_file(sourcePath)
    
    # recursively resolve all relations 
    if len(relation) > 0:
        def relationFunc(feature):
            if feature.id in unresolved:
                unresolved.remove(feature.id)
                for member in feature.members:
                    if member.type == 'r':
                        unresolved.add(member.ref)
                        relation.add(member.ref)
                    elif member.type == 'w':
                        way.add(member.ref)
                    elif member.type == 'n':
                        node.add(member.ref)

        unresolved = relation.copy()
        while len(unresolved) > 0:
            osmium.make_simple_handler(relation=relationFunc).apply_file(sourcePath)

    if len(way) > 0:
        # deconstruct way into nodereflist --> add to node if way is to be copied
        def wayFunc(feature):
            if feature.id in way:
                for n in feature.nodes:
                    node.add(n.ref)
        osmium.make_simple_handler(way=wayFunc).apply_file(sourcePath)
    
    # nodes can be directly copied and don't need processing
    return toWrite

def get_relation_members(sourcePath:str,relation:Iterable):
    '''
    take in an iterable of relations
    return the members of each relation as a dictionary
    key = relationID
    value = list of (id,featureType)
    '''

    relation = set(relation)
    result = {}

    def relationFunc(feature):
        if feature.id not in relation:
            return
        # else extract tags and members
        result[feature.id] = dict()
        result[feature.id]["tags"] = {tag.k:tag.v for tag in feature.tags}
        result[feature.id]["members"] = [(mem.type,mem.ref) for mem in feature.members]

    osmium.make_simple_handler(relation=relationFunc).apply_file(sourcePath)

    return result

def writeFeatures(
    sourcePath:str,
    destPath:str,
    data: Dict = None,
    node: Iterable=set(),
    way: Iterable=set(),
    relation: Iterable=set()):
    '''
    take sets of osmID and write the data from sourcePath to destPath
    both as osm.pbf
    '''

    if data != None:
        node = data.get(OSMtype.NODE,set())
        way = data.get(OSMtype.WAY,set())
        relation = data.get(OSMtype.RELATION,set())
    else:
        node = set(node)
        way = set(way)
        relation = set(relation)


    def nodeFunc(feature):
        if feature.id in node:
            writer.add_node(feature)
    # function to test node --> else do nothing

    def wayFunc(feature):
        if feature.id in way:
            writer.add_way(feature)

    def relationFunc(feature):
        if feature.id in relation:
            writer.add_relation(feature)


    writeHandler = osmium.make_simple_handler(
        node = nodeFunc if len(node)> 0 else None,
        way = wayFunc if len(way)> 0 else None,
        relation = relationFunc if len(relation)> 0 else None)

    with PBFwriter(destPath,overwrite=True) as writer:
        writeHandler.apply_file(sourcePath)

    # return void

def pbfFilter(sourcePath: str,
    nodePred=None,
    wayPred=None,
    relationPred=None,
    areaPred=None)-> Dict:
    '''
    taking in predicate functions, return dictionary of sets of osm ID for features that satisfy predicate
    predicate should take in a feature and return a boolean value
    '''
    result = {
        "node":set(),
        "way":set(),
        "relation":set(),
        "area":set(),}

    def featureFunc(feature,predicate,target):
        if predicate(feature):
            target.add(feature.id)
    
    def nodeCallback(feature): 
        return featureFunc(feature, nodePred, result[OSMtype.NODE])
    def wayCallback(feature): 
        return featureFunc(feature, wayPred, result[OSMtype.WAY])
    def relationCallback(feature): 
        return featureFunc(feature, relationPred, result[OSMtype.RELATION])
    def areaCallback(feature): 
        return featureFunc(feature, areaPred, result[OSMtype.AREA])

    # run callbacks if predicate is not None
    osmium.make_simple_handler(
        node = None if nodePred == None else nodeCallback,
        way = None if wayPred == None else wayCallback,
        relation = None if relationPred == None else relationCallback,
        area = None if areaPred == None else areaCallback
    ).apply_file(sourcePath)
    
    return result

def filter_by_tag(
    sourcePath:str,
    tags:Iterable,
    featureTypes = {"node","way","area","relation"},
    filterType="any",
    caseSensitive=False):
    '''
    filter .pbf file at sourcePath
    take in an iterable of strings to find in tags
    return a dict of {node:set()...} for individual features that fulfill the filter
    '''
    result = {
        "node":set(),"way":set(),
        "relation":set(),"area":set(),
    }

    # ensure that tags are in string form
    if not caseSensitive:
        tags = [t.lower() for t in tags]

    def featureFunc(feature,target:set):
        # generator to ensure all tags exposed, default str(feature.tags) is truncated
        sTags = str({k:v for k,v in feature.tags})
        if not caseSensitive:
            sTags = sTags.lower()
        tag_results = [t in sTags for t in tags]
        if filterType == "any" and any(tag_results):
            target.add(feature.id)
        elif filterType == "all" and all (tag_results):
            target.add(feature.id)

    nodeFunc = lambda feature: featureFunc(feature,result["node"]) if "node" in featureTypes else None
    wayFunc = lambda feature: featureFunc(feature,result["way"]) if "way" in featureTypes else None
    relationFunc = lambda feature: featureFunc(feature,result["relation"]) if "relation" in featureTypes else None
    areaFunc = lambda feature: featureFunc(feature,result["area"]) if "area" in featureTypes else None

    osmium.make_simple_handler(
        node = nodeFunc,
        way = wayFunc,
        relation = relationFunc,
        area = areaFunc
        ).apply_file(sourcePath)
    return result



