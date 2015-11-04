# -*- coding: utf-8 -*-
"""
Created on Sun Oct 18 15:29:22 2015
@author: Emmanuel
"""

####Packages à importer
print(__doc__)
import pickle
import pandas as pd
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
#from sklearn.grid_search import GridSearchCV
from sklearn.grid_search import RandomizedSearchCV
from sklearn.svm import SVR
#from sklearn.svm import LinearSVR
from scipy.stats import randint
import scipy.stats as st
import matplotlib.pyplot as plt
from sklearn.neighbors import KNeighborsRegressor
import csv
from sklearn.feature_selection import f_regression
from sklearn.feature_selection import SelectKBest
from sklearn.pipeline import Pipeline
from sklearn.cluster import KMeans
from sklearn.ensemble.partial_dependence import plot_partial_dependence
from sklearn.ensemble.partial_dependence import partial_dependence
from sklearn.datasets.california_housing import fetch_california_housing
from sklearn.linear_model import LinearRegression
from sklearn.linear_model import RANSACRegressor

################################




class Learning:
    def __init__(self): 
        self.database = ""#"Test_Python/Data_2010.csv" ### base de donnees des maisons ### EX:"Test_Python/Data_2010.csv"
        self.X=[] ###X_
        self.label=[] ### y_
        self.ratio= 0.15 ### ratio test / length database
        self.X_train=[]
        self.X_test=[]
        self.y_train=[]
        self.y_test=[]
        self.transfo=[],[]
        self.cv = 5
        self.n_iter=100
        self.max_depth_max=100
        self.min_samples_split_max=50
        self.min_samples_leaf_max=50
        self.max_leaf_nodes_max=50
        self.max_features_max=20
        self.n_estimators_max=80
        self.n_neigh_max=20
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
        
        self.prix_max=25000000
        self.prix_min=50000
        self.surf_max=400
        self.surf_min=7
        self.prix_m2_max=32000
        self.prix_m2_min=5000
        self.room_max=10
        self.room_min=0
        
        self.categorie1=1
        self.categorie2=1
        self.categorie3=1
        
        self.location = 0

  

    def matrix(self):  ### renvoie matrice des descripteurs, vecteur prix
        df=pd.read_csv(self.database)
                
        
        names0=df.columns
        names=[]
        for i in range(len(names0)):
            names.append(names0[i])   
        index_surface=names.index("surface_q")
        index_adt=names.index("arrondissement_q")
        index_precis=names.index("coordonnees_precises")
        index_prix=names.index("prix")
        index_piece=names.index("nombre_pieces_q")
        data=df.values  #### matrice python avec les données  
        data=data[(data[:,index_prix]<self.prix_max)&(data[:,index_prix]>self.prix_min)]
        data=data[np.isnan(data[:,index_adt])==False]
        data=data[np.isnan(data[:,index_surface])==False]
        data=data[(data[:,index_surface]>self.surf_min)&(data[:,index_surface]<self.surf_max)]
        data=data[(data[:,index_prix]/data[:,index_surface]>self.prix_m2_min)&(data[:,index_prix]/data[:,index_surface]<self.prix_m2_max)]        
        #data=data[(data[:,index_precis]==1)]
        data=data[(data[:,index_piece]<self.room_max)&(data[:,index_piece]>self.room_min)]
        
        if self.categorie1==0:
            data=data[((data[:,index_adt]<18)&(data[:,index_adt]<>12)&(data[:,index_adt]<>13)&(data[:,index_adt]<>11))]
       
        if self.categorie3==0:
            data=data[((data[:,index_adt]<3)|(data[:,index_adt]>8))&(data[:,index_adt]!=1)&(data[:,index_adt]!=10)]
            
        if self.categorie2==0:
            data=data[(((data[:,index_adt]<14)|(data[:,index_adt]>17))&(data[:,index_adt]!=2)&(data[:,index_adt]!=9))]
        
             
                
        X_0=data[:,:-1]####construction des descripteurs (#Marion) et des étiquettes
        y_0=data[:,-1]#/data[:,index_surface]
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
            if self.location==0:
                y[i]=(y_0[i]//1000)*1000.0
            else:
                y[i]=(y_0[i]//10)*10.0
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

        
        
        
        
    def simple_tree(self): 
        tree_reg = DecisionTreeRegressor()
        #RandomizedSearchCV(DecisionTreeRegressor(), param_distributions=parameters_tree, cv=self.cv, n_iter=self.n_iter,n_jobs=-1)
        X_train, y_train =self.X_train,self.y_train
        tree_reg.fit(X_train, y_train)
        self.tree_reg=tree_reg#.best_estimator_
        
        
    def adaboost(self):### changer le tree + options
        X_train, y_train =self.X_train,self.y_train
        #parameters_ada={'n_estimators':randint(45,self.n_estimators_max),'learning_rate':[1.0]}
        ada_reg=AdaBoostRegressor(RandomForestRegressor())
        ada_reg.fit(X_train,y_train)
        self.ada_reg=ada_reg
        
    def Kneighbors(self): ### changer metric
        X_train, y_train =self.X_train,self.y_train
        param_nei={'n_neighbors':randint(4,self.n_neigh_max)}
        Kneigh_reg=RandomizedSearchCV(KNeighborsRegressor(),param_distributions=param_nei,cv=self.cv, n_iter=self.n_iter,n_jobs=-1)
        Kneigh_reg.fit(X_train,y_train)
        self.Kneigh_reg=Kneigh_reg.best_estimator_

    def bagging(self): ##changer tree et options
        X_train, y_train =self.X_train,self.y_train
        parameters_bag={'n_estimators':randint(10,self.n_estimators_max),"bootstrap": [True, False]}
        bag_reg=RandomizedSearchCV(BaggingRegressor(DecisionTreeRegressor()),param_distributions=parameters_bag,cv=self.cv, n_iter=self.n_iter,n_jobs=-1)
        bag_reg.fit(X_train,y_train)
        self.bag_reg=bag_reg.best_estimator_

    def RandomFo(self):
        parameters_forest={'n_estimators':randint(10,self.n_estimators_max),
                "bootstrap": [True, False]}
        X_train, y_train =self.X_train,self.y_train
        forest_reg=RandomizedSearchCV(RandomForestRegressor(),param_distributions=parameters_forest,cv=self.cv, n_iter=self.n_iter,n_jobs=-1)
        forest_reg.fit(X_train,y_train)
        self.forest_reg=forest_reg.best_estimator_
        
    
    def Extra(self):
        parameters_extra={"bootstrap": [True, False],
'n_estimators':randint(20,self.n_estimators_max)
}
        X_train, y_train =self.X_train,self.y_train
        extra_reg=RandomizedSearchCV(ExtraTreesRegressor(),param_distributions=parameters_extra,cv=self.cv, n_iter=self.n_iter,n_jobs=-1)
        extra_reg.fit(X_train,y_train)
        self.extra_reg=extra_reg.best_estimator_
        
    def Gradient(self): 
        X_train, y_train =self.X_train,self.y_train
        parameters_boost={'max_depth':randint(3,self.max_depth_max+1),
  'n_estimators':randint(80,100+self.n_estimators_max)}
        boost_reg=RandomizedSearchCV(GradientBoostingRegressor(loss=self.loss),param_distributions=parameters_boost,cv=self.cv, n_iter=self.n_iter,n_jobs=-1)
        boost_reg.fit(X_train,y_train)
        self.boost_reg=boost_reg.best_estimator_

    def SVR(self):### ajout option parametres
        X_train, y_train =self.X_train,self.y_train
        param_SVR={'gamma': st.expon(scale=.1),'C': st.expon(scale=100),'epsilon':st.expon(scale=0.1),'degree':randint(3,7)}
        SVR_reg=RandomizedSearchCV(SVR(kernel=self.kernel),param_SVR,cv=self.cv, n_iter=self.n_iter,n_jobs=-1)
        SVR_reg.fit(X_train,y_train)
        self.SVR_reg=SVR_reg.best_estimator_
        

        
        
        


Cluster1 = Learning()
Cluster1.database="Test_Python/Data_0311.csv"#"Test_Python/Data_0411_loc"#
Cluster1.Initialisation_data()### cree les donnes de test et de validation

#Cluster2 = Learning()
#Cluster2.database="Test_Python/Data_0411_loc"
#Cluster2.location=1
#Cluster2.prix_max=25000000
#Cluster2.prix_min=50000
#Cluster2.surf_max=400
#Cluster2.surf_min=7
#Cluster2.prix_m2_max=32000
#Cluster2.prix_m2_min=5000
#Cluster2.room_max=10
#self.room_min=0
#Cluster2.Initialisation_data()### cree les donnes de test et de validation


#################################


clas=Cluster1
clas.X.shape
################## learning methods
###Cluster1:
#clas.simple_tree()
clas.adaboost()
###gridsearch
#clas.RandomFo()
#clas.Kneighbors()
#clas.bagging()
#clas.Extra()
#clas.Gradient()
#clas.SVR()




clf=clas.ada_reg
# save the classifier with pickle
fid = open('Pred/fit_basic', 'wb') 
pickle.dump(clf,fid)
fid.close()



####
##
X_train, y_train =clas.X_train,clas.y_train
X_test, y_test =clas.X_test,clas.y_test


print ("score et ecart")
print (clf.score(X_test,y_test))
print(sum(map(abs,clf.predict(X_test)-y_test))/len(X_test))
v=(clf.predict(X_test)-y_test)/y_test
v=map(abs,v)
print sum(v)/len(X_test)


   







############################
#########################""
obj=pd.read_csv(clas.database)
names0=obj.columns
names=[]
for i in range(len(names0)):
    names.append(names0[i])
index_surface=names.index("surface_q")
index_adt=names.index("arrondissement_q")
index_piece=names.index("nombre_pieces_q")
index_x=names.index("coordonnee_x_q")
index_y=names.index("coordonnee_y_q")
index_etage=names.index("etage_q")
index_ch=names.index("nombre_chambres_q")



Q=np.zeros(len(y_test))
for i in range(len(Q)):
    Q[i]=y_test[i]

Qt=np.zeros(len(y_train))
for i in range(len(Qt)):
    Qt[i]=y_train[i]

Q2=np.zeros(len(y_test))
    
  
    
scores=np.zeros(len(np.unique(X_test[:,index_adt]))) 

for i in range(len(np.unique(X_test[:,index_adt]))):
    p=np.unique(X_test[:,index_adt])[i]
    print i+1
    reg=LinearRegression()
    #reg = RANSACRegressor(reg)
    M0=X_train[X_train[:,index_adt]==p]
    M1=X_test[X_test[:,index_adt]==p]
    Z=np.ones((len(M0),2))
    Z[:,1] = M0[:,index_surface]
    Z2 =np.ones((len(M1),2))
    Z2[:,1] = M1[:,index_surface]
    reg.fit(Z,y_train[X_train[:,index_adt]==p])
    scores[i]=reg.score(Z2,y_test[X_test[:,index_adt]==p])
    print scores[i]
    #print reg.coef_
    Qt[X_train[:,index_adt]==p]=y_train[X_train[:,index_adt]==p]-reg.predict(Z)
    Q[X_test[:,index_adt]==p]=y_test[X_test[:,index_adt]==p]-reg.predict(Z2)
    Q2[X_test[:,index_adt]==p]=reg.predict(Z2)
    
    s="Pred/fit_adt_"+str(i+1)+".pickle"
    fid = open(s, 'wb') 
    pickle.dump(reg,fid)
    fid.close()

index=np.argsort(scores)
list_index=[]
for i in index:
    if scores[i]<0.88:
        list_index.append(i)


scores2=np.zeros((len(list_index)))
for i in range(len(list_index)):
    p=np.unique(X_test[:,index_adt])[list_index[i]]
    print list_index[i]+1
    reg=AdaBoostRegressor(RandomForestRegressor())
    Z=X_train[X_train[:,index_adt]==p]
    Z2=X_test[X_test[:,index_adt]==p]
    reg.fit(Z,y_train[X_train[:,index_adt]==p])
    scores2[i]=reg.score(Z2,y_test[X_test[:,index_adt]==p])
    print scores2[i]
    Qt[X_train[:,index_adt]==p]=y_train[X_train[:,index_adt]==p]-reg.predict(Z)
    Q[X_test[:,index_adt]==p]=y_test[X_test[:,index_adt]==p]-reg.predict(Z2)
    Q2[X_test[:,index_adt]==p]=reg.predict(Z2)
    s="Pred/fit_adt_"+str(list_index[i]+1)+".pickle"
    fid = open(s, 'wb') 
    pickle.dump(reg,fid)
    fid.close()

list_index2=[]
index=np.argsort(scores2)
for i in index:
    if scores2[i]<0.88:
        list_index2.append(list_index[i])

n=len(list_index2)
b_train=True
b_test=True


for i in range(n):
    b_train=b_train&(X_train[:,index_adt]==np.unique(X_train[:,index_adt])[list_index2[i]])
    b_test=b_test&(X_test[:,index_adt]==np.unique(X_test[:,index_adt])[list_index2[i]])

reg2=AdaBoostRegressor(RandomForestRegressor())
reg2.fit(X_train[b_train],y_train[b_train])
reg2.score(X_test[b_test],y_test[b_test])
Qt[b_train]=Qt[b_train]-reg2.predict(X_train[b_train])
Q[b_test]=Q[b_test]-reg2.predict(X_test[b_test])
Q2[b_test]=reg2.predict(X_test[b_test])

for i in range(n):
    s="Pred/fit_adt_"+str(list_index2[i]+1)+".pickle"
    fid = open(s, 'wb') 
    pickle.dump(reg2,fid)
    fid.close()



r=AdaBoostRegressor(RandomForestRegressor())
r.fit(X_train,Qt)
r.score(X_test,Q)

s="Pred/fit_final.pickle"
fid = open(s, 'wb') 
pickle.dump(r,fid)
fid.close()

mean,std=clas.transfo
transformation = csv.writer(open("Pred/transformation.csv","wb"))
transformation.writerow(mean)
transformation.writerow(std)

indexation = csv.writer(open("Pred/indexation.csv","wb"))
indexation.writerow(list_index)
indexation.writerow(list_index2)



clf=r
print(sum(map(abs,clf.predict(X_test)+Q2-y_test))/len(X_test))
v=(clf.predict(X_test)+Q2-y_test)/y_test
v=map(abs,v)
print sum(v)/len(X_test)



print(sum(map(abs,0.5*(clf.predict(X_test)+Q2+clas.ada_reg.predict(X_test))-y_test))/len(X_test))
v=(0.5*(clf.predict(X_test)+Q2+clas.ada_reg.predict(X_test))-y_test)/y_test
v=map(abs,v)
print sum(v)/len(X_test)







##############################
weights=clas.ada_reg.feature_importances_

obj=pd.read_csv(clas.database)

names0=obj.columns
names=[]
for i in range(len(names0)):
    names.append(names0[i])
names.append("ecart")


index=np.argsort(weights)
p=10
for i in range(p):
    print names[index[len(index)-1-i]] ###caracteristiques les plus importantes
    


###########################################"
pred=clf#test.forest_reg ##choix du predicteur

###### visuaalisation des erreurs
ecart_pred=v#(pred.predict(X_test)-y_test)/y_test #erreur en %

mean,std=clas.transfo
X=std*X_test+mean
M=np.zeros((len(y_test),len(X_test[0,:])+2))
for i in range(len(M)):
    for j in range(len(X_test[0,:])):
        M[i,j]=X[i,j]
    M[i,len(X_test[0,:])]=y_test[i]
    M[i,-1]=abs(ecart_pred[i])
    
M=M.tolist()
M.append(names)
M=M[::-1]

writer = csv.writer(open('errors.csv', 'wb'))
for values in M:
    writer.writerow(values)

###csv filtré######################
#X,y=clas.X,clas.label
#
#M=np.zeros((len(X),len(X[0,:])+1))
#for i in range(len(M)):
#    for j in range(len(X[0,:])):
#        M[i,j]=X[i,j]
#    M[i,len(X[0,:])]=y[i]
#   
#    
#M=M.tolist()
#M.append(names)
#M=M[::-1]
#
#writer = csv.writer(open('base_filtre.csv', 'wb'))
#for values in M:
#    writer.writerow(values)


###########################

#X=X_train
#
#Z0=np.zeros((len(X),7))
#Z0[:,0]=X[:,index_surface]
#Z0[:,1]=X[:,index_piece]
#Z0[:,2]=X[:,index_x]
#Z0[:,3]=X[:,index_y]
#Z0[:,4]=X[:,index_etage]
#Z0[:,5]=X[:,index_ch]
#Z0[:,-1]=X[:,index_adt]
#
#
#X=X_test
#
#Z1=np.zeros((len(X),7))
#Z1[:,0]=X[:,index_surface]
#Z1[:,1]=X[:,index_piece]
#Z1[:,2]=X[:,index_x]
#Z1[:,3]=X[:,index_y]
#Z1[:,4]=X[:,index_etage]
#Z1[:,5]=X[:,index_ch]
#Z1[:,-1]=X[:,index_adt]
#
#
#
#clf=RandomForestRegressor()
#clf.fit(X_train,y_train)
#Z0=clf.transform(X_train,threshold="0.3*mean")
#Z1=clf.transform(X_test,threshold="0.3*mean")
#
#
#n=1
#cluster=KMeans(n_clusters=n, init='k-means++', n_init=200, max_iter=400, 
#               tol=0.0001, precompute_distances='auto', verbose=0, random_state=None, copy_x=True, n_jobs=-1)
#cluster.fit(Z0)
#Z=cluster.predict(Z0)
#Z_test=cluster.predict(Z1)
#
#
#vec0=np.zeros(len(np.unique(Z_test)))
#vec1=np.zeros(len(np.unique(Z_test)))
#for p in (np.unique(Z_test)):
#    
#    X1,y1,x,y=X_train[Z==p],y_train[Z==p],X_test[Z_test==p],y_test[Z_test==p]
#    
#    c=AdaBoostRegressor(RandomForestRegressor())
#    o=c.fit(X1,y1)
#    print ("cluster")
#    print p
#    print ("echantillon")
#    print X1.shape,x.shape
#    print ("score du cluster")
#    print c.score(x,y)
#    print ("ecart du cluster")
#    print(sum(map(abs,c.predict(x)-y))/len(x))
#    v=(c.predict(x)-y)/y
#    v=map(abs,v)
#    print sum(v)/len(x)
#    print 
#    vec0[p]=c.score(x,y)*len(X1)
#    vec1[p]=sum(v)/len(x)*len(X1)
#print sum(vec0)/len(y_train),sum(vec1)/len(y_train)
############################

#clf=AdaBoostRegressor(RandomForestRegressor())
#clf.fit(X_train,y_train)
#clf.score(X_test,y_test)



