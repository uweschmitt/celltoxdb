#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun  4 16:58:25 2020

@author: alx
"""


import os
import pandas as pd
import re
from shutil import copyfile


ex = pd.read_csv("./data/experimenters.csv")
ex_map = dict(zip(ex.short_name_deprecated.to_list(),
                  ex.short_name.to_list()))

fnames = os.listdir("../rawdata/")
rnames = []
gfnames = []
try:
    for i,fname in enumerate(fnames):
        if re.search("recovery", fname) or re.search("rou",fname) or fname == ".DS_Store" or fname == "newnames":
            continue
        fns = fname.replace(" ","").replace("CFDA","CF").split('_')
        fns[1] = re.sub("é|é","é",fns[1])
        fns[1] = ex_map[fns[1]]
        rnames.append("_".join(fns))
        gfnames.append(fname)
except:
    print(fname)
    
fdir = "../rawdata/"
outdir = "../rawdata/newnames"
for i, fname in enumerate(gfnames):

    old_full = os.path.join(fdir,fname)
    new_full = os.path.join(outdir,rnames[i])
    print(old_full)
    print(new_full)
    print("")
    copyfile(old_full, new_full)
    #os.rename(old_full,new_full)


    
