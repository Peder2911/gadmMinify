#!/usr/bin/env python

import geopandas as gpd
import pandas as pd
import sqlite3 as sqlt

smallified = gpd.read_file("gpkg/dat.gpkg")

con = sqlt.connect("raw/gadm36.gpkg")
c = con.cursor()
meta = pd.read_sql("SELECT GID_0 as ISO_3, NAME_0, NAME_1, HASC_1 FROM gadm", con)
meta = meta.drop_duplicates()

withmeta = smallified.merge(meta,on = ("NAME_0","NAME_1"))
withmeta.to_file("gpkg/dat_w_meta.gpkg",driver = "GPKG")
print("done!")
