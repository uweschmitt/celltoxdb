# -*- coding: utf-8 -*-
"""
Created on Wed Apr 22 18:40:12 2020

@author: Alex
"""
import app
from insert_db import add_record
from fileIO import read_dr

import os

db = app.db
Chemical = app.db.models.Chemical
Nanomaterial = app.db.models.Nanomaterial
Exposure = app.db.models.Exposure

files = list(filter(lambda x: (x.endswith("xls") or x.endswith("xlsx") or x.endswith("csv") ) and not x.startswith('.') and not x.startswith('~'),os.listdir('../rawdata/newnames')))
fname  = files[0]



data = [read_dr(os.path.join("..","rawdata","newnames",fname),verbose=True) for fname in files]

#check how many chemicals cant be assigned

missing_chems = []
for d in data:
    chem_id = d['cas_number']
    cas_id = db.session.query(Chemical).filter(Chemical.cas_number == chem_id).one_or_none()
    if cas_id is None:
        chem_name = db.session.query(Chemical).filter(Chemical.name == chem_id).one_or_none()
        if(cas_id is None and chem_name is None):
            if chem_id.find("nano") == 0:
                nano_id = int(chem_id.strip("nano"))
                nano_entry = db.session.query(Nanomaterial).filter(Nanomaterial.id == nano_id).one_or_none()
                if nano_entry is None:
                    missing_chems.append(chem_id)
            else:
                missing_chems.append(chem_id)
                
            
np_names = db.session.query(Chemical).filter(and_(Chemical.name.ilike('%np%'),Chemical.cas_number == "No CAS")).all()            
set(missing_chems)   
np_names
from app.models import Nanomaterial
nano_df = pd.read_sql_table("nanomaterial",db.engine )
nano_df.to_excel("./data/nanomaterials.xlsx")
         
add_record(data[0],db.session,db.engine)

db.session.query(Estimated).delete()
db.session.query(Dose_response).delete()
db.session.query(Exposure).delete()
from itertools import compress
aidx = [a == "GIL_jaikga_24_0024h_CF_m1_FBS00_nn_in_me_D_335104-84-2.xlsx" for a in files]
tr = list(compress(data,aidx))[0]
add_record(tr,db.session,db.engine)


failed = []
failed_files = []
for i,d in enumerate(data):
    try:
        add_record(d,db.session,db.engine)
    except:
        failed.append(d["id_string"])
        failed_files.append(files[i])
        pass
 
fdata = [read_dr(os.path.join("..","rawdata","newnames",fname),verbose=True) for fname in failed_files]
    
failed2 = []
failed_files2 = []

for i,d in enumerate(fdata):
    try:
        add_record(d,db.session,db.engine)
    except:
        failed2.append(d["id_string"])
        failed_files2.append(failed_files[i])
        pass
 

#filesIB = list(filter(lambda x: not x.startswith('.'),os.listdir('../rawdata/for_upload')))
#dataIB = [read_dr(os.path.join("..","rawdata","for_upload",fname),verbose=True) for fname in filesIB]


Person = app.models.Person
Institution = app.models.Institution
Person_Institution = app.models.Person_Institution

seq = app.db.session.query
q = seq(Person).join(Person_Institution)
qwe = q.with_entities(Person.id,Person_Institution.institution_id).all()
updict = [{"experimenter_id": x[0], "institution_id" : x[1]} for x in qwe]
for d in updict:
    seq(Exposure).filter(Exposure.experimeter_id == d['experimenter_id']).\
        update(d)

app.db.session.bulk_update_mappings(Exposure,updict)