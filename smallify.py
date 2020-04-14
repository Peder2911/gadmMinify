#!/usr/bin/env python

import shapely
import geopandas as gpd
from datetime import datetime
from os import path

def homogenize(geometry):
    if geometry.geom_type == "Polygon":
        return shapely.geometry.MultiPolygon([geometry])
    else:
        return geometry

def noIslands(multiPolygon):
    largePol = [p for p in multiPolygon if round(p.area,3) != 0]
    return shapely.geometry.MultiPolygon(largePol)

if __name__ == "__main__":
    print("Reading raw gadm (this takes a while)...")
    raw = gpd.read_file("raw/gadm36.gpkg")
    print("Successfully read!")

    for c in set(raw.NAME_0):
        dest = f"out/{c}.geojson"
        if not path.exists(dest):
            m1 = datetime.now()
            print(f"\nDoing {c}")
            d = raw[raw.NAME_0 == c]
            d = d.dissolve("NAME_1")
            d["geometry"] = d.geometry.apply(lambda x: noIslands(homogenize(x)))
            d = d.simplify(0.008)
            try:
                d.to_file(dest, driver = "GeoJSON")
            except ValueError:
                print("{c} failed! Probably empty...")
            print(f"That took {round((datetime.now()-m1).total_seconds(),2)} seconds")
        else:
            print(f"Skipping {c} (exists @ {dest})")

