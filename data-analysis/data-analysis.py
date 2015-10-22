# -*- coding: utf-8 -*-
"""
Created on Wed Oct 21 15:51:09 2015

@author: Marion
"""

import csv
import numpy as np
from pylab import *
import matplotlib.pyplot as plt

##### donnees a modifier en fonction du fichier que l'on souhaite analyser
filename = "apparts_cinq_sites_10-21_traite.csv"
datename = "-10-21"
##### ##### #####

# ouverture du csv
r =csv.reader(open(filename,"rb"),delimiter=',')
x = list(r)

# labels des colonnes du csv
labels = x[0]

# donnees du csv
data = x[1:]
data = np.array(data)

# string vide to -1 (donnee manquante) pour faire le cast to float
data[data=='']='0'

# cast to float
data = data.astype(np.float)

# fonction pour tracer un parametre en fonction de l'autre

def traceNuage(xname, yname):
    
    # limite max en x, y du graphe (si defini = 1, sinon y_max = max(y))
    defini = 0
    x_max = 400
    y_max = 8000000
    
    # affichage
    plt.figure(figsize = (12,10))

    # donnees    
    y = data[:,labels.index(yname)]
    x = data[:,labels.index(xname)]
    
    # trace du graphe
    plt.scatter(x, y)
    
    # gestion de l'affichage
    if defini:
        plt.xlim(0, x_max)
        plt.ylim(0, y_max)
    else:
        plt.xlim(0, max(x))
        plt.ylim(0, max(y))
    plt.xlabel(xname)
    plt.ylabel(yname)
    plt.grid(True)
    title("'"+yname+"' en fonction de '"+xname+"' sur le training set")
    
    # sauvegarde en png
    plt.savefig(yname+'_'+xname+datename+'.png')
    
# fonction pour tracer un histogramme

def traceHisto(yname):
    
    # affichage
    plt.figure(figsize = (12,10))

    # donnees    
    y = data[:,labels.index(yname)]
    
    # trace du graphe
    hist(y)
    
    # gestion de l'affichage
    plt.ylabel(yname)
    plt.grid(True)
    title("repartition de '"+yname+"' sur le training set")
    
    # sauvegarde en png
    plt.savefig(yname+'_hist.png')

# fonction pour tracer un parametre en fonction d'un parametre discret

def traceMoustache(xname, yname):
    
    # limite max en y du graphe (si defini = 1, sinon y_max = max(y))
    defini = 1
    y_max = 3000000
    
    # affichage
    plt.figure(figsize = (32,12))
    
    # donnees    
    y = data[:,labels.index(yname)]
    x = data[:,labels.index(xname)]
    
    # couper y en differentes box selon les labels donnes par x
    unique_x = np.unique(x)
    split_y = []
    count_y = []
    
    for i in range(len(unique_x)):
        split_y.append(y[x == unique_x[i]])
        count_y.append(len(y[x == unique_x[i]]))
    
    split_y = np.array(split_y)
    count_y = np.array(count_y)
    
    # trace du graphe 1
    plt.subplot(1, 2, 1)
    plt.boxplot(split_y, positions = unique_x, patch_artist = True)
    
    # gestion de l'affichage 1
    if defini:
        plt.ylim(0, y_max)
    else:
        plt.ylim(0, max(y))
    
    plt.xlabel(xname)
    plt.ylabel(yname)
    plt.grid(True)
    title("'"+yname+"' en fonction de '"+xname+"' sur le training set")
    
    # trace du graphe 2 histogramme
    plt.subplot(1, 2, 2)
    bar(unique_x, count_y, align = 'center')
    
    # gestion de l'affichage 2
    plt.xlim(-1, max(unique_x)+1)
    plt.ylim(0, max(count_y)+100)
    plt.xlabel(xname)
    plt.ylabel('nombre de donnees')
    title("nombre de donnees par '"+xname+"' sur le training set")
    
    # sauvegarde en png
    plt.savefig(yname+'_'+xname+datename+'_box'+'.png')

# histogramme prix, surface

traceHisto('prix')
traceHisto('surface')

# prix en fonction de la surface

traceNuage('surface','prix')

# prix en fonction de l'arrondissement

traceMoustache('arrondissement','prix')

# prix en fonction de la présence de balcon

traceMoustache('balcon','prix')

# prix en fonction de la présence d'ascenseur

traceMoustache('ascenseur','prix')

# prix en fonction de l'etage

traceMoustache('etage','prix')

# 