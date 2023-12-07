# -*- coding: utf-8 -*-
"""
Created on Tue Jun  2 16:12:47 2020

@author: Alex
"""
#%env DATABASE_URL=postgresql+psycopg2://utox_fab:iLoveFAB@/cell_tox

import pandas as pd
import re

from app import db
from app.models import Chemical,Exposure
from utils import chemical_title

#dat= pd.read_excel("D://polybox/dr_database/Cells_Dose_ResponsesV16.xlsm",
#                   sheet_name = "IDs")

dat= pd.read_excel("/Users/alx/polybox2/dr_database/Cells_Dose_ResponsesV17.xlsm",
                   sheet_name = "IDs")


dats = dat[['Year','Place','Reference','File ID  AB','File ID NR','File ID CFDA',
    'File ID PB']]

ex = pd.read_csv("./data/experimenters.csv")
ex_map = dict(zip(ex.short_name_deprecated.to_list(),
                  ex.short_name.to_list()))

def replace_experimenter(umap,string):
    for key,value in umap.items():
        string = re.sub(key,value,string)
    return(string)

def my_replace_experimenter(string):
    if pd.isnull(string):
        return(string)
    return replace_experimenter(ex_map,string)

dats['File ID  AB'] = dats['File ID  AB'].map(my_replace_experimenter)
dats['File ID NR'] = dats['File ID NR'].map(my_replace_experimenter)
dats['File ID CFDA'] = dats['File ID CFDA'].map(my_replace_experimenter)
dats['File ID PB'] = dats['File ID PB'].map(my_replace_experimenter)
dat_long = dats.melt(id_vars=['Year','Place','Reference'],value_name="id_string")

dat_long = dat_long.rename(columns={"Year" : "year","Reference":"doi","Place":"place"})
dat_long = dat_long.dropna(subset=["id_string"])
dat_dict = dat_long.to_dict(orient='records')
dat_id_dict = dict(zip(dat_long.id_string,dat_dict))


# %env DATABASE_URL=postgresql+psycopg2://utox_admin:iLoveCellLines@/cell_tox_db
session = db.session

id_maps = []

for eid,sid in session.query(Exposure.id,Exposure.id_string):
    id_maps.append({
        "id": eid,
        "id_string": my_replace_experimenter(sid)
        })
session.bulk_update_mappings(Exposure,id_maps)



emaps = []


for eid,sid in session.query(Exposure.id,Exposure.id_string):
    if sid in dat_id_dict.keys():
        if pd.isna(dat_id_dict[sid]["doi"]):
            dat_id_dict[sid]["doi"] = None
        emaps.append(
            {"id" : eid,
             "doi" : dat_id_dict[sid]["doi"],
             "year" : dat_id_dict[sid]["year"]}
            )

session.bulk_update_mappings(Exposure,emaps)
session.commit()

##### add molecular weight information to chemicals

datc = dat[['CAS Nr.','g/mol']].drop_duplicates().dropna()
datc['g/mol'] = datc['g/mol'].map(str).map(lambda x: re.sub(',','.',x)).map(float)
datc = datc.rename(columns = {"CAS Nr." : "cas_number", "g/mol" : "moleculwar_weight"})
mw_map = datc.to_dict(orient = "records")
session.bulk_update_mappings(Chemical,mw_map)
session.commit()

##### capitalize chemical names
cnmap = []
for cid, cname in session.query(Chemical.id,Chemical.name):
    cnmap.append({"id": cid, "name": chemical_title(cname)})
    
session.bulk_update_mappings(Chemical,cnmap)
session.commit()



    
    
