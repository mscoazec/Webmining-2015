# -*- coding: utf-8 -*-
"""
Created on Sun Oct 18 15:29:22 2015

@author: Emmanuel
"""

####Packages à importer
import pandas as pd
from sklearn import tree
import numpy as np
from sklearn.ensemble import  BaggingRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.utils import shuffle
#from sklearn.cross_validation import cross_val_score
from sklearn.cross_validation import train_test_split
from sklearn.grid_search import GridSearchCV
from sklearn.svm import SVR
from sklearn.svm import LinearSVR
import csv as csv



################################

### importation des donnees
##Extract data
###nom et format du fichier
df=pd.read_excel("Data_1610.xlsx")
#### matrice python avec les données
data=df.values 

####construction des descripteurs (#Marion) et des étiquettes
X=data[:,:-1]
y=data[:,-1]
X[:,57]=map(float,X[:,57]) ### conversion des m²
y=map(float,y) ### conversion des prix

####Mélange en vue des cross valid
X,y=shuffle(X,y)

        
######################## utilité ici?
# Normalize data 
#mean, std = X.mean(axis=0), X.std(axis=0)
#X = (X - mean) / std
# Get rid of Nan values
#X[np.isnan(X)] = -1. 
############################


#######Construction des ensembles d'apprentissage et de test
### ratio test/dataset
ratio=0.2

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=ratio, random_state=0)
    

##### Machine learning
#######################################################
###☻Pour chaque méthode, nous donnons les paramètres de l'estimateur et nous
#### cherchons à trouver les meilleurs par cross validation
#### à la fin, on construit le predict associé à ces paramètres
cv=5### nb d'étape dans le cross valid
########################
#### Trees

###Simple tree

#### Parameters ._max
max_depth_max_tree=5 
min_samples_split_max_tree=5

### liste de dictionnaires contenant les valeurs possibles de chaque paramètre
parameters_tree={'max_depth': range(1,max_depth_max_tree+1),
                 'min_samples_split':range(1,min_samples_split_max_tree+1)}
### gridsearch qui trouve le set optimal de parametres
tree_reg = GridSearchCV(DecisionTreeRegressor(), parameters_tree, cv=cv)
### generation de l'arbre
tree_reg.fit(X_train, y_train)
### predicteur
y_tree=tree_reg.predict(X_test)
score_tree=tree_reg.score(X_test,y_test)

#### Bagging
### bornes des parametres ._max
n_estimators_max_bag=4
min_samples_split_max_bag=4
max_depth_max_bag=4

parameters_tree_bag={'max_depth':range(1,max_depth_max_bag+1),
'min_samples_split':range(1,min_samples_split_max_bag+1)}

### Gridsearch
tree_reg_bag=GridSearchCV(DecisionTreeRegressor(), parameters_tree_bag, cv=cv)
bag_reg=GridSearchCV(BaggingRegressor(tree_reg_bag),{'n_estimators':range(1,n_estimators_max_bag)},cv=cv)
### .fit et predicteur
bag_reg.fit(X_train,y_train)
score_bag=bag_reg.score(X_test,y_test)



#### Random Forest
### bornes des parametres ._max
n_estimators_max_forest=4
min_samples_split_max_forest=4
max_depth_max_forest=4

parameters_tree_forest={'max_depth':range(1,max_depth_max_forest+1),
'min_samples_split':range(1,min_samples_split_max_forest+1),'n_estimators':range(1,n_estimators_max_forest)}
### Gridsearch
forest_reg=GridSearchCV(RandomForestRegressor(),parameters_tree_forest,cv=cv)
forest_reg.fit(X_train,y_train)
score_forest=forest_reg.score(X_test,y_test)

### SVR
###◘ spaces of parameters
precision=5
gamma_vec=10**(np.linspace(-4,0,precision))
C_vec=2**(np.linspace(0,8,precision))
epsilon_vec=10**(np.linspace(-3,-0.5,precision))

### list of dictionaries with all possible values of the parameters
parameters_SVR =[{'kernel': ['linear'], 'C': C_vec,'epsilon':epsilon_vec},
                 {'kernel': ['rbf'], 'gamma': gamma_vec,'C': C_vec,'epsilon':epsilon_vec},
                {'kernel': ['poly'], 'gamma': gamma_vec,'C': C_vec,'epsilon':epsilon_vec}]
### Gridsearch & fit
#SVR_reg=GridSearchCV(SVR(cache_size=1000),parameters_SVR,cv=cv)
#SVR_reg.fit(X_train,y_train)

### linear svr faster
SVR_lin=GridSearchCV(LinearSVR(),[{'C': C_vec,'epsilon':epsilon_vec}],cv=cv)
SVR_lin.fit(X_train,y_train)

score_linSVR=SVR_lin.score(X_test,y_test)

                    
                    


#### Comparaison des scores et "erreur moyenne" en terme de prix
### les noms des objets à appeler sont donnés en-dessous


print ("Scores and average gap  of different methods")
print ()

### tree simple: tree_reg
print ("Simple tree")
print (score_tree)
print(sum(map(abs,tree_reg.predict(X_test)-y_test))/len(X_test))


### bagging: bag_reg
print ("Bagging")
print (score_bag)
print(sum(map(abs,bag_reg.predict(X_test)-y_test))/len(X_test))


### Random forest: forest_reg
print ("Random forest")
print (score_forest)
print(sum(map(abs,forest_reg.predict(X_test)-y_test))/len(X_test))


### SVR: SVR_lin
print ("Linear Svr")
print (score_linSVR)
print(sum(map(abs,SVR_lin.predict(X_test)-y_test))/len(X_test))

























