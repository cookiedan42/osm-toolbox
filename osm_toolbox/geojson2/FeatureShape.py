from .base import deepCopy
from typing import List,Dict, Union, TypeVar
from collections.abc import Iterator,Iterable
import shapely.geometry as sg
import json

FeatureShape = TypeVar("FeatureShape")

class FeatureShape(dict):
    '''
    Augmented Dictionary representation of geoJSON feature
    FeatureShape.shape - shapely object for geoJSON feature
    FeatureShape.shapeID - UUID based on shape
    '''
    __slots__ = ["shape", "shapeID"]

    @classmethod
    def from_shapely(cls,shape,properties={})-> FeatureShape:
        '''
        create a FeatureShape object from a shapely shape object and optional properties
        params:
            shape: shapely geometry object to use as the base
            properties: properties to attach to the geojson object
        return:
            FeatureShape object
        '''

        res = cls({ "type": "Feature",
        "geometry": sg.Point(0,0),
        "properties": properties
        })

        res.shape = shape
        res.shapeID = id(shape)
        res["geometry"] = sg.mapping(shape)
        
        return res

    def __init__(self, geoJSON_Dict = None):
        '''
        param:
            geoJSON_Dict - Dictionary representation of a geoJSON feature
        '''
        # setup empty geojson structure
        self.update({ "type": "Feature",
        "geometry": None,
        "properties": None
        })
        self.update(deepCopy(geoJSON_Dict))
        self.shape = sg.shape(self["geometry"])
        self.shapeID = id(self.shape)

    def copy(self) -> FeatureShape:
        '''
        create a copy of the FeatureShape
        '''
        # export the underlying dictionary, then rebuild the new FeatureShape
        # keep the old shape and ID
        newFS = FeatureShape(self)
        newFS.shape = self.shape
        newFS.shapeID = self.shapeID
        return newFS

    def transform(self,transformer,transform_coords=False):
        '''
        transform projection of shape using a transformer
        param:
            transformer : function(shapely_object) -> shapely_object
                function that transforms a shapely object into the new shapely object to use
            transform_coords: Boolean
                (optional) True if backing geojson geometry should also be transformed
        '''
        res = self.copy()
        res.shape = transformer(res.shape)
        res.shapeID = id(res.shape)
        if transform_coords:
            res["geometry"] = sg.mapping(res.shape)
        return res

    def __str__(self) -> str:
        # detailed repr of underlying geojson data
        return f"<{self.shape.type} Feature>" + json.dumps(self, indent=2)

    def __repr__(self) -> str:
        # simple repr using memory address
        return f"<{self.shape.type}Shape@{id(self)}>"

    def properties(self) -> dict:
        '''
        return properties dict if present
        return empty dictionary otherwise
        '''
        return self.get("properties", {})

    def geometry(self) -> dict:
        '''
        return geometry dict if present
        return empty dictionary otherwise
        '''
        return self.get("geometry",{})

    def json(self):
        '''
        return json representation of this feature
        '''
        return deepCopy(self)