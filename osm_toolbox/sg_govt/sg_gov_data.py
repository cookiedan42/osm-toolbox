import json
from typing import Dict 

# cleanup govt data
def parseDesc(desc: str)-> Dict:
    '''
    cleanup 2 column markup table string into properties dictionary
    '''
    # govt data is stored as a markup table
    # convert table into dict of {<th>:<td>}
    desc = desc.split('<th>')
    desc = [i for i in desc if "<td>" in i]
    desc = [i.split("</td>")[0] for i in desc]
    # elements in desc are now in form of "header</th><td>data"
    return {i.split("</th>")[0]:i.split("<td>")[1] for i in desc}

def clean_KML_GeoJSON(
    inPath:str,outPath: str=None,
    delTable=True,tableKey="Description")->Dict:
    '''
    clean geojson with properties as 2 col KML table
    
    Optional outPath to write geojson to file
    Optional delTable to delete original table
    TableKey : name of table in properties, default "Description"
    return a geojson dictionary
    '''
    with open(inPath,"r") as jsFile:
        source = json.load(jsFile)
        
    for feature in source["features"]:
        # convert Description to discrete properties
        for k,v in parseDesc(feature["properties"].get(tableKey,{})).items():
            feature['properties'][k] = v
        
        if delTable: del feature['properties'][tableKey]

    # write out modified data if needed
    if outPath !=None:
        with open(outPath,"w") as jsFile:
            json.dump(source,jsFile)
    return source


#TODO: divide into file cleaner and dict cleaner