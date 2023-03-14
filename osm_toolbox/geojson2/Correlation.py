# draw correlations between features in a FeatureCollection 
from pandas import DataFrame
from .FeatureCollection import FeatureCollection
# return a dataframe of heatmaps



def correlation(featC,whiteList=[],blackList=[]):
    data = [i["properties"] for i in featC]
    if len(whiteList) > 0:
        # only include whitelisted fields
        data = [{k:v for k,v in i["properties"].items() if k in whiteList} for i in data]

    if len(blackList) > 0:
        # remove blackListed fields
        data = [{k:v for k,v in i["properties"].items() if k not in whiteList} for i in data]

    return DataFrame(data).corr()



