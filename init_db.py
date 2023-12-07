# -*- coding: utf-8 -*-
"""
Created on Sun Apr 12 07:41:31 2020

@author: Alex
"""
#from sqlalchemy.orm import sessionmaker
#from sqlalchemy import create_engine
from app import db
from app.models import Chemical, Medium, Person, Cell_line, Endpoint, Solvent, \
    Person_Institution, Institution
import json, os,csv
import pandas as pd

#engine = create_engine("postgresql+psycopg2://utox_admin:iLoveCellLines@/cell_tox_db")




#DBSession = sessionmaker(bind=engine)
#session = DBSession()


db.create_all()
session = db.session

with open(os.path.join(".","data","media.csv"),'r') as f:
    media_info = pd.read_csv(f)
session.bulk_insert_mappings(Medium,
                             media_info.to_dict(orient='rows'))

with open(os.path.join(".","data","endpoints.csv"),'r') as f:
    endpoint_info = pd.read_csv(f)
session.bulk_insert_mappings(Endpoint,
                             endpoint_info.to_dict(orient='rows'))

with open(os.path.join(".","data","solvents.csv"),'r') as f:
    solvent_info = pd.read_csv(f,sep=';'  )
session.bulk_insert_mappings(Solvent,
                             solvent_info.to_dict(orient='rows'))



with open(os.path.join(".","data","chemicals_info.json"),'r') as f:
    #ch_info = json.load(f)
    
    
    cdf = pd.read_json(f)
# cdfc = cdf['cas_number'].value_counts()
# mask = (cdfc > 1) & (cdfc < 30)
# doublets = cdfc[mask]
# doublet_names = list(doublets.keys())
# dfmask = [i in doublet_names for i in cdf['cas_number']]
# doublet_df = cdf.loc[dfmask]
# doublet_df.to_excel('./data/chemical_doublets.xlsx')    

# cdf.loc[(cdf['experimental_solubility'] != 7.3) | (cdf.name =='lindane')]



# bad_ids_r = db.session.query(Chemical.id,Chemical.cas_number).filter(and_(Chemical.experimental_solubility == 7.3,Chemical.name != 'Lindane')).all()
# bad_cas = [x[1] for x in bad_ids_r]
# bad_ids = [x[0] for x in bad_ids_r]
# db.session.query(Chemical).filter(Chemical.id.in_(bad_ids)).delete(synchronize_session='fetch')

# from sqlalchemy import func


# db.session.query(Exposure).filter(Exposure.chemical_id.in_(bad_ids))
# db.session.query(Chemical).filter(Chemical.id.in_(bad_ids))
# f = db.session.query(Chemical.cas_number, func.count(Chemical.cas_number)). \
#     group_by(Chemical.cas_number). \
#     having(and_(func.count(Chemical.cas_number) > 1,func.count(Chemical.cas_number) < 5 ))

# doublet_cas = [x[0] for x in f.all()]
# doublet_ids_r = db.session.query(Chemical,Chemical.id).filter(Chemical.cas_number.in_(doublet_cas))
# doublet_ids = [x[1] for x in doublet_ids_r]
# db.session.query(Chemical).filter(Chemical.id.in_(doublet_ids)).delete(synchronize_session='fetch')
# db.session.commit()

# chu = pd.read_excel(os.path.join(".","data","chemicals_unique.xlsx"))
# session.bulk_insert_mappings(Chemical,chu.to_dict(orient="rows"))
# session.commit()

chemical_df = pd.read_sql_table(
    "chemical",
    con=db.engine
)
chemical_df.to_excel("./data/chemicals_info_corrected.xlsx")



perXls= pd.ExcelFile(os.path.join(".","data","experimenters_filled.xlsx"))

perSheet = pd.read_excel(perXls,"Person")
instSheet = pd.read_excel(perXls,"Institution")
perInstSheet = pd.read_excel(perXls,"Person_Institution")

perInstSheet['end_year'] = perInstSheet['end_year'].replace("present",10000).astype(int)

perSheet.to_sql("person",
                db.engine,
                if_exists='append',
                schema='public',
                index=False,
                chunksize=500)


instSheet.to_sql("institution",
                db.engine,
                if_exists='append',
                schema='public',
                index=False,
                chunksize=500)

piDicts = []

for rec in perInstSheet.to_dict(orient = "records"):
    person_id = session.query(Person.id).filter_by(short_name=rec['person']).one()[0]
    institution_id = session.query(Institution.id).filter_by(short_name=rec['institution']).one()[0]
    piDicts.append(
        {
            "person_id" : person_id,
            "institution_id": institution_id,
            "start_year" : rec["start_year"],
            "end_year" : rec["end_year"]
            })
session.bulk_insert_mappings(Person_Institution,piDicts)
session.commit()

with open(os.path.join(".","data","cell_lines.csv"),'r') as f:
    cell_line = pd.read_csv(f,sep=",")
    
    
session.bulk_insert_mappings(Cell_line,
                             cell_line.to_dict(orient='rows'))



session.commit()




session.commit()
session.close()





