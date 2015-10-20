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
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.ensemble import ExtraTreesRegressor
from sklearn.utils import shuffle
#from sklearn.cross_validation import cross_val_score
from sklearn.cross_validation import train_test_split
from sklearn.grid_search import GridSearchCV
from sklearn.grid_search import RandomizedSearchCV
from sklearn.svm import SVR
#from sklearn.svm import LinearSVR
import os
from sklearn import preprocessing 
from scipy.stats import randint
from scipy.stats import uniform
import scipy.stats as st

################################

### importation des donnees
##Extract data
###nom et format du fichier
## chemin en cours
os.getcwd()
df=pd.read_csv("Test_Python/Data_1910.csv") ### 1er appel
#df=pd.read_csv("Data_1910.csv")
#### matrice python avec les données
data=df.values 


####construction des descripteurs (#Marion) et des étiquettes
X_0=data[:,:-1]
y_0=data[:,-1]


n=len(X_0)### nombre d'annonces
k=len(X_0[0,:]) ###nombres de features

X=np.zeros((n,k))
y=np.zeros(n)


for i in range(n):
    for j in range(k):
        X[i,j]=X_0[i,j]*1.
    y[i]=y_0[i]*1.
        



####Mélange en vue des cross valid
X,y=shuffle(X,y)

        ############################


#######Construction des ensembles d'apprentissage et de test
### ratio test/dataset
ratio=0.2

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=ratio, random_state=0)
    
# Normalize data 
### on normalise les données d'apprentissage et on applique la même transfo à l'ensemble de test:
### ici toutes les donnees sont entre 0 et 1: on écrase entre min et max
min_max_scaler= preprocessing.MinMaxScaler()
X_train=min_max_scaler.fit_transform(X_train)
X_test=min_max_scaler.transform(X_test)

### normalisation: moyenne 0 et variance 1
mean, std = X_train.mean(axis=0), X_train.std(axis=0)

#### eviter les nan si std = 0: on laisse la variable pseudo-cste inchangée
for i in range(len(std)):
    if (std[i]==0):
        std[i]=1

X_train = (X_train - mean) / std ### on apprend sur desdonnées standardisées et 
####on applique notre predict à des données qui ont subi la mm transfo
X_test=(X_test-mean)/std
    

##### Machine learning
#######################################################
###☻Pour chaque méthode, nous donnons les paramètres de l'estimateur et nous
#### cherchons à trouver les meilleurs par cross validation
#### à la fin, on construit le predict associé à ces paramètres
cv=5### nb d'étape dans le cross valid
n_iter=20###  nombre  d'iteration dans le random grid search
########################
#### Trees

###Simple tree

#### Parameters ._max
max_depth_max_tree=15
min_samples_split_max_tree=10
min_samples_leaf_max_tree=10 


### liste de dictionnaires contenant les valeurs possibles de chaque paramètre
parameters_tree={'max_depth': randint(1,max_depth_max_tree+1),
                 'min_samples_split':randint(1,min_samples_split_max_tree+1),
                    'min_samples_leaf':randint(1,min_samples_leaf_max_tree+1)
}
### gridsearch qui trouve le set optimal de parametres
tree_reg = RandomizedSearchCV(DecisionTreeRegressor(), parameters_tree, cv=cv, n_iter=n_iter,n_jobs=-1)
### generation de l'arbre
tree_reg.fit(X_train, y_train)
### predicteur
y_tree=tree_reg.predict(X_test)
score_tree=tree_reg.score(X_test,y_test)



#### Bagging
### bornes des parametres ._max
max_depth_max_bag=10
min_samples_split_max_bag=10
min_samples_leaf_max_bag=10 
n_estimators_max_bag=10

### liste de dictionnaires contenant les valeurs possibles de chaque paramètre
parameters_tree_bag={'max_depth': randint(1,max_depth_max_bag+1),
                 'min_samples_split':randint(1,min_samples_split_max_bag+1),
                    'min_samples_leaf':randint(1,min_samples_leaf_max_bag+1),
"bootstrap": [True, False]
}

### Gridsearch  ### ameliorer par double apprentissage?
#tree_reg_bag=RandomizedSearchCV(DecisionTreeRegressor(), parameters_tree_bag, cv=cv,n_iter=n_iter)
bag_reg=RandomizedSearchCV(BaggingRegressor(DecisionTreeRegressor()),{'n_estimators':randint(20-n_estimators_max_bag,20+n_estimators_max_bag)},cv=cv,n_iter=n_iter,n_jobs=-1)
### .fit et predicteur
bag_reg.fit(X_train,y_train)
score_bag=bag_reg.score(X_test,y_test)



#### Random Forest
### bornes des parametres ._max
n_estimators_max_forest=10
min_samples_split_max_forest=10
max_depth_max_forest=10
min_samples_leaf_max_forest=10
max_features_max=10


parameters_tree_forest={'max_depth':randint(1,max_depth_max_forest+1),
"bootstrap": [True, False],
'min_samples_split':randint(1,min_samples_split_max_forest+1),
  "min_samples_leaf": randint(1, min_samples_leaf_max_forest+1),
"max_features": randint(1, max_features_max),
'n_estimators':randint(20-n_estimators_max_forest,20+n_estimators_max_forest)
}
### Gridsearch
forest_reg=RandomizedSearchCV(RandomForestRegressor(),parameters_tree_forest,cv=cv,n_iter=n_iter,n_jobs=-1)
forest_reg.fit(X_train,y_train)
score_forest=forest_reg.score(X_test,y_test)



####Extra Trees
### bornes des parametres ._max
n_estimators_max_extra=10
min_samples_split_max_extra=10
max_depth_max_extra=10
min_samples_leaf_max_extra=10

parameters_tree_extra={'max_depth':randint(1,max_depth_max_extra+1),
"bootstrap": [True, False],
'min_samples_split':randint(1,min_samples_split_max_extra+1),
  "min_samples_leaf": randint(1, min_samples_leaf_max_extra+1),
'n_estimators':randint(20-n_estimators_max_extra,20+n_estimators_max_extra)
}
### Gridsearch
extra_reg=RandomizedSearchCV(ExtraTreesRegressor(),parameters_tree_extra,cv=cv,n_iter=n_iter,n_jobs=-1)
extra_reg.fit(X_train,y_train)
score_extra=extra_reg.score(X_test,y_test)



### Gradient-boosting
### Parameters
learning_rate=0.1 ### utiliser une loi uniforme
n_estimators_max_boost=10
max_depth_max_boost=5
min_samples_split_max_boost=5

parameters_boost={'loss':['ls'],'max_depth':randint(1,max_depth_max_boost+1),
                  'min_samples_split':randint(1,min_samples_split_max_boost+1),'n_estimators':randint(100-n_estimators_max_boost,100+n_estimators_max_boost)}

boost_reg=RandomizedSearchCV(GradientBoostingRegressor(),parameters_boost,cv=cv,n_iter=n_iter,n_jobs=-1)
boost_reg.fit(X_train,y_train)
score_boost=boost_reg(X_test,y_test)

### SVR
###◘ spaces of parameters
precision=1
gamma_vec=10**(np.linspace(-4,0,precision)) #### defaut = 
C_vec=2**(np.linspace(0,8,precision)) ###defaut = 1
epsilon_vec=10**(np.linspace(-2,-0.5,precision))  ### defaut =0.1
degree_vec=range(3,6,4)

### list of dictionaries with all possible values of the parameters
parameters_SVR =[{'class_weight':['auto', None],'kernel': ['linear'], 'C': st.expon(scale=100),'epsilon':st.expon(scale=0.1)},
                 {'class_weight':['auto', None],'kernel': ['rbf'], 'gamma': st.expon(scale=.1),'C': st.expon(scale=100),'epsilon':st.expon(scale=0.1),'degree':randint(3,7)},
                {'class_weight':['auto', None],'kernel': ['poly'], 'gamma': st.expon(scale=.1),'C': st.expon(scale=100),'epsilon':st.expon(scale=0.1),'degree':randint(3,7)}]
### Gridsearch & fit
SVR_reg=RandomizedSearchCV(SVR(),{'gamma': st.expon(scale=.1),'C': st.expon(scale=100),'epsilon':st.expon(scale=0.1),'degree':randint(3,7)},cv=cv,n_iter=n_iter,n_jobs=-1)
SVR_reg.fit(X_train,y_train)
score_SVR=SVR_reg.score(X_test,y_test)

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

### Extra Trees: extra_reg
print ("Extra trees")
print (score_extra)
print(sum(map(abs,extra_reg.predict(X_test)-y_test))/len(X_test))
### Gradient boosting: boost_reg
print ("Gradient boosting")
print (score_boost)
print(sum(map(abs,boost_reg.predict(X_test)-y_test))/len(X_test))

### SVR: SVR_lin
print ("Svr")
print (score_SVR)
print(sum(map(abs,SVR_reg.predict(X_test)-y_test))/len(X_test))




