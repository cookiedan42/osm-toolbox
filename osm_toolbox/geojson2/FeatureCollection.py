from .base import deepCopy
from .FeatureShape import FeatureShape

from typing import List,Dict, Union, TypeVar
from collections.abc import Iterator,Iterable
import json

FeatureCollection = TypeVar("FeatureCollection")
class FeatureCollection(dict):
    '''
    augmented dictionary class for working with geoJSON FeatureCollection
    features key is a dictionary of geoJSON features and shapely objects keyed on id(shape)

    structured as a dictionary with extra attributes and methods
    '''
    __slots__ = []

    @classmethod
    def from_features(cls,features:Iterable)->FeatureCollection:
        '''
        create a featureCollection from iterable of featureShapes
        '''
        #create empty Feature Collection
        r = FeatureCollection({})
        r["features"] = {i.shapeID:i for i in features}
        return r

    def __init__(self, geoJSON_Dict):
        '''
        take in a geoJSON dictionary object as an argument
        '''
        # update self with empty geojson structure
        self.update({
            "type": "FeatureCollection",
            "features": []
        })
        self.update(deepCopy(geoJSON_Dict))
        self["features"] = [FeatureShape(i) for i in self["features"]]
        self["features"] = {i.shapeID: i for i in self["features"]}

    def transform(self, transformer,transform_coords=False)->FeatureCollection:
        '''
        transform projection of shapes using a transformer
        param:
            transformer : function(shapely_object) -> shapely_object
                function that transforms a shapely object into the new shapely object to use
            transform_coords: Boolean
                (optional) True if backing geojson geometry should also be transformed
        '''

        res = self.copy()
        for k,v in res["features"].items():
            res["features"][k] =  v.transform(transformer,transform_coords=transform_coords)
        res["features"] = {v.shapeID:v for v in res.features()}
        return res

    def features(self) -> Iterator:
        '''return an Iterator of the features in the feature colection'''
        return (i for i in self["features"].values())
    
    def shapes(self)-> Iterator:
        '''return a Iterator of the shapes in the feature collection'''
        return (i.shape for i in self["features"].values())

    def copy(self) -> FeatureCollection:
        '''return a copy of the object'''
        return FeatureCollection(self.to_geojson())

    def __len__(self) -> int:
        '''return number of features in the geojson'''
        return len(self["features"])

    def get(self, key, default=None):
        '''try to retrieve self[key], returns default value if not found'''
        try:
            return self[key]
        except KeyError:
            return default

    def __getitem__(self, key: Union[str, int]):
        '''
        return top level entry if keytype is a string
        return FeatureShape associated with memory address if key is integer
        '''
        if type(key) == str:
            return super().__getitem__(key)
        elif type(key) == int:
            return self["features"][key]

    def __setitem__(self, key, value):
        '''
        set top level entry if keytype is a string
        set FeatureShape if key is an integer
        '''
        if type(key) == str:
            super().__setitem__(key, value)
        elif type(key) == int:
            super()["features"][key] = value

    def to_geojson(self) -> Dict:
        '''
        return the geoJSON dictionary object representation of this object for writing
        ["features"] is restored to an array of features
        '''
        result = deepCopy(self)
        result["features"] = list(self["features"].values())
        return result

    def __repr__(self) -> str:
        # repr of all top level feature collection, then features
        r = "<FeatureCollection>{ "
        for k, v in self.items():
            if k == "features":
                continue
            r += f" {k}: {v},"
        return (r + f" feature count : {len(self['features'])}" + "}")