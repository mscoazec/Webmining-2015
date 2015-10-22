# -*- coding: utf-8 -*-
"""
Created on Wed Oct 21 15:54:10 2015

@author: chzhang
"""

import base64
import json
from sklearn.feature_extraction.text import CountVectorizer
import pandas as pd
#from time import time
import os
#import pylab as plt
import numpy as np
import math
from sklearn import decomposition
#from sklearn.lda import LDA

os.getcwd()
df=pd.read_csv("apparts_cinq_sites_10-21_traite.csv") ### 1er appel

#### matrice python avec les données
data=df.values 


####
X_0=data[:,:-1]
y_0=data[:,-1]


n=len(X_0)### nombre d'annonces
k=len(X_0[0,:]) ###nombres de features

X_1=np.zeros((n,k))
y=np.zeros(n)

#conversion en float
for i in range(n):
    for j in range(k):
        if math.isnan(X_0[i,j]):
            X_1[i,j]=0.
        else:
            X_1[i,j]=X_0[i,j]*1.
    if math.isnan(y_0[i]):
        y[i]=0.
    else:
        y[i]=y_0[i]*1.

Trunc=np.zeros((n,3))
for i in range(n):
        Trunc[i]=[X_1[i][57], X_1[i][60], y[i]]
with open('surfacearrond.json', 'w') as outfile:
   json.dump(Trunc.tolist(), outfile)