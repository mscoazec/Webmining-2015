# -*- coding: utf-8 -*-
"""
Created on Mon Oct 12 09:45:45 2015

@author: hlevy
"""

"""
Fichier réalisant l'extraction de données à partir de textes d'annonces immobilières
Entrée : fichier Json
Sortie : tableau de caractéristiques rempli
"""


"""
Imports
"""
import csv
import numpy as np
import json
import re
import time
import os

"""
Déclaration de variables générales
"""
#le fichier contenant la liste des features
fichier_features = "Liste_features.csv"

#la colonne de la première chaîne de caractère à chercher
column_chains = 3

#le nombre maximal de chaînes de caractères entraînant l'activation d'une feature
number_chains = 4

#la colonne du nom de la feature dans le tableau
column_featureName = 0

#la colonne yes/no
column_yesNo = 2



"""
Importation des features depuis le fichier csv
Attention à ce fichier csv : les colonnes des chaînes de caractère sont à manier avec précaution
    Elles ne doivent pas contenir de caractère majuscule
    Pour les features numériques, il faut que le groupe ([0-9,.]) doit être le premier groupe,
    cela signifie que les accents/non accents ne peuvent être gérés par des groups qu'après le
    groupe qui contient la valeur numérique.
"""
cr = csv.reader(open(fichier_features,"rb"))


"""
Le tableau qui contiendra les informations importantes sur les features :
featureName | yesNo | wording1 | wording2 | wording3 | ...
Le tableau est sous forme de liste car il contient des string et un booléen
"""
tab_features = []



"""
On crée aussi une liste des features qui nous servira à renseigner les en-tête des fichiers
de données sur les annonces. On y met aussi le prix
"""
feature_and_price_list = []








"""
Remplissage du tableau et de la liste en parcourant le fichier contenant les features
Pour les chaînes de caractère à rechercher : pour les features numériques, il faut
impérativement que le premier groupe entre parenthèses soit celui du nombre à chercher.
Si vous souhaitez utiliser des variantes d'expression régulières avec des parenthèses,
vous ne pouvez le faire qu'après le groupe contenant la valeur numérique à chercher.
"""
#Ouverture du reader du fichier csv
cr = csv.reader(open(fichier_features,"rb"))

#Parcours du tableau
number_features = -1
for row in cr:
    #On ne prend pas en compte la première ligne
    if number_features > -1:
        #On détermine la liste à renseigner : cela dépend entre autres du nombre de chaînes de caractère
        current_row = []
        
        #featureName
        current_row.append(row[column_featureName])
        
        
        #Yes / No (booléen)
        current_row.append(row[column_yesNo] == "x")
        
        #les chaînes de caractère à rechercher (on ne prend pas les dernières cases vides)
        for i in range(number_chains):
            if row[column_chains + i] != '':
                current_row.append(row[column_chains + i])
        
        #On ajoute la ligne à notre tableau de features
        tab_features.append(current_row)
        
        
        #On rajoute la feature dans notre liste de features
        feature_and_price_list.append(row[column_featureName])
        
        
    number_features += 1


#On ajoute le prix en toute dernière colonne
feature_and_price_list.append("prix")













"""
Ecriture d'un dictionnaire donnant la position de chaque feature dans le tableau
On verra plus tard si on l'utilise ou pas.
Pour l'instant on ne l'utilise pas.


dico_features = {}

#Remplissage du dictionnaire
for i in range(number_features):
    dico_features[tab_features[i][0]] = i
"""











"""
La fonction extraction_features qui ressort un dictionnaire
C'est une ancienne version de la fonction, qui sert à sortir non pas un .csv mais un .json

def extraction_features(texte):
    
    #texte est un texte d'annonce. Ce doit être un string.
    #Cette fonction ressort un dictionnaire feature:valeur
    
    #La sortie : le dictionnaire de features
    featdict = {}
    
    #On parcourt l'ensemble des features
    for feat_num in range(number_features):
        
        #On parcourt l'ensemble des chaînes de caractère à chercher pour la feature courante
        for chain_num in range(2, len(tab_features[feat_num])):
            
            #La recherche de la chaîne de caractères courante
            value_feat = re.search(tab_features[feat_num][chain_num], texte)
            
            #On ne renseigne pas les features numériques si on n'a pas trouvé l'information
            if value_feat != None:
                if tab_features[feat_num][1]:
                    featdict[tab_features[feat_num][0]] = True
                else:
                    featdict[tab_features[feat_num][0]] = value_feat.group(1)
    
    print featdict
"""





"""
Dictionnaire de nombres
"""
num_dict = {"un":"1", "deux" : "2", "trois" : "3", "quatre" : "4", "cinq" : "5", "six" : "6",
           "sept" : "7", "huit" : "8", "neuf" : "9", "dix" : "10", "onze" : "11",
           "douze" : "12", "treize" : "13", "quatorze" : "14", "quinze" : "15", "seize" : "16"}





#Extraction des caractéristiques d'un bien à partir d'un texte
def extraction_features(texte):
    """
    texte est un texte d'annonce. Ce doit être un string.
    Cette fonction ressort un tableau des valeurs des features
    """
    #La sortie : le tableau de valeurs de chacune des features
    feat_values = []
    
    #On parcourt l'ensemble des features
    for feat_num in range(number_features):
        
        #On commence avec None
        value_feat = None
        
        #On parcourt l'ensemble des chaînes de caractère à chercher pour la feature courante
        for chain_num in range(2, len(tab_features[feat_num])):
            
            #La recherche de la chaîne de caractères courante
            value_feat_chain = re.search(tab_features[feat_num][chain_num], texte)
            
            #On met à jour la recherche si on a trouvé quelque chose
            if value_feat_chain != None:
                value_feat = value_feat_chain
            
        #feature yesNo
        if tab_features[feat_num][1]:
            if value_feat != None:
                feat_values.append(1)
            else:
                feat_values.append(0)
        
        #feature numérique
        else:
            if value_feat != None:
                #Valeur à ajouter dans la liste
                value_to_add = value_feat.group(1)
                
                #Gestion des nombres écrits en lettres
                if value_to_add in num_dict:
                    value_to_add = num_dict[value_to_add]
                
                #Version valeur entière
                feat_values.append(int(float(value_to_add.replace(",", "."))))
                
                #Version valeur initiale (avec des virgules)
                #feat_values.append(value_feat.group(1))
            else:
                feat_values.append(0)
    
    #La sortie : le tableau de valeurs des features
    return feat_values









#Extraction de toutes les caractéristiques d'une annonce complète (comprenant URL, titre, description, prix ...)
def traitement_annonce(annonce):
    """
    annonce est un tableau de string, contenant obligatoirement l'URL, et possiblement d'autres
    champs : texte de l'annonce, prix, récapitulatif des caractéristiques ... Cela dépend du site
    """
    
    """
    Extraction du site d'annonce à partir de l'URL
    """
    url_string = annonce["url"]
    site_annonce = ""
    
    #Les différents sites
    if re.search("seloger", url_string):
        site_annonce = "seloger"
    
    
    #La sortie : un tableau de string
    feat_values_description = []
    
    """
    L'algorithme de traitement de l'annonce dépend du site duquel l'annonce a été extraite.
    Chaque site aura des champs qui lui sont propres
    """
    
    #seloger
    if site_annonce == "seloger":
        #Champs : "titre", "infos", "description", "prix"
        
        
        """
        Version trois champs séparés
        #On récupère les informations contenues dans le titre et dans la description
        feat_values_title = extraction_features(annonce["titre"])
        feat_values_infos = extraction_features(annonce["infos"])
        feat_values_description = extraction_features(annonce["description"])
        
        #Les informations dans le titre priment sur celles contenues dans les infos qui priment sur cells
        #contenues dans la description en cas de redondance.
        #Mais il y a plus d'informations dans la description donc on part des valeurs tirées de la description       
        for i in range(len(feat_values_description)):
            #Recopie des valeurs contenues dans infos
            if feat_values_infos[i] != 0:
                feat_values_description[i] = feat_values_infos[i]
            
            #Recopie des valeurs contenues dans titre
            if feat_values_title[i] != 0:
                feat_values_description[i] = feat_values_title[i]
        """



        """
        Version un seul champ concaténé
        """
        #On récupère les informations contenues dans le titre et dans la description
        feat_values_description = extraction_features(annonce["titre"] + annonce["infos"] + annonce["description"])
        


        #On rajoute le prix à la main
        feat_values_description.append(annonce["prix"])
    
    
    
    #La sortie : le tableau de features avec le prix au bout
    return feat_values_description











#Extraction de toutes les annonces d'un fichier json résultant du crawling, et écriture dans un fichier csv
#des features pour chacune des annonces
def traitement_fichier(fichierJson, fichier_sortie = None):
    """
    fichierJson est le nom d'un fichier Json contenant des annonces extraites d'un site Web :
    Il doit se terminer par .json
    fichier_sortie est un csv.writer donnant le fichier dans lequel renseigner les caractéristiques.
    
    Si on ne donne pas de fichier_sortie, la fonction traitement_fichier
    crée un fichier csv du nom fichierJson_traite.csv, contenant les valeurs
    des features (et le prix) pour chaque annonce, avec une ligne par annonce
    """
    
    
    #Si on n'a pas donné de fichier de sortie dans les paramètres, on en crée un
    #Création du fichier csv qui contiendra les données
    #On remplace l'extension en .json par _traite.csv
    if fichier_sortie == None:
        fichier_sortie = csv.writer(open(fichierJson.replace(".json","") + "_traite.csv", "wb"))
    
        #On peut déjà renseigner les en-tête : les noms de features
        fichier_sortie.writerow(feature_and_price_list)
    
    #Import du fichier Json des annonces
    annoncesJson = json.load(open(fichierJson))
    
    #Nombre d'annonces à traiter
    nombre_annonces = len(annoncesJson)    
    
    #Suivi du traitement sur la console
    print "Fichier "+ fichierJson + " : traitement de %s annonces..." %nombre_annonces
    
    #Calcul du temps de traitement des annonces
    temps_debut = time.clock()
    
    #On traite chacune des annonces une par une
    for i in range(nombre_annonces):
        fichier_sortie.writerow(traitement_annonce(annoncesJson[i]))
        
        #Affichage du nombre d'annonces toutes les 100 annonces pour suivre l'avancement
        if (i>0 and (i%100) == 0):
            print "%s/%s" %(i, nombre_annonces)
    
    
    #Calcul du temps de traitement des annonces
    temps_fin = time.clock()
    temps_total = temps_fin - temps_debut + 0.0
    annonces_par_seconde = (nombre_annonces + 0.0)/temps_total
    

    #Impression du temps de traitement
    print "%s annonces traitées en %1.1f secondes, soit %1.1f annonces/seconde." %(nombre_annonces, temps_total, annonces_par_seconde)










#Extraction de toutes les annonces de tous les fichiers d'un dossier contenant des fichiers Json
def traitement_dossier(dossierFichiers):
    """
    dossierFichiers est le chemin d'un dossier contenant des .json d'annonces
    La fonction traitement_dossier crée un fichier csv concaténant toutes les caractéristiques
    de toutes les annonces de tous les fichiers du dossier. Ce fichier csv est placé à côté du dossier
    (et pas dans le dossier).
    """
    
    #Calcul du temps total du programme
    temps_debut = time.clock()
    
    
    #Le fichier de sortie dans lequel on écrira les données
    fichier_sortie = csv.writer(open(dossierFichiers + "_traite.csv", "wb"))
    
    #On renseigne les en-tête : les noms de features
    fichier_sortie.writerow(feature_and_price_list)    
    
    #Suivi du traitement sur la console
    print "Traitement du dossier " + dossierFichiers
    
    #On parcourt tous les fichiers du dossier
    for fichierJson in os.listdir(dossierFichiers):
        if fichierJson[-5:] == ".json":
            #On traite chaque fichier un par un en écrivant les données dans fichier_sortie
            traitement_fichier(dossierFichiers + "/" + fichierJson, fichier_sortie)
    
    
    #Calcul du temps total du programme
    temps_fin = time.clock()
    temps_total = temps_fin - temps_debut
    

    #Impression du temps de traitement
    print "Temps total du programme : %d secondes." %(temps_total)

    
    












"""
Commandes de tests
"""
#Test de la fonction extraction_features
#texte_test = "Au 3eme etage avec ascenseur d'un bel immeuble pierre de taille, appartement 5/6 pieces d'une surface de 213 m2 comprenant une entree, un sejour de 80 m2, 3 grandes chambres, possibilite 4 chambres, une tres grande cuisine dinatoire, 1 salle de bains avec WC, une salle d'eau (buanderie), un WC independant. Parquet au sol. Appartement tres lumineux, double exposition (Nord/Est et Sud/Ouest. Possibilite de le diviser. Emplacement de parking dans la cour. Gardienne digicode et interphone. 1 575 000 E. Contact: Laurence de Villeneuve. RESUME DES CARACTERISTIQUES : Surface de 213 m2, 6 Etages, 3 Etage, 5 Pieces, 4 Chambres, 1 Salle de bains, 1 Salle d'eau, 2 Toilettes, Toilettes Separees, Parquet, Television Par Cable, Ascenseur, 1 Parking, Situation : ville, Chauffage gaz, Cuisine americaine equipee, Interphone, Digicode, Gardien, Entree, 35 m2 Salle a manger, Salle de sejour : 85 m2, Orientation Est, Nord, Ouest..."
#texte_test = ""
#extraction_features(texte_test.lower())


#Test de la fonction traitement_fichier
#traitement_fichier('items_seLoger-10-12.json')


#Test de la fonction traitement_dossier
traitement_dossier('Fichiers_Json')

