import shapely.geometry as sg
from shapely.strtree import STRtree
from typing import Union, Dict
#TODO:  rewrite documentation for pairs to use geojson2.featureshapes

def closestPoints(test, ref, buffer: Union[int, float] = None):
    '''
    Find the closest REF feature for each TEST feature
    Arguments:
    test -- geojson2 FeatureCollection of features
    ref --  geojson2 FeatureCollection of features
    buffer  -- [Optional] unitless numerical upper bound for distance between paired features
                uses the units of test and ref
    
    Return dictionary where {testKey:nearest refKey} for every testKey 
    '''
    REF_tree = STRtree([v.shape for k, v in ref.items()])
    closest = dict()
    for testK, testV in test.items():
        k = REF_tree.nearest(testV.shape)  # returns a shape
        if buffer != None and k.distance(testV.shape) > buffer:
            # discard if distance greater than buffer
            continue
        closest[testK] = id(k)
    return closest


def dict_pair(dict1: Dict, dict2: Dict, buffer: Union[int, float] = None):
    '''
    Pair up features from two dictionaries of feaureshapes by location
    Arguments:
    dict1   -- geojson2 FeatureCollection of features
    dict2   -- geojson2 FeatureCollection of features
    buffer  -- [Optional] numerical upper bound for distance between ref paired features

    Return:
    set of paired features set( (dict1Key,dict2key) )
    set of unpaired keys from dict1
    set of unpaired keys from dict2
    '''
    
    # include in pairs if features are mutual closest features
    closest1 = closestPoints(dict1, dict2, buffer)
    closest2 = closestPoints(dict2, dict1, buffer)
    # create set of tuples for matched pairs
    pairs = set((K1, V1) for K1, V1 in closest1.items() if closest2[V1] == K1)
    
    # filter out feature keys that are in pairs
    notRemain1 = set(i[0] for i in pairs)
    remain1 = set(i for i in dict1.keys() if i not in notRemain1)
    notRemain2 = set(i[1] for i in pairs)
    remain2 = set(i for i in dict2.keys() if i not in notRemain2)

    return pairs, remain1, remain2


def features_pair(features1, features2, buffer=None, times=2):
    '''
    pair data from 2 geojson dictionaries
    Argument:
    features1 -- iterable of features in geojson format
    features2 -- iterable of features in geojson format
    buffer  -- [Optional] numerical upper bound for distance between ref paired features
    times -- [Optional] number of times to run pairing, default 2
    Return:
    pairs of geojson features [(features1, features2)]
    unpaired features from features1
    unpaired features from features2
    '''
    # construct universal unique identifiers using memory address as key
    features1 = {v.shapeID: v for v in features1}
    features2 = {v.shapeID: v for v in features2}
    # add shape data to entries
    pairs = []  # tuples of feature pairs to output

    while times > 0:
        pairing = dict_pair( features1, features2, buffer)
        if len(pairing[0]) == 0:
            # terminate early if no pairs constructed
            break
        # add pairs
        pairs += [(features1[d1], features2[d2]) for d1, d2 in pairing[0]]
        # 
        features1 = {k:v for k,v in features1.items() if k in pairing[1]}
        features2 = {k:v for k,v in features2.items() if k in pairing[2]}
        if len(pairing[1]) == 0 or len(pairing[2]) == 0:
            # terminate early if one featureset exhausted
            break
        times -= 1

    # convert back into list of geojson features for return value
    remain1 = [v for v in features1.values()]
    remain2 = [v for v in features2.values()]
    return pairs, remain1, remain2
