# -*- coding: utf-8 -*-
"""
Created on Sun Oct 18 15:29:22 2015
@author: Emmanuel
"""

####Packages à importer
print(__doc__)
from time import time
from operator import itemgetter
import pandas as pd
from sklearn import tree
import numpy as np
from sklearn.ensemble import AdaBoostRegressor
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
from sklearn import preprocessing 
from scipy.stats import randint
from scipy.stats import uniform
import scipy.stats as st
from sklearn import metrics
import matplotlib.pyplot as plt
from sklearn.neighbors import KNeighborsRegressor
import csv
################################




class Learning:
    def __init__(self): 
        self.database = ""#"Test_Python/Data_2010.csv" ### base de donnees des maisons ### EX:"Test_Python/Data_2010.csv"
        self.X=[] ###X_
        self.label=[] ### y_
        self.ratio= 0.2 ### ratio test / length database
        self.X_train=[]
        self.X_test=[]
        self.y_train=[]
        self.y_test=[]
        self.transfo=[],[]
        self.cv = 5
        self.n_iter= 200
        self.max_depth_max=100
        self.min_samples_split_max=100
        self.min_samples_leaf_max=100
        self.max_leaf_nodes_max=100
        self.max_features_max=80
        self.n_estimators_max=80
        self.n_neigh_max=15
        self.tree_reg=[]
        self.ada_reg=[]
        self.Kneigh_reg=[]
        self.bag_reg=[]
        self.forest_reg=[]
        self.extra_reg=[]
        self.boost_reg=[]
        self.SVR_reg=[]
        self.loss="ls"
        self.kernel="rbf"


    def matrix(self):  ### renvoie matrice des descripteurs, vecteur prix
        df=pd.read_csv(self.database)
        data=df.values  #### matrice python avec les données
        X_0=data[:,:-1]####construction des descripteurs (#Marion) et des étiquettes
        y_0=data[:,-1]
        n=len(X_0)### nombre d'annonces
        k=len(X_0[0,:]) ###nombres de features
        X=np.zeros((n,k)) ### descripteurs
        y=np.zeros(n) ### prix
        for i in range(n):
            for j in range(k):
                if (np.isnan(X_0[i,j])):
                    X[i,j]=-1
                else:
                    X[i,j]=X_0[i,j]*1.0
            y[i]=(y_0[i]//1000)*1000.0
        X,y=shuffle(X,y) ####Mélange en vue des cross valid
        self.X= X
        self.label = y 

    def learning_data(self): ###renvoie X_train, X_test, y_train, y_test
                                    ### ratio représente la taille relative de X_test par rapport à database
    
        X = self.X
        y= self.label
        X_train, X_test, y_train, y_test = train_test_split( X, y, test_size=self.ratio, random_state=0)
        self.X_train=X_train
        self.X_test=X_test
        self.y_train=y_train
        self.y_test=y_test
        
    def transform(self): ### fonction qui transforme nos données et permet d'appliquer la mm transfo aux prochains inputs
        X_train=self.X_train
        ### normalisation: moyenne 0 et variance 1
        mean_0=X_train.mean(axis=0)
        std_0= X_train.std(axis=0)
        for i in range(len(std_0)):#### eviter les nan si std = 0: on laisse la variable pseudo-cste inchangée
            if (std_0[i]==0):
                std_0[i]=1.   
        self.transfo=mean_0,std_0

    
    def transform_data(self,z):
        mean,std = self.transfo
        return (z-mean)/std
  
    def Var_Creation(self): ### cree les ensembles de train et de test
        self.X_train=self.transform_data(self.X_train)
        self.X_test=self.transform_data(self.X_test)
        
        
    def Initialisation_data(self):
        self.matrix() #### creation de X,y descripteurs, prix
        self.learning_data()  ### creation des variables d'apprentissage et de test
        self.transform() ### cree la fonction de normalisation
        self.Var_Creation() ## normamlise les inputs

        
        
        
        
    def simple_tree(self): #### methode d'apprentissage avec arbre simple
                                                ### cv: nb d'etapes ds la cross valid
                                                ### n_iter est le nb d'iteration pour la random cross valid
                
        parameters_tree={'max_depth': randint(1,self.max_depth_max+1),
                 'min_samples_split':randint(1,self.min_samples_split_max+1),
                    'min_samples_leaf':randint(1,self.min_samples_leaf_max+1),
                    'max_leaf_nodes':randint(2,self.max_leaf_nodes_max),
        "max_features": randint(1, self.max_features_max)}
        tree_reg = RandomizedSearchCV(DecisionTreeRegressor(), param_distributions=parameters_tree, cv=self.cv, n_iter=self.n_iter,n_jobs=-1)
        X_train, y_train =self.X_train,self.y_train
        tree_reg.fit(X_train, y_train)
        self.tree_reg=tree_reg.best_estimator_
        
        
    def adaboost(self):### changer le tree + options
        X_train, y_train =self.X_train,self.y_train
        parameters_ada={'n_estimators':randint(45,self.n_estimators_max),'learning_rate':[1.0]}
        ada_reg=RandomizedSearchCV(AdaBoostRegressor(DecisionTreeRegressor(),loss='square'),param_distributions=parameters_ada,cv=self.cv, n_iter=self.n_iter,n_jobs=-1)
        ada_reg.fit(X_train,y_train)
        self.ada_reg=ada_reg.best_estimator_
        
    def Kneighbors(self): ### changer metric
        X_train, y_train =self.X_train,self.y_train
        param_nei={'n_neighbors':randint(4,self.n_neigh_max)}
        Kneigh_reg=RandomizedSearchCV(KNeighborsRegressor(),param_distributions=param_nei,cv=self.cv, n_iter=self.n_iter,n_jobs=-1)
        Kneigh_reg.fit(X_train,y_train)
        self.Kneigh_reg=Kneigh_reg.best_estimator_

    def bagging(self): ##changer tree et options
        X_train, y_train =self.X_train,self.y_train
        parameters_bag={'n_estimators':randint(15,self.n_estimators_max),"bootstrap": [True, False]}
        bag_reg=RandomizedSearchCV(BaggingRegressor(DecisionTreeRegressor()),param_distributions=parameters_bag,cv=self.cv, n_iter=self.n_iter,n_jobs=-1)
        bag_reg.fit(X_train,y_train)
        self.bag_reg=bag_reg.best_estimator_

    def RandomFo(self):
        parameters_forest={'max_depth':randint(1,self.max_depth_max+1),
                                "bootstrap": [True, False],
    'min_samples_split':randint(1,self.min_samples_split_max+1),
    "min_samples_leaf": randint(1,self.min_samples_leaf_max+1),
    "max_features": randint(1, self.max_features_max),
    'n_estimators':randint(15,self.n_estimators_max),
}
### Gridsearch
        X_train, y_train =self.X_train,self.y_train
        forest_reg=RandomizedSearchCV(RandomForestRegressor(),param_distributions=parameters_forest,cv=self.cv, n_iter=self.n_iter,n_jobs=-1)
        forest_reg.fit(X_train,y_train)
        self.forest_reg=forest_reg.best_estimator_
        
    
    def Extra(self):
        parameters_extra={'max_depth':randint(1,self.max_depth_max+1),
"bootstrap": [True, False],
'min_samples_split':randint(1,self.min_samples_split_max+1),
  "min_samples_leaf": randint(1, self.min_samples_leaf_max+1),
'n_estimators':randint(20,20+self.n_estimators_max)
}
        X_train, y_train =self.X_train,self.y_train
        extra_reg=RandomizedSearchCV(ExtraTreesRegressor(),param_distributions=parameters_extra,cv=self.cv, n_iter=self.n_iter,n_jobs=-1)
        extra_reg.fit(X_train,y_train)
        self.extra_reg=extra_reg.best_estimator_
        
    def Gradient(self): 
        X_train, y_train =self.X_train,self.y_train
        parameters_boost={'max_depth':randint(1,self.max_depth_max+1),
                  'min_samples_split':randint(1,self.min_samples_split_max+1),'n_estimators':randint(80,100+self.n_estimators_max)}
        boost_reg=RandomizedSearchCV(GradientBoostingRegressor(loss=self.loss),param_distributions=parameters_boost,cv=self.cv, n_iter=self.n_iter,n_jobs=-1)
        boost_reg.fit(X_train,y_train)
        self.boost_reg=boost_reg.best_estimator_

    def SVR(self):### ajout option parametres
        X_train, y_train =self.X_train,self.y_train
        param_SVR={'gamma': st.expon(scale=.1),'C': st.expon(scale=100),'epsilon':st.expon(scale=0.1),'degree':randint(3,7)}
        SVR_reg=RandomizedSearchCV(SVR(kernel=self.kernel),param_SVR,cv=self.cv, n_iter=self.n_iter,n_jobs=-1)
        SVR_reg.fit(X_train,y_train)
        self.SVR_reg=SVR_reg.best_estimator_
        

        
test = Learning()
test.database="Test_Python/Data_2610.csv"
#test.database="Data_2110.csv"
test.Initialisation_data()### cree les donnes de test et de validation
test.simple_tree()
test.adaboost()
test.Kneighbors()
test.bagging()
test.RandomFo()
test.Extra()
test.Gradient()
test.SVR()






#### Comparaison des scores et "erreur moyenne" en terme de prix
### les noms des objets à appeler sont donnés en-dessous

X_train, y_train =test.X_train,test.y_train
X_test, y_test =test.X_test,test.y_test
print ("Scores and average gap  of different methods")
print 

### tree simple: tree_reg
print ("Simple tree")
print (test.tree_reg.score(X_test,y_test))
print(sum(map(abs,test.tree_reg.predict(X_test)-y_test))/len(X_test))

### Adaboost
print ("Ada")
print (test.ada_reg.score(X_test,y_test))
print(sum(map(abs,test.ada_reg.predict(X_test)-y_test))/len(X_test))

### K-neighbour
print("K_neighbours")
print (test.Kneigh_reg.score(X_test,y_test))
print (sum(map(abs,test.Kneigh_reg.predict(X_test)-y_test))/len(X_test))


### bagging: bag_reg
print ("Bagging")
print (test.bag_reg.score(X_test,y_test))
print(sum(map(abs,test.bag_reg.predict(X_test)-y_test))/len(X_test))


### Random forest: forest_reg
print ("Random forest")
print (test.forest_reg.score(X_test,y_test))
print(sum(map(abs,test.forest_reg.predict(X_test)-y_test))/len(X_test))

### Extra Trees: extra_reg
print ("Extra trees")
print (test.extra_reg.score(X_test,y_test))
print(sum(map(abs,test.extra_reg.predict(X_test)-y_test))/len(X_test))
### Gradient boosting: boost_reg
print ("Gradient boosting")
print (test.boost_reg.score(X_test,y_test))
print(sum(map(abs,test.boost_reg.predict(X_test)-y_test))/len(X_test))

### SVR: SVR_reg
print ("Svr")
print (test.SVR_reg.score(X_test,y_test))
print(sum(map(abs,test.SVR_reg.predict(X_test)-y_test))/len(X_test))



pred=test.forest_reg
ecart_pred=pred.predict(X_test)-y_test
M=np.zeros((len(y_test),len(X_test[0,:])+1))
obj=pd.read_csv(test.database)
names=obj.columns


for i in range(len(M)):
    for j in range(len(X_test[0,:])):
        M[i,j]=X_test[i,j]
    M[i,-1]=ecart_pred[i]
    

writer = csv.writer(open('errors.csv', 'wb'))

writer.writerow(obj.columns)
for values in M:
    writer.writerow(values)




