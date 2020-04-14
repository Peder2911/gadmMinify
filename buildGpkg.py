#!/usr/bin/env python

import fiona
from fiona.crs import from_string as crs_from_string
import json
import geopandas as gpd
import shapely

from os import path
import os


TGT = "gpkg/dat.gpkg"

allCountries = [path.splitext(f)[0] for f in os.listdir("out") if f != ".gitkeep"]

if not path.exists(TGT):
    schema = {
        "geometry":"MultiPolygon",
        "properties":[("NAME_0","str"),("NAME_1","str")]
    }

    crs = crs_from_string('+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs')
    with fiona.open(TGT,"w",
        driver = "GPKG",
        layer = "adm1",
        schema = schema,
        crs = crs) as gpkg:
        pass
    todo = allCountries
else:
    existing = gpd.read_file(TGT)
    todo = set(allCountries).difference(set(existing.NAME_0))
    print(f"Doing {len(todo)} countries")

def homogenize(x):
    if x is None:
        return None 
    elif x.geom_type == "Polygon":
        return shapely.geometry.MultiPolygon([x])
    elif x.geom_type == "MultiPolygon":
        return x
    else:
        raise ValueError("Geometries must be Polygon or MultiPolygon!")

for c in todo:
    print(f"Doing {c} |",end = "")
    data = gpd.read_file(f"out/{c}.geojson")
    print(f"Shape: {data.shape} |", end ="")

    preNrow = data.shape[0]
    
    data["geometry"] = data.geometry.apply(homogenize)
    data = data.loc[data.geometry.apply(lambda x: x is not None)]

    postNrow = data.shape[0]
    diff = postNrow - preNrow
    if diff != 0:
        print(f"Diff: {diff} |",end = "")
        print(f"\x1b[1mPost-trans: {data.shape} |\x1b[0m", end ="")


    with fiona.open(TGT,"a","GPKG","adm1") as gpkg:
        for i,r in data.iterrows():
            gpkg.write({
                "geometry": r.geometry.__geo_interface__ ,
                "properties": {
                    "NAME_0": c,
                    "NAME_1": r.NAME_1
                }
            })
    print("wrote!")
