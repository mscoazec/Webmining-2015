# -*- coding: utf-8 -*-
"""
Created on Mon Oct 19 11:01:38 2015

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

X_1=np.zeros((n,5))
y=np.zeros(n)

#conversion en float
#extraction des données quantitatives, à la main pour l'instant
#pour l'instant check isNaN 
for i in range(n):
    if math.isnan(X_0[i,57]):
        X_1[i,0]=0.
    else:
        X_1[i,0]=X_0[i,57]*1.
    if math.isnan(X_0[i,60]):
        X_1[i,1]=0.
    else:
        X_1[i,1]=X_0[i,60]*1.
    if math.isnan(X_0[i,61]):
        X_1[i,2]=0.
    else:
        X_1[i,2]=X_0[i,61]*1.
    if math.isnan(X_0[i,63]):
        X_1[i,3]=0.
    else:
        X_1[i,3]=X_0[i,63]*1.
    if math.isnan(X_0[i,66]):
        X_1[i,4]=0.
    else:
        X_1[i,4]=X_0[i,66]*1.    
    if math.isnan(y_0[i]):
        y[i]=0.
    else:
        y[i]=y_0[i]*1.

X_centered= X_1-X_1.mean(axis=0, dtype=np.float64)
std = X_centered.std(axis=0)
for i in range(len(std)):
    if (std[i]==0):
        std[i]=1
X=X_centered/std
#X=X_centered
ncomponents=2
Reducteur1=decomposition.PCA(n_components=ncomponents, whiten=True)

X_reduced=Reducteur1.fit_transform(X)

#on rajoute les valeurs d'étiquettes dans la dernière colonne
X_redT=X_reduced.T
labels=np.array([y])

ReducedDataT=np.append(X_redT, labels, axis=0)
#print ReducedDataT.shape
ReducedData=ReducedDataT.T
#print ReducedData.shape
X_1, X_2=Reducteur1.components_
max_1=0
max_2=0
ind_1=0
ind_2=0
#max_3=0
#ind_3=0
for i in range(X_1.size):
    if math.fabs(X_1[i])>max_1:
        max_1=math.fabs(X_1[i])
        ind_1=i
for i in range(X_2.size):
    #if (i!=74)&(i!=67)&(i!=71):
         if math.fabs(X_2[i])>max_2:
            max_2=math.fabs(X_2[i])
            ind_2=i
#for i in range(X_3.size):
    #if (i!=74)&(i!=67)&(i!=71):
#        if math.fabs(X_3[i])>max_3:
#            max_3=math.fabs(X_3[i])
#            ind_3=i
print X_1, X_2
print "La principale contribution au premier axe vient du feature "+ str(ind_1) +" et vaut "+str(X_1[ind_1])
print "La principale contribution au second axe vient du feature "+ str(ind_2)  +" et vaut "+str(X_2[ind_2])
#ecriture du fichier json
with open('ReducedData.json', 'w') as outfile:
   json.dump(ReducedData.tolist(), outfile)
    



