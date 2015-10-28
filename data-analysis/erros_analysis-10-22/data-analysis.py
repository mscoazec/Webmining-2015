# -*- coding: utf-8 -*-
"""
Created on Wed Oct 21 15:51:09 2015

@author: Marion
"""

import csv
import numpy as np
from pylab import *
import matplotlib.pyplot as plt
import json
import io
from sklearn import linear_model

"""
pour l'analyse
"""

##### donnees a modifier en fonction du fichier que l'on souhaite analyser
filename = "errors_.csv"
datename = ""
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
    plt.xlabel(xname,fontsize=14)
    plt.ylabel(yname,fontsize=14)
    plt.grid(True)
    title("'"+yname+"' en fonction de '"+xname+"' sur le training set",
          fontsize=18)
    
    # sauvegarde en png
    plt.savefig(yname+'_'+xname+datename+'.png')
    
def traceNuageReg(xname, yname):
    
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
    
    regr = linear_model.LinearRegression()
    regr.fit(x[:,np.newaxis], y)
    
    x_test = np.linspace(np.min(x), np.max(x), 100)
    
    plt.plot(x_test, regr.predict(x_test[:,np.newaxis]), color='red', linewidth=3)
    
    # gestion de l'affichage
    if defini:
        plt.xlim(0, x_max)
        plt.ylim(0, y_max)
    else:
        plt.xlim(0, max(x))
        plt.ylim(0, max(y))
    plt.xlabel(xname,fontsize=14)
    plt.ylabel(yname,fontsize=14)
    plt.grid(True)
    title("'"+yname+"' en fonction de '"+xname+"' sur le training set",
          fontsize=18)
    
    # sauvegarde en png
    plt.savefig(yname+'_'+xname+'_reg'+datename+'.png')
    
# fonction pour tracer un histogramme

def traceHisto(yname):
    
    # affichage
    plt.figure(figsize = (12,10))

    # donnees    
    y = data[:,labels.index(yname)]
    
    # trace du graphe
    hist(y, bins=200)
    
    # gestion de l'affichage
    plt.ylabel(yname,fontsize=14)
    plt.grid(True)
    title("Histogramme de repartition de '"+yname+"' sur le training set",
          fontsize=18)
    
    # sauvegarde en png
    plt.savefig('hist_'+yname+'_all.png')
    plt.close("all")
    
# fonction pour tracer des repartitions en fonction d'un parametre discret

def traceHistoPar(yname, xname):

    plt.close("all")
    
    # donnees    
    y = data[:,labels.index(yname)]
    x = data[:,labels.index(xname)]
    
    # couper y en differentes box selon les labels donnes par x
    unique_x = np.unique(x)
    split_y = []
    
    plt.figure(figsize = (20,40))
    
    for i in range(len(unique_x)):
        split_y = y[x == unique_x[i]]
        split_y = np.array(split_y)
            
        # affichage
        if i == 1:
            ax1 = plt.subplot(len(unique_x)/2, 2, 1)
        if i > 1:
            plt.subplot(len(unique_x)/2, 2, i, sharex=ax1, sharey=ax1)
    
        # trace du graphe
        hist(split_y, bins=20)
        
        # gestion de l'affichage
        plt.ylabel(yname)
        plt.grid(True)
        title("Histogramme de repartition de '"+yname+"' sur '"+
        xname+"' numero "+str(int(unique_x[i])))
        
        # sauvegarde en png
    plt.savefig('hist_'+yname+'_par_'+xname+'.png')
    plt.close("all")
    

# trace nuage par

def traceNuagePar(yname, zname, xname):
    
    plt.close("all")
    
    # donnees    
    y = data[:,labels.index(yname)]
    x = data[:,labels.index(xname)]
    z = data[:,labels.index(zname)]
    
    # couper y en differentes box selon les labels donnes par x
    unique_x = np.unique(x)
    split_y = []
    
    plt.figure(figsize = (20,40))
    
    for i in range(len(unique_x)):
        
        split_y = y[x == unique_x[i]]
        split_y = np.array(split_y)
        
        split_z = z[x == unique_x[i]]
        split_z = np.array(split_z)
            
        # affichage
        if i == 1:
            ax1 = plt.subplot(len(unique_x)/2, 2, 1)
        if i > 1:
            plt.subplot(len(unique_x)/2, 2, i, sharex=ax1, sharey=ax1)
    
        # trace du graphe
        plt.scatter(split_y, split_z)
        
        # gestion de l'affichage
        plt.xlabel(yname)
        plt.ylabel(zname)
        plt.grid(True)
        title("'"+zname+"' en fonction de '"+yname+"' sur '"+
        xname+"' numero "+str(int(unique_x[i])))
        
        # sauvegarde en png
    plt.savefig(zname+'_'+yname+'_par_'+xname+'.png')
    plt.close("all")

# fonction pour tracer un parametre en fonction d'un parametre discret
# equivalente a la precedante mais avec une presentation boite a moustaches

def statsPar(yname, xname):
    
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
    
    return unique_x, split_y, count_y
    

def traceMoustachePar(yname, xname, defini, y_min, y_max):
    
    unique_x, split_y, count_y = statsPar(yname, xname)
    
    # affichage
    plt.figure(figsize = (28,10))
    
    # trace du graphe 1
    plt.subplot(1, 2, 2)
    plt.boxplot(split_y, positions = unique_x, patch_artist = True)
    
    # gestion de l'affichage 1
    if defini:
        plt.ylim(y_min, y_max)
    
    plt.xlabel(xname,fontsize=14)
    plt.ylabel(yname,fontsize=14)
    plt.grid(True)
    title("Repartition de '"+yname+"' par valeur de '"+xname+"' sur le training set",
          fontsize=18)
    
    # trace du graphe 2 histogramme
    plt.subplot(1, 2, 1)
    bar(unique_x, count_y, align = 'center')
    
    # gestion de l'affichage 2
    plt.xlim(-1, max(unique_x)+1)
    plt.ylim(0, max(count_y)+100)
    plt.xlabel(xname,fontsize=14)
    plt.ylabel("nombre d'objets",fontsize=14)
    plt.grid(True)
    title("Nombre d'objets du training set par valeur de '"+xname+"'",
          fontsize=18)
    
    # sauvegarde en png
    plt.savefig(yname+'_'+xname+datename+'_box'+'.png')
    plt.close("all")
    
# histogrammes prix, surface

traceHisto('prix')

traceHisto('surface')

# prix en fonction de la surface

traceNuageReg('surface','prix')
traceNuageReg('surface','ecart')

# prix en fonction de l'

y_max_prix = 0.2
y_min_prix = - y_max_prix

traceMoustachePar('ecart', 'arrondissement', 1, y_min_prix, y_max_prix)

# surface en fonction de l'arrondissement

traceMoustachePar('surface','arrondissement', 1, y_min_prix, y_max_prix)

# prix en fonction de la présence d'ascenseur

y_max_prix = 1
y_min_prix = - y_max_prix

traceMoustachePar('ecart', 'ascenseur', 1, y_min_prix, y_max_prix)

