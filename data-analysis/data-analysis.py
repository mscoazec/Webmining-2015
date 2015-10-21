# -*- coding: utf-8 -*-
"""
Created on Wed Oct 21 15:51:09 2015

@author: Marion
"""

import csv
import numpy as np
from pylab import *
import matplotlib.pyplot as plt

filename = "apparts_cinq_sites_10-21_traite.csv"
datename = "-10-21"

r =csv.reader(open(filename,"rb"),delimiter=',')
x = list(r)

labels = x[0]
data = x[1:]

data = np.array(data)

# string vide to 0 pour cast to float
data[data=='']='0'

data = data.astype(np.float)

# fonction pour tracer un parametre en fonction de l'autre

def traceNuage(xname, yname):
    
    plt.figure(figsize=(20,10))
    
    y = data[:,labels.index(yname)]
    x = data[:,labels.index(xname)]
    
    plt.scatter(x, y)
    plt.xlim(0, max(x))
    plt.ylim(0, max(y))
    plt.xlabel(xname)
    plt.ylabel(yname)
    title(yname+' en fonction de '+xname+' sur le training set')
    
    plt.savefig(yname+'_'+xname+datename+'.png')

# fonction pour tracer un parametre en fonction d'un parametre discret

def traceMoustache(xname, yname):
    
    defini = 1
    
    plt.figure(figsize=(20,10))
    
    y = data[:,labels.index(yname)]
    x = data[:,labels.index(xname)]
    
    unique_x = np.unique(x)
    split_y = []
    
    for i in range(len(unique_x)):
        split_y.append(y[x == unique_x[i]])
    
    split_y = np.array(split_y)
    
    plt.boxplot(split_y, positions = unique_x, patch_artist = True)
    
    if defini:
        plt.ylim(0, 3500000)
    else:
        plt.ylim(0, max(y))
    
    plt.xlabel(xname)
    plt.ylabel(yname)
    title(yname+' en fonction de '+xname+' sur le training set')
    
    plt.savefig(yname+'_'+xname+datename+'_box'+'.png')

# nombre de donnees par arrondissement

# prix en fonction de la surface

traceNuage('surface','prix')

# prix en fonction de l'arrondissement

traceMoustache('arrondissement','prix')

# prix en fonction de la présence de balcon

traceMoustache('balcon','prix')

# prix en fonction de la présence d'ascenseur

traceMoustache('ascenseur','prix')