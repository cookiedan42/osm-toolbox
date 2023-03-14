import osmium as osm ##TODO CHANGE
import json
from typing import Dict

def count_pbf_features(
    source:str  # path to .pbf file to count features of
)-> Dict:
    l = count_features()
    l.apply_file(source)
    return {
        "nodes":l.cNode,
        "ways":l.cWay,
        "relations":l.cRelation,
        "areas":l.cArea,
    }
class count_features(osm.SimpleHandler):
    def __init__(self):
        super().__init__()
        self.cNode = 0
        self.cWay = 0
        self.cRelation = 0
        self.cArea = 0
    def area(self,area):
        self.cArea +=1
    def node(self,k):
        self.cNode +=1
    def relation(self,k):
        self.cRelation+=1
    def way(self,k):
        self.cWay +=1