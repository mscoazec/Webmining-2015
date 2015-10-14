# -*- coding: utf-8 -*-
"""
Created on Mon Oct 12 12:59:32 2015

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
from sklearn.cross_validation import cross_val_score


################################
##Extract data
df=pd.read_excel("Data_2.xlsx")
data=df.values
X=data[:,:-1]
Y=data[:,-1]

X,Y=shuffle(X,Y)
##########################
# Normalize data
#mean, std = X.mean(axis=0), X.std(axis=0)
#X = (X - mean) / std
# Get rid of Nan values
#X[np.isnan(X)] = -1. 
############################
####Learning set: 
#### ratio r pour l'apprentissage; ici 80%/20%
def r(m):
    return (m*4)/5
    
n=len(Y)
borne=r(n)
X_learn=X[0:borne,:]
Y_learn=Y[0:borne]

#### Test set
X_test=X[borne:,:]
Y_test=Y[borne:]
###################################


##### Machine learning
#######################################################

####definition des parametres pertinents
#### il faudra faire des cross valid par methode d'apprentissage

####Tree & Forest 
###☻ les variables _max sont les bornes pour la recherche des parametres optimaux
### les autres variables contiendront les paramètres optimaux pour chaque méthode de learning
max_depth_max=4
max_depth=1###tree simple
max_depth_bag=1
max_depth_Forest=1

n_max= 10
n_estimators_Forest=1
n_estimators_Bag=1

min_samples_max= 10
min_samples_split_Forest=1
min_samples_split_Bag=1

####SVM


###ICA


#########################################################
####methodes d'apprentissage

#### Tree & Forest

##########################################"
####Tree simples
v=range(max_depth_max)
score_Reg=np.zeros(max_depth_max)

for i in v:
    
    Regressor= tree.DecisionTreeRegressor(criterion='mse',max_depth=i+1) 
    Regressor.fit(X_learn,Y_learn)
    score_Reg[i]=1-np.mean(cross_val_score(Regressor, X_learn, Y_learn, cv=5))
    
    
max_depth=np.argmin(score_Reg)
######
Tree_Regressor=tree.DecisionTreeRegressor(max_depth=max_depth+1)
Tree_Regressor.fit(X_learn,Y_learn)
score_tree=Tree_Regressor.score(X_test,Y_test)
########################################

#####"Bagging & random forest

####attention: dedoubler les vecteur car les optima ne st pas les mm pour forets et arbres
#### les variables score_ contiendront les scores calculés dans chaque boucle pour la cross valid
score_depth_Forest= np.zeros(max_depth_max)
score_samples_Forest=np.zeros(min_samples_max)
score_estimator_Forest=np.zeros(n_max)
score_depth_Bag= np.zeros(max_depth_max)
score_samples_Bag=np.zeros(min_samples_max)
score_estimator_Bag=np.zeros(n_max)
#### les vecteurs suivants contiendront k*(j,i) et j*(i) 
#### ce sont les paramètres optimaux relatifs aux boucles supérieures
n_estimators_Bag_vec=np.zeros((min_samples_max,max_depth_max)) ### longueur/j,i
n_estimators_Forest_vec=np.zeros((min_samples_max,max_depth_max)) ### longueur/j,i
min_samples_split_Bag_vec=np.zeros(max_depth_max) ### longueur/i
min_samples_split_Forest_vec=np.zeros(max_depth_max) ### longueur/i


#### Cross valid
### i est la mex_depth
### j min_samples_split
### k n_estimators
for i in v:
    
    for j in range(min_samples_max):
        
        for k in range(n_max):
#### on fait un parcours pour trouver k*(j,i)
            params = {'n_estimators': k+1, 'max_depth': i+1,
'min_samples_split':j+1}
            rfc=RandomForestRegressor(**params)
            clf=DecisionTreeRegressor(max_depth=i+1,min_samples_split=j+1)
            bag=BaggingRegressor(base_estimator=clf,n_estimators=k+1)
            rfc.fit(X_learn,Y_learn)
            bag.fit(X_learn,Y_learn)
            score_rfc = [np.mean(cross_val_score(rfc, X_learn, Y_learn, cv=5)),np.std(cross_val_score(rfc, X_learn, Y_learn, cv=5))]
            score_bag = [np.mean(cross_val_score(bag, X_learn, Y_learn, cv=5)),np.std(cross_val_score(bag, X_learn, Y_learn, cv=5))]
        
            score_estimator_Forest[k]=1-score_rfc[0]
            score_estimator_Bag[k]=1-score_bag[0]
    ### on stocke les k*(j,i)    
        n_estimators_Bag_vec[j,i]=int(np.argmin(score_estimator_Bag)//1)
        n_estimators_Forest_vec[j,i]=int(np.argmin(score_estimator_Forest)//1)
#### on calcule alors les nouveaux arbres avec i, j et k*(j,i)
        params = {'n_estimators': int(n_estimators_Forest_vec[j,i]+1), 'max_depth': i+1,
                     'min_samples_split':j+1}
        rfc=RandomForestRegressor(**params)
        clf=DecisionTreeRegressor(max_depth=i+1,min_samples_split=j+1)
        bag=BaggingRegressor(base_estimator=clf,n_estimators=int(1+n_estimators_Bag_vec[j,i]))
        rfc.fit(X_learn,Y_learn)
        bag.fit(X_learn,Y_learn)
        score_rfc = [np.mean(cross_val_score(rfc, X_learn, Y_learn, cv=5)),np.std(cross_val_score(rfc, X_learn, Y_learn, cv=5))]
        score_bag = [np.mean(cross_val_score(bag, X_learn, Y_learn, cv=5)),np.std(cross_val_score(bag, X_learn, Y_learn, cv=5))]
          
        score_samples_Bag[j]=1-score_bag[0]
        score_samples_Forest[j]=1-score_rfc[0]
### on stocke les j*(i)
    min_samples_split_Bag_vec[i]=int(np.argmin(score_samples_Bag)//1)
    min_samples_split_Forest_vec[i]=int(np.argmin(score_samples_Forest)//1)
### idem, on recalcule les arbres avec i, j*(i) et k*(j*(i),i)
    params = {'n_estimators': int(1+n_estimators_Forest_vec[min_samples_split_Forest_vec[i],i]), 'max_depth':1+ i,
   'min_samples_split':int(1+min_samples_split_Forest_vec[i])}
    rfc=RandomForestRegressor(**params)
    clf=DecisionTreeRegressor(max_depth=1+i,min_samples_split=int(1+min_samples_split_Bag_vec[i]))
    bag=BaggingRegressor(base_estimator=clf,n_estimators=int(1+n_estimators_Bag_vec[min_samples_split_Bag_vec[i],i]))
    rfc.fit(X_learn,Y_learn)
    bag.fit(X_learn,Y_learn)
    score_rfc = [np.mean(cross_val_score(rfc, X_learn, Y_learn, cv=5)),np.std(cross_val_score(rfc, X_learn, Y_learn, cv=5))]
    score_bag = [np.mean(cross_val_score(bag, X_learn, Y_learn, cv=5)),np.std(cross_val_score(bag, X_learn, Y_learn, cv=5))]
          
    score_depth_Bag[i]=1-score_bag[0]
    score_depth_Forest[i]=1-score_rfc[0]
### on trouve alors i* et on a les paramètres optimaux pour nos méthodes de learning
max_depth_bag=int(np.argmin(score_depth_Bag)//1)
max_depth_Forest=int(np.argmin(score_depth_Forest)//1)

min_samples_split_Bag=int(min_samples_split_Bag_vec[max_depth_bag]//1)
min_samples_split_Forest=int(min_samples_split_Forest_vec[max_depth_Forest]//1)

n_estimators_Bag=int(n_estimators_Bag_vec[min_samples_split_Bag,max_depth_bag]//1)
n_estimators_Forest=int(n_estimators_Forest_vec[min_samples_split_Forest,max_depth_Forest]//1)

###################
#### on applique enfin nos méthodes avec les bons paramètres
params = {'n_estimators': int(1+n_estimators_Forest), 'max_depth': int(1+max_depth_Forest),
   'min_samples_split':int(1+min_samples_split_Forest)}
rfc=RandomForestRegressor(**params)
clf=DecisionTreeRegressor(max_depth=1+max_depth_bag,min_samples_split=1+min_samples_split_Bag)
bag=BaggingRegressor(base_estimator=clf,n_estimators=int(1+n_estimators_Bag))
rfc.fit(X_learn,Y_learn)
bag.fit(X_learn,Y_learn)
########################

score_rfc = rfc.score(X_test,Y_test)
score_bag = bag.score(X_test,Y_test)
    
     

           



#####SVM



#####ICA







#######Bilan
###fonction d'erreur
def f(z):
    return abs(z)
    
    ### on affiche les scores et la sommes des écarts aux prix réels par méthode
print "Random forest"  +" "+"score"+" "+"ecart"
print score_rfc 
print sum(map(f,rfc.predict(X_test)-Y_test))
print "Bagging"+" "+"score"+" "+"ecart"
print score_bag
print sum(map(f,bag.predict(X_test)-Y_test))
print "Tree" +" "+"score"+" "+"ecart"
print score_tree
print sum(map(f,Tree_Regressor.predict(X_test)-Y_test))

######################

W=Y_test[0:8]
W0=rfc.predict(X_test)
W1=W0[0:8]

V=np.sort(np.unique(W0))

    



