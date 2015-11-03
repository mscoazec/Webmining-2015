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
import json
import re
import time
import os
import math
import unicodedata
import numpy as np

class Text_analysis:
    
    def __init__(self):
        """
        Déclaration de variables générales
        """
        #le fichier contenant la liste des features
        self.fichier_features = "Liste_features.csv"
        
        #la colonne de la première chaîne de caractère à chercher
        self.column_chains = 4
        
        #le nombre maximal de chaînes de caractères entraînant l'activation d'une feature
        self.number_chains = 6
        
        #la colonne du nom de la feature dans le tableau
        self.column_featureName = 0
        
        #la colonne yes/no
        self.column_yesNo = 2
        
        #la colonne négation
        self.column_negation = 3
        
        
        
        #le dossier où mettre les output (les fichiers .csv contenant les données d'apprentissage)
        self.dossier_output = "Output"
        
        
        
        #le fichier contenant les coordonnées des arrondissements et des stations de métro
        #Les coordonnées sont en décimales et non pas en degrés minutes secondes, et je les ai multipliées
        #par dix mille (10 000) pour avoir directement des entiers
        #les donées ont été tirées d'openstreetmap pour les stations de métro, et de wikipédia pour les arrondissements
        self.fichier_coordonnees = "Coordonnees.csv"
        
        #la colonne du nom de la location dans le tableau
        self.column_locationName = 0
        
        #la colonne de la coordonnee x
        self.column_xCoordonnee = 1
        
        #la colonne de la coordonnee y
        self.column_yCoordonnee = 2
        
        #la ligne de la première ligne d'arrondissements (la ligne de l'excel moins un)
        self.line_ardt = 1
        
        #la ligne de la première ligne de métro (la ligne de l'excel moins un)
        self.line_metro = 21

        #la ligne du premier autre lieu qu'un métro (la ligne de l'excel moins un)
        self.line_other_locations = 408
        
        """
        Importation des features depuis le fichier csv
        Attention à ce fichier csv : les colonnes des chaînes de caractère sont à manier avec précaution
            Elles ne doivent pas contenir de caractère majuscule
            Pour les features numériques, il faut que le groupe ([0-9,.]) doit être le premier groupe,
            cela signifie que les accents/non accents ne peuvent être gérés par des groups qu'après le
            groupe qui contient la valeur numérique.
        Attention aussi aux features négatives
            Les features négatives sont présentes dans Liste_features.csv
            Elles sont importées dans tab_features mais PAS dans feature_and_price_list
            Elles ne sont donc pas recopiées dans le fichier de sortie
            Faire attention aux références : une feature négative fait référence à une feature positive
            Si vous insérez une ligne dans le fichier, vérifier que ces correspondances sont toujours correctes
        """
        self.cr = csv.reader(open(self.fichier_features,"rb"))
        
        
        """
        Le tableau qui contiendra les informations importantes sur les features :
        featureName | yesNo | wording1 | wording2 | wording3 | ...
        Le tableau est sous forme de liste car il contient des string et un booléen
        """
        self.tab_features = []
        
        
        
        """
        On crée aussi une liste des features qui nous servira à renseigner les en-tête des fichiers
        de données sur les annonces. On y met aussi le prix
        """
        self.feature_and_price_list = []
        
        
        
        
        
        #Suivi du nombre de metros trouves avec mon algorithme (site pap)
        self.nombre_metros_trouves = 0
        
        #Suivi du nombre de lieux trouves avec mon algorithme
        self.nombre_lieux_trouves = 0
        
        #Suivi du nombre d'annonces comportant un lieu trouve par l'algorithme
        self.nombre_annonces_avec_lieu = 0
        
        
        """
        Remplissage du tableau et de la liste en parcourant le fichier contenant les features
        Pour les chaînes de caractère à rechercher : pour les features numériques, il faut
        impérativement que le premier groupe entre parenthèses soit celui du nombre à chercher.
        Si vous souhaitez utiliser des variantes d'expression régulières avec des parenthèses,
        vous ne pouvez le faire qu'après le groupe contenant la valeur numérique à chercher.
        """
        
        """
        On en profite pour récupérer la position des features coordonnees x et y, de
        coordonnees_precises et de l'arrondissement dans la liste des features
        """
        self.pos_xCoordinate = 0
        self.pos_yCoordinate = 0
        self.pos_ardt = 0
        self.pos_coor_precises = 0
        
        
        #Parcours du tableau
        self.number_features = -1
        for row in self.cr:
            #On ne prend pas en compte la première ligne
            if self.number_features > -1:
                #On détermine la liste à renseigner : cela dépend entre autres du nombre de chaînes de caractère
                current_row = []
                
                #featureName
                current_row.append(row[self.column_featureName])
                
                
                #Yes / No (booléen)
                current_row.append(row[self.column_yesNo] == "x")
                
                #Négation de la feature n°...
                current_row.append(row[self.column_negation])
                
                #les chaînes de caractère à rechercher (on ne prend pas les dernières cases vides)
                for i in range(self.number_chains):
                    if row[self.column_chains + i] != '':
                        current_row.append(row[self.column_chains + i])
                
                #On ajoute la ligne à notre tableau de features
                self.tab_features.append(current_row)
                
                
                #On rajoute la feature dans notre liste de features
                #Mais uniquement si ce n'est pas une feature négative
                if row[self.column_negation] == "":
                    self.feature_and_price_list.append(row[self.column_featureName])
                
                #Si c'est la ligne de la coordonne x, on renseigne la position des features x et y
                if row[self.column_featureName] == "coordonnee_x_q":
                    self.pos_xCoordinate = self.number_features
                    self.pos_yCoordinate = self.number_features + 1
                
                #Si c'est la ligne de l'arrondissement, on renseigne la position de la feature ardt
                if row[self.column_featureName] == "arrondissement_q":
                    self.pos_ardt = self.number_features
                    
                #Si c'est la ligne de coordonnees_precises, on renseigne la position de la feature ardt
                if row[self.column_featureName] == "coordonnees_precises":
                    self.pos_coor_precises = self.number_features
                
                
            self.number_features += 1
        
        
        #On ajoute l'url, la description, et le prix en toute dernière colonne
        self.feature_and_price_list.append("prix")
        self.feature_and_price_list.append("url")
        self.feature_and_price_list.append("titre")
        self.feature_and_price_list.append("description")
        
        
        
        
        
        
        
        
        
        
        
        
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
        self.num_dict = {"un":"1", "deux" : "2", "trois" : "3", "quatre" : "4", "cinq" : "5", "six" : "6",
                   "sept" : "7", "huit" : "8", "neuf" : "9", "dix" : "10", "onze" : "11",
                   "douze" : "12", "treize" : "13", "quatorze" : "14", "quinze" : "15", "seize" : "16"}
        
        
        
        
        
        
        
        #Dictionnaires qui vont contenir les coordonnées
        #Arrondissements
        self.dict_xCoordonnees_ardt = {}
        self.dict_yCoordonnees_ardt = {}
        
        #Métros
        self.dict_xCoordonnees_metros = {}
        self.dict_yCoordonnees_metros = {}
        
        #Lieux
        self.dict_xCoordonnees_lieux = {}
        self.dict_yCoordonnees_lieux = {}
        
        
        """
        Importation des coordonnées depuis le fichier csv
        """
        self.cr_coor = csv.reader(open(self.fichier_coordonnees,"rb"))
        
        #Parcours du tableau
        self.number_locations = -1
        for row in self.cr_coor:
            #On ne prend pas en compte la première ligne
            if self.number_locations > -1:
                
                if self.number_locations < self.line_metro - 1:                    
                    #On renseigne la coordonnee en x et en y, en entier et pas en string
                    self.dict_xCoordonnees_ardt[self.number_locations + 1] = int(row[self.column_xCoordonnee])
                    self.dict_yCoordonnees_ardt[self.number_locations + 1] = int(row[self.column_yCoordonnee])
                
                else:
                    #Détermination du nom à rentrer : on met les noms en minuscules et en unicode
                    cur_locationName = unicode(row[self.column_locationName].lower(), 'utf-8')
                    
                    #Puis on enlève les accents des noms
                    cur_locationName = unicodedata.normalize('NFKD', cur_locationName).encode('ascii','ignore')
                    
                    
                    
                    
                    #Pour les métros :
                    #On let met dans le dico des lieux avec le mot métro devant.
                    #On let met dans le dico des métros avec juste le nom du métro
                    if self.number_locations < self.line_other_locations - 1:
                        #On renseigne la coordonnee en x et en y, en entier et pas en string
                        #On rajoute le mot 'metro' pour qu'il ne prenne en compte que les métros
                        #Car certains métros comme Commerce se retrouvent dans un texte sans être un métro
                        self.dict_xCoordonnees_lieux['metro ' + cur_locationName] = int(row[self.column_xCoordonnee])
                        self.dict_yCoordonnees_lieux['metro ' + cur_locationName] = int(row[self.column_yCoordonnee])
                        
                        #Pour le dico des métros, on met juste le nom du métro
                        self.dict_xCoordonnees_metros[cur_locationName] = int(row[self.column_xCoordonnee])
                        self.dict_yCoordonnees_metros[cur_locationName] = int(row[self.column_yCoordonnee])
                        
                    #Pour les autres lieux (les rues), on les met tels quels dans le dico des lieux
                    else:
                        self.dict_xCoordonnees_lieux[cur_locationName] = int(row[self.column_xCoordonnee])
                        self.dict_yCoordonnees_lieux[cur_locationName] = int(row[self.column_yCoordonnee])
                    
            
            self.number_locations += 1
        
        
        
        
        
        
    
        
        
        
        
        
    
    #Extraction des caractéristiques d'un bien à partir d'un texte
    def extraction_features(self, texte, rechercher_lieux = False, fonction_test = False):
        """
        texte est un texte d'annonce. Ce doit être un string.
        Cette fonction ressort un tableau des valeurs des features
        Par défaut on ne cherche pas les lieux de la liste des coordonnees car cela prend du temps
        On ne le fera que sur les champs description (on précisera True pour ces recherches quand on appellera cette
        fonction extraction_features)
        """
        #La sortie : le tableau de valeurs de chacune des features
        feat_values = []
        
        
        
        
        """
        Recherche de features
        """
        #On parcourt l'ensemble des features
        for feat_num in range(self.number_features):
            
            #On commence avec None
            value_feat = None
            
            #On parcourt l'ensemble des chaînes de caractère à chercher pour la feature courante
            for chain_num in range(3, len(self.tab_features[feat_num])):
                
                #La recherche de la chaîne de caractères courante
                value_feat_chain = re.search(self.tab_features[feat_num][chain_num], texte)
                
                #On met à jour la recherche si on a trouvé quelque chose
                if value_feat_chain != None:
                    value_feat = value_feat_chain
                
            #feature yesNo
            if self.tab_features[feat_num][1]:
                if value_feat != None:
                    feat_values.append(1)
                else:
                    feat_values.append("")
            
            #feature numérique
            else:
                if value_feat != None:
                    #Valeur à ajouter dans la liste
                    value_to_add = value_feat.group(1)
                    
                    #Gestion des nombres écrits en lettres
                    if value_to_add in self.num_dict:
                        value_to_add = self.num_dict[value_to_add]
                    
                    #Version valeur entière
                    feat_values.append(int(float(value_to_add.replace(",", "."))))
                    
                    #Version valeur initiale (avec des virgules)
                    #feat_values.append(value_feat.group(1))
                else:
                    feat_values.append("")
        
        
        """
        Recherche de coordonnées : uniquement si l'on a mis rechercher_lieux à vrai
        """
        if rechercher_lieux:
            
            
            for lieu in self.dict_xCoordonnees_lieux:
                #On cherche le nom du lieu dans le texte
                metro_found = re.search(lieu, texte)
                
                #Si on trouve le lieu, on rajoute ses coordonnees dans la liste des coordonnees trouvees pour l'appartement
                if metro_found != None:
                    #Si c'est le premier lieu trouve, il faut remplacer le "" par un []
                    if feat_values[self.pos_xCoordinate] == "":
                        feat_values[self.pos_xCoordinate] = []
                        feat_values[self.pos_yCoordinate] = []
                    
                    
                    
                    #On ajoute les valeurs des coordonnees du lieu trouvé
                    feat_values[self.pos_xCoordinate].append(self.dict_xCoordonnees_lieux[lieu])
                    feat_values[self.pos_yCoordinate].append(self.dict_yCoordonnees_lieux[lieu])
                    
                    
                    #Affichage d'un lieu trouve : ligne non prise en compte quand on lance l'analyse de tous les textes
                    if fonction_test:
                        print "Lieu trouve : " + lieu + " (%d, %d)." %(self.dict_xCoordonnees_lieux[lieu], self.dict_yCoordonnees_lieux[lieu])
                    
                    #Suivi du nombre de lieux trouves avec mon algorithme
                    self.nombre_lieux_trouves += 1
                    
            #Un peu d'affichage quand on fait des tests
            if fonction_test:
                print ""
            
            """
            Une fois une liste de coordonnes trouvees, on prend la moyenne des coordonnes trouvees
            Si on n'a rien trouvé, on laisse ""
            """
            if feat_values[self.pos_xCoordinate] != "":
                feat_values[self.pos_xCoordinate] = int(np.mean(feat_values[self.pos_xCoordinate]))
                feat_values[self.pos_yCoordinate] = int(np.mean(feat_values[self.pos_yCoordinate]))
        
        
        #La sortie : le tableau de valeurs des features
        return feat_values
    
    
    
    
    
    
    
    
    
    #Extraction de toutes les caractéristiques d'une annonce complète (comprenant URL, titre, description, prix ...)
    def traitement_annonce(self, annonce, fonction_test = False):
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
        else:
            if re.search("explorimmo", url_string):
                site_annonce = "explorimmo"
            else:
                if re.search("fnaim", url_string):
                    site_annonce = "fnaim"
                else:
                    if re.search("laforet", url_string):
                        site_annonce = "laforet"
                    else:
                        if re.search("www.pap.fr", url_string):
                            site_annonce = "pap"
                        else:
                            if re.search("paruvendu", url_string):
                                site_annonce = "paruvendu"
                            else:
                                #Cas où on récupère les données rentrées par l'utilisateur sur notre site internet
                                if re.search("notresite", url_string):
                                    site_annonce = "notresite"
        
        
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
            Version description séparée
            """
            #On récupère les informations contenues dans le titre, dans les infos, et dans la description
            #Dans description on cherche des mentions de lieux, et on affiche si on est en test
            #On rajoute le nom du site à la main pour les features de site web
            feat_values_infos = self.extraction_features(annonce["titre"] + annonce["infos"]  + "site "+site_annonce)
            feat_values_description = self.extraction_features(annonce["description"], True, fonction_test)
            
            #Les informations dans le titre et dans les infos priment sur celles
            #contenues dans la description en cas de redondance.
            #titre & infos > description
            #Mais il y a plus d'informations dans la description donc on part des valeurs tirées de la description       
            for i in range(len(feat_values_description)):
                #Recopie des valeurs contenues dans infos et titre
                if feat_values_infos[i] != '':
                    feat_values_description[i] = feat_values_infos[i]
            
            
            
            """
            Version un seul champ concaténé
            #On récupère les informations contenues dans le titre, dans la description, et dans infos
            feat_values_description = self.extraction_features(annonce["titre"] + annonce["infos"] + annonce["description"])
            """
            
            #On rajoute le prix à la main (la fonction float("") bug si la chaîne est vide)
            if annonce["prix"] != "":
                feat_values_description.append(int(float(annonce["prix"].replace(",", ".").replace("HC","").replace("CC",""))))
        
        
        
        
        
        
        
        #explorimmo
        if site_annonce == "explorimmo":
            #Champs : "titre", "infos", "description", "prix", "localisation"
            
            """
            Version description séparée
            """
            #On récupère les informations contenues dans le titre, dans les infos, dans la localisation, et dans la description
            #Dans description on cherche des mentions de lieux
            #On rajoute le nom du site à la main pour les features de site web
            feat_values_infos = self.extraction_features(annonce["titre"] + annonce["infos"] + annonce["localisation"] + "site "+site_annonce)
            feat_values_description = self.extraction_features(annonce["description"], True, fonction_test)
            
            #Les informations dans le titre, dans les infos et dans localisation priment sur celles
            #contenues dans la description en cas de redondance.
            #titre & localisation & infos > description
            #Mais il y a plus d'informations dans la description donc on part des valeurs tirées de la description       
            for i in range(len(feat_values_description)):
                #Recopie des valeurs contenues dans infos et titre et localisation
                if feat_values_infos[i] != '':
                    feat_values_description[i] = feat_values_infos[i]
            
            
            
            """
            Version un seul champ concaténé
            #On récupère les informations contenues dans le titre, dans la description, dans infos, et dans la localisation
            feat_values_description = self.extraction_features(annonce["titre"] + annonce["infos"] + annonce["description"] + annonce["localisation"])
            """
            
            
            #On rajoute le prix à la main (la fonction float("") bug si la chaîne est vide)
            if annonce["prix"] != "":
                feat_values_description.append(int(float(annonce["prix"].replace(",", ".").replace("HC","").replace("CC",""))))
        
        
        
        
        
        
        
        #fnaim
        #Attention il y a des espaces dans les prix
        if site_annonce == "fnaim":
            #Champs : "titre", "infos", "description", "prix", "localisation"
            
            """
            Version description séparée
            """
            #On récupère les informations contenues dans le titre, dans les infos, dans la localisation, et dans la description
            #Dans description on cherche des mentions de lieux
            #On rajoute le nom du site à la main pour les features de site web
            feat_values_infos = self.extraction_features(annonce["titre"] + annonce["infos"] + annonce["localisation"] + "site "+site_annonce)
            feat_values_description = self.extraction_features(annonce["description"], True, fonction_test)
            
            #Les informations dans le titre, dans les infos, et dans la localisation priment sur celles
            #contenues dans la description en cas de redondance.
            #titre & localisation & infos > description
            #Mais il y a plus d'informations dans la description donc on part des valeurs tirées de la description       
            for i in range(len(feat_values_description)):
                #Recopie des valeurs contenues dans infos et titre et localisation
                if feat_values_infos[i] != '':
                    feat_values_description[i] = feat_values_infos[i]
            
            
            
            """
            Version un seul champ concaténé
            #On récupère les informations contenues dans le titre, dans la description, dans infos, et dans la localisation
            feat_values_description = self.extraction_features(annonce["titre"] + annonce["infos"] + annonce["description"] + annonce["localisation"])
            """
            
            
            #On rajoute le prix à la main (la fonction float("") bug si la chaîne est vide)
            #Il y a des espaces qu'il faut enlever
            if annonce["prix"] != "":
                feat_values_description.append(int(float(annonce["prix"].replace(",", ".").replace(" ","").replace("HC","").replace("CC",""))))
        
        
        
        
        
        
        #laforet
        #Attention il y a des espaces dans les prix
        if site_annonce == "laforet":
            #Champs : "titre", "infos", "description", "prix"
            
            """
            Version description séparée
            """
            #On récupère les informations contenues dans le titre, dans les infos, et dans la description
            #Dans description on cherche des mentions de lieux
            #On rajoute le nom du site à la main pour les features de site web
            feat_values_infos = self.extraction_features(annonce["titre"] + annonce["infos"] + "site "+site_annonce)
            feat_values_description = self.extraction_features(annonce["description"], True, fonction_test)
            
            #Les informations dans le titre, et dans les infos priment sur celles
            #contenues dans la description en cas de redondance.
            #titre & infos > description
            #Mais il y a plus d'informations dans la description donc on part des valeurs tirées de la description       
            for i in range(len(feat_values_description)):
                #Recopie des valeurs contenues dans infos et titre
                if feat_values_infos[i] != '':
                    feat_values_description[i] = feat_values_infos[i]
            
            
            
            """
            Version un seul champ concaténé
            #On récupère les informations contenues dans le titre, dans la description, et dans infos
            feat_values_description = self.extraction_features(annonce["titre"] + annonce["infos"] + annonce["description"])
            """
            
            #On rajoute le prix à la main (la fonction float("") bug si la chaîne est vide)
            #Il y a des espaces qu'il faut enlever
            if annonce["prix"] != "":
                feat_values_description.append(int(float(annonce["prix"].replace(",", ".").replace(" ","").replace("HC","").replace("CC",""))))
        
        
        
        
        
        
        #pap
        #Attention les prix sont avec des . séparant les millions des milliers des euros
        #4.800.000 pour 4 millions et huit cent mille euros
        #Traitement spécial pour les métros sur ces annonces
        if site_annonce == "pap":
            #Champs : "titre", "infos", "description", "prix", "localisation", "metro"
            
            """
            Version description séparée
            """
            #On récupère les informations contenues dans le titre, dans les infos, et dans la description
            #On ne cherche pas la mention de lieux dans description car on a déjà les métros dans le champ métro
            #On rajoute le nom du site à la main pour les features de site web
            feat_values_infos = self.extraction_features(annonce["titre"] + annonce["infos"] + annonce["localisation"] + "site "+site_annonce)
            feat_values_description = self.extraction_features(annonce["description"])
            
            #Les informations dans le titre, dans les infos, et dans la localisation priment sur celles
            #contenues dans la description en cas de redondance.
            #titre & infos & localisation > description
            #Mais il y a plus d'informations dans la description donc on part des valeurs tirées de la description       
            for i in range(len(feat_values_description)):
                #Recopie des valeurs contenues dans infos, titre, et localisation
                if feat_values_infos[i] != '':
                    feat_values_description[i] = feat_values_infos[i]
            
            
            """
            Version un seul champ concaténé
            #On récupère les informations contenues dans le titre, dans la description, et dans infos
            feat_values_description = self.extraction_features(annonce["titre"] + annonce["infos"] + annonce["description"])
            """
            
            
            #On récupère les coordonnées des métros renseignés dans le champ métro
            for metro in annonce["metro"]:
                if metro in self.dict_xCoordonnees_metros:
                    #Si c'est le premier lieu trouve, il faut remplacer le "" par un []
                    if feat_values_description[self.pos_xCoordinate] == "":
                        feat_values_description[self.pos_xCoordinate] = []
                        feat_values_description[self.pos_yCoordinate] = []
                    else:
                        #Si on a déjà un entier dans la case, il faut le remplacer par un tableau avec l'entier en question
                        if isinstance(feat_values_description[self.pos_xCoordinate], int):
                            feat_values_description[self.pos_xCoordinate] = [feat_values_description[self.pos_xCoordinate]]
                            feat_values_description[self.pos_yCoordinate] = [feat_values_description[self.pos_yCoordinate]]
                    
                    #On ajoute les valeurs des coordonnees du métro trouvé
                    feat_values_description[self.pos_xCoordinate].append(self.dict_xCoordonnees_metros[metro])
                    feat_values_description[self.pos_yCoordinate].append(self.dict_yCoordonnees_metros[metro])
                    
                    #Affichage d'un lieu trouve : ligne non prise en compte quand on lance l'analyse de tous les textes
                    if fonction_test:
                        print "Metro trouve (pap) : " + metro + " (%d, %d)." %(self.dict_xCoordonnees_metros[metro], self.dict_yCoordonnees_metros[metro])
                    
                    #Suivi du nombre de metros trouves avec mon algorithme
                    self.nombre_metros_trouves += 1
                    
            #Lorsque l'on fait des tests, on fait un peu d'affichage
            if fonction_test:
                print ""        
            
            
            #Une fois remplie la liste des coordonnées de métros, on prend la moyenne
            if feat_values_description[self.pos_xCoordinate] != "":
                feat_values_description[self.pos_xCoordinate] = str(int(np.mean(feat_values_description[self.pos_xCoordinate])))
                feat_values_description[self.pos_yCoordinate] = str(int(np.mean(feat_values_description[self.pos_yCoordinate])))
            
            #On rajoute le prix à la main (la fonction float("") bug si la chaîne est vide)
            if annonce["prix"] != "":
                feat_values_description.append(int(float(annonce["prix"].replace(".","").replace(",", ".").replace("HC","").replace("CC",""))))
        
        
        
        
        
        
        
        
        #paruvendu
        #Attention il y a des espaces dans les prix
        if site_annonce == "paruvendu":
            #Champs : "titre", "infos", "description", "prix", "localisation"
            
            """
            Version description séparée
            """
            #On récupère les informations contenues dans le titre, dans les infos, dans la localisation, et dans la description
            #Dans description on cherche des mentions de lieux
            #On rajoute le nom du site à la main pour les features de site web
            feat_values_infos = self.extraction_features(annonce["titre"] + annonce["infos"] + annonce["localisation"] + "site "+site_annonce)
            feat_values_description = self.extraction_features(annonce["description"], True, fonction_test)
            
            #Les informations dans le titre, dans les infos, et dans la localisation priment sur celles
            #contenues dans la description en cas de redondance.
            #titre > localisation > infos > description
            #Mais il y a plus d'informations dans la description donc on part des valeurs tirées de la description       
            for i in range(len(feat_values_description)):
                #Recopie des valeurs contenues dans infos, titre, et localisation
                if feat_values_infos[i] != '':
                    feat_values_description[i] = feat_values_infos[i]
            
            
            
            """
            Version un seul champ concaténé
            #On récupère les informations contenues dans le titre, dans la description, dans infos, et dans la localisation
            feat_values_description = self.extraction_features(annonce["titre"] + annonce["infos"] + annonce["description"] + annonce["localisation"])
            """
            
            
            #On rajoute le prix à la main (la fonction float("") bug si la chaîne est vide)
            #Il y a des espaces qu'il faut enlever
            if annonce["prix"] != "":
                feat_values_description.append(int(float(annonce["prix"].replace(",", ".").replace(" ", "").replace("HC","").replace("CC",""))))
        
        
        
        
        
        
        
        
        #notresite
        if site_annonce == "notresite":
            #Champs : "description"
            
            #On récupère les informations contenues dans le titre, dans la description
            #Pas besoin de chercher le lieu dedans, on ne met pas de stations de métro proches
            feat_values_description = self.extraction_features(annonce["description"])
            
            #On n'a pas de prix vu que l'on veut une estimation, donc on met la valeur à 0
            feat_values_description.append(0)
        
        
        
        
        
        """
        Opérations faites dans tous les cas
        """
        
        #Emmanuel m'a demandé d'arrondir les prix au millier, je le fais dans tous les cas
        #Le prix est en toute dernière place de ma liste donc je peux trouver sa place avec len()-1
        if site_annonce != "":
            feat_values_description[len(feat_values_description) - 1] = int(math.ceil(feat_values_description[len(feat_values_description) - 1] / 1000) * 1000)
        
        
        #Coordonnees de l'arrondissement si on n'a rien trouvé de mieux
        if site_annonce != "":
            if feat_values_description[self.pos_xCoordinate] == "":
                if feat_values_description[self.pos_ardt] in self.dict_xCoordonnees_ardt:
                    #Remplissage des coordonnees de l'arrondissement
                    feat_values_description[self.pos_xCoordinate] = str(self.dict_xCoordonnees_ardt[feat_values_description[self.pos_ardt]])
                    feat_values_description[self.pos_yCoordinate] = str(self.dict_yCoordonnees_ardt[feat_values_description[self.pos_ardt]])
                    
                    #Et on met la feature correspondante à 0 (0 signifie qu'on a juste l'arrondissement)
                    feat_values_description[self.pos_coor_precises] = 0
            else:
                #Sinon c'est qu'on a une annonce avec un lieu (métro pap ou lieu autre) dedans
            
                #Donc on augmente le nombre d'annonces avec un lieu
                self.nombre_annonces_avec_lieu += 1
                
                #Et on met la feature correspondante à 1 (1 signifie qu'on a un lieu précis)
                feat_values_description[self.pos_coor_precises] = 1
        
        
        #Report des valeurs des features négatives et suppression des features négatives
        for i in range(len(self.tab_features)):
            #numéro de la feature à négationner
            feature_number = self.tab_features[i][self.column_negation - 1]
            
            #Si ce n'est pas une chaîne vide, c'est une feature négative
            if feature_number != "":
                #la feature à négationner est deux lignes plus bas que la valeur, car le tableau commence à 0
                #et qu'on a pas pris dans le tableau la première ligne du fichier Excel
                #Il faut transformer la valeur en int car c'est encore un string
                feature_number = int(feature_number) - 2
                
                #Si elle a été mise à un dans le traitement de l'annonce, il faut négationner la featurecorrespondante
                if feat_values_description[i] == 1:
                    feat_values_description[feature_number] = 0
        
        
        
        
        #Suppression des features négatives
        #Il faut garder le nombre de delete car on parcourt deux tableaux différents à la fois
        nombre_deletions = 0
        for i in range(len(self.tab_features)):
            
            
            #Si ce n'est pas une chaîne vide, c'est une feature négative
            if self.tab_features[i][self.column_negation - 1] != "":
                #On la supprime dans le tableau de sortie
                del feat_values_description[i - nombre_deletions]
                
                #On oublie pas d'incrémenter le nombre de delete
                nombre_deletions += 1
        
        
        
        
        
        
        """
        Opérations faites dans tous les cas, sauf pour notre site
        """
        #Ajout de l'url et de la description dans le fichier à la demande d'Adrien et Marion
        if site_annonce != "" and site_annonce != "notresite":
            feat_values_description.append(annonce["url"])
            feat_values_description.append(annonce["titre"])
            feat_values_description.append(annonce["description"])
        
        
        
        
        
        
        #La sortie : le tableau de features avec le prix au bout
        return feat_values_description
    
    
    
    
    
    
    
    
    
    
    
    #Extraction de toutes les annonces d'un fichier json résultant du crawling, et écriture dans un fichier csv
    #des features pour chacune des annonces
    def traitement_fichier(self, fichierJson, fichier_sortie = None):
        """
        fichierJson est le nom d'un fichier Json contenant des annonces extraites d'un site Web :
        Il doit se terminer par .json
        Chaque fichier Json doit contenir un champ "prix" car on vérifie qu'il est non nul et non égal à Prix NC    
        
        fichier_sortie est un csv.writer donnant le fichier dans lequel renseigner les caractéristiques.
        
        Si on ne donne pas de fichier_sortie, la fonction traitement_fichier
        crée un fichier csv du nom fichierJson_traite.csv, contenant les valeurs
        des features (et le prix) pour chaque annonce, avec une ligne par annonce
        """
        
        #Réinitialisation du nombre de lieux trouves
        self.nombre_lieux_trouves = 0
        
        #Réinitialisation du nombre d'annonces comportant un lieu
        self.nombre_annonces_avec_lieu = 0
        
        #Si on n'a pas donné de fichier de sortie dans les paramètres, on en crée un
        #Création du fichier csv qui contiendra les données
        #On remplace l'extension en .json par _traite.csv
        if fichier_sortie == None:
            fichier_sortie = csv.writer(open(fichierJson.replace(".json","") + "_traite.csv", "wb"))
        
            #On peut déjà renseigner les en-tête : les noms de features
            fichier_sortie.writerow(self.feature_and_price_list)
        
        #Import du fichier Json des annonces
        annoncesJson = json.load(open(fichierJson))
        
        #Nombre d'annonces à traiter
        nombre_annonces = len(annoncesJson)    
        
        #Suivi du traitement sur la console
        print "Fichier "+ fichierJson + " : traitement de %s annonces..." %nombre_annonces
        
        #Calcul du temps de traitement des annonces
        temps_debut = time.clock()
        
        #On traite chacune des annonces une par une
        #On vérifie que les prix sont bien des valeurs numériques, et qu'il n'y a pas d'espaces
        #On enlève des prix les espaces, on remplace les "." par des ","
        #Et on enlève les "HC" qui causent des problèmes pour certains apparts en location
        for i in range(nombre_annonces):
            if annoncesJson[i]["prix"].replace(".","").replace(" ","").replace("HC","").replace("CC","").isdigit():
                fichier_sortie.writerow(self.traitement_annonce(annoncesJson[i]))
            
            #Affichage du nombre d'annonces par seconde au bout de 50 annonces pour estimer le temps total
            if (i == 10):
                temps_fin = time.clock()
                temps_total = temps_fin - temps_debut + 0.0
                annonces_par_seconde = (i + 0.0)/(temps_total + 0.001)
                print "%1.1f annonces/seconde." %annonces_par_seconde
                
                
            #Affichage du nombre d'annonces toutes les 100 annonces pour suivre l'avancement
            if (i>0 and (i%100) == 0):
                print "%s/%s" %(i, nombre_annonces)
        
        
        #Calcul du temps de traitement des annonces
        #On ajoute 0.001 au temps total pour éviter la division par zéro si le traitement est instantané
        temps_fin = time.clock()
        temps_total = temps_fin - temps_debut + 0.0
        annonces_par_seconde = (nombre_annonces + 0.0)/(temps_total + 0.001)
        
    
        #Impression du temps de traitement
        print "%s annonces traitées en %1.1f secondes, soit %1.1f annonces/seconde." %(nombre_annonces, temps_total, annonces_par_seconde)
        print "Nombre de lieux trouvés (hors métros pap) : %d." %self.nombre_lieux_trouves
        print "Nombre d'annonces comportant un lieu : %d." %self.nombre_annonces_avec_lieu
        print ""
    
    
    
    
    
    
    
    
    #Extraction de toutes les annonces de tous les fichiers d'un dossier contenant des fichiers Json
    def traitement_dossier(self, dossierEnInput):
        """
        dossierFichiers est le chemin d'un dossier contenant des .json d'annonces
        La fonction traitement_dossier crée un fichier csv concaténant toutes les caractéristiques
        de toutes les annonces de tous les fichiers du dossier. Ce fichier csv est placé à côté du dossier
        (et pas dans le dossier).
        """
        
        #Calcul du temps total du programme
        temps_debut = time.clock()
        
        #Le chemin d'accès complet au dossier qui est dans l'Input
        dossierFichiers = "Input/" + dossierEnInput
        
        #Le fichier de sortie dans lequel on écrira les données
        fichier_sortie = csv.writer(open(self.dossier_output + "/" + dossierEnInput + "_traite.csv", "wb"))
        
        #On renseigne les en-tête : les noms de features
        fichier_sortie.writerow(self.feature_and_price_list)    
        
        #Suivi du traitement sur la console
        print "Traitement du dossier " + dossierEnInput
        
        #On parcourt tous les fichiers du dossier
        for fichierJson in os.listdir(dossierFichiers):
            if fichierJson[-5:] == ".json":
                #On traite chaque fichier un par un en écrivant les données dans fichier_sortie
                self.traitement_fichier(dossierFichiers + "/" + fichierJson, fichier_sortie)
        
        
        #Calcul du temps total du programme
        temps_fin = time.clock()
        temps_total = temps_fin - temps_debut
        
    
        #Impression du temps de traitement
        #Moins d'une minute
        if temps_total < 60:
            print "Temps total du programme : %d secondes." %(temps_total)
        else:
            #Entre une et deux minutes
            if temps_total < 120:
                print "Temps total du programme : 1 minute %d secondes." %(temps_total - 60)
            else:
                #Entre deux minutes et une heure
                if temps_total < 3600:
                    print "Temps total du programme : %d minutes %d secondes." %(int(temps_total/60), temps_total%60)
                else:
                    #Entre une et deux heures
                    if temps_total < 7200:
                        print "Temps total du programme : 1 heure %d minutes %d secondes." %(int(temps_total/60) - 60, temps_total%60)
                    else:
                        #Au-delà de deux heures
                        print "Temps total du programme : %d heure %d minutes %d secondes." %(int(temps_total/3600), int(temps_total/60) - 60*int(temps_total/3600), temps_total%60)
        
    
    
    
    
    
    

    def test_une_annonce(self, site=0, numero_annonce=0):
        """
        Fonction pour comparer le texte d'une annonce (aléatoire par défaut) avec les features que je donne
        """
        
        #Saut de ligne initial
        print ""
        
        
        #Valeur du site
        if site > 6 or site < 0:
            print "Veuillez rentrer un site entre 0 et 6 SVP."
            
            #Saut de ligne final
            print ""
            
            return
            
        
        #Choix aléatoire du site si rien n'est renseigné
        if site == 0:
            site = int(np.floor(6 * np.random.rand() + 1))
        
        #nom du site
        sitename = ""
        if site == 1:
            sitename = "explorimmo-10-22"
        if site == 2:
            sitename = "fnaim-10-22"
        if site == 3:
            sitename = "laforet-10-22"
        if site == 4:
            sitename = "pap-10-23"
        if site == 5:
            sitename = "paruvendu-10-22"
        if site == 6:
            sitename = "seloger_15eme-11-02"
            
        #Ouverture du fichier du site
        fichierJson = "Input/appart_vente_11-02/items_appart_" + sitename + ".json"
        annoncesJson = json.load(open(fichierJson))

        #Nombre d'annonces dans le fichier
        nombre_annonces = len(annoncesJson)
        
        #Choix aléatoire d'une annonce si rien n'est renseigné
        if numero_annonce == 0:
            numero_annonce = int(np.floor(nombre_annonces * np.random.rand()))
        
        #Si l'annonce rentrée est supérieure au nombre d'annonces dans le fichier
        if numero_annonce > nombre_annonces:
            print "Numéro d'annonce : %d plus grand que le nombre d'annonces dans le fichier : %d." %(numero_annonce, nombre_annonces)
            
            #Saut de ligne final
            print ""
            
            return
        
        #Extraction des features avec ma fonction
        annonce = annoncesJson[numero_annonce]
        features_de_lannonce = self.traitement_annonce(annonce, True)
        
        #Impression d'informations sur la console
        print "Site " + sitename + " (n°%d)," %site+ " annonce numéro %d." %numero_annonce
        print "Contenu de l'annonce :"
        
        #Les différents champs : "titre", "infos", "description", "prix", "localisation", "metro"
        if "url" in annonce:
            print "Url : " + annonce["url"]
        if "titre" in annonce:
            print "Titre : " + annonce["titre"]
        if "infos" in annonce:
            print "Infos : " + annonce["infos"]
        if "localisation" in annonce:
            print "Localisation : " + annonce["localisation"]
        if "metro" in annonce:
            #Pour les métros, on est obligés de faire une liste des métros à la main
            liste_metros = ""
            for j in range(len(annonce["metro"])):
                if j > 0:
                    liste_metros += " | "
                liste_metros += annonce["metro"][j]
            print "Metros : " + liste_metros
        if "description" in annonce:
            print "Description : " + annonce["description"]
        if "prix" in annonce:
            print "Prix : " + annonce["prix"]
            
        
        
        
        #Impression des features extraites : seulement celles remplies
        print ""
        print "Features extraites avec le traitement du texte :"
        
        for i in range(len(features_de_lannonce)):
            #Si la feature est remplie on l'imprime
            if features_de_lannonce[i] != "":
                #On différencie si la valeur est un string ou un entier.
                if isinstance(features_de_lannonce[i], str):
                    print self.feature_and_price_list[i] + " : " + features_de_lannonce[i]
                else:
                    print self.feature_and_price_list[i] + " : %s." %features_de_lannonce[i]
                

        
        #Saut de ligne final
        print ""        
        return

"""
Commandes de tests
"""
#Test de la fonction extraction_features
#texte_test = "Au 3eme etage avec ascenseur d'un bel immeuble pierre de taille, appartement 5/6 pieces d'une surface de 213 m2 comprenant une entree, un sejour de 80 m2, 3 grandes chambres, possibilite 4 chambres, une tres grande cuisine dinatoire, 1 salle de bains avec WC, une salle d'eau (buanderie), un WC independant. Parquet au sol. Appartement tres lumineux, double exposition (Nord/Est et Sud/Ouest. Possibilite de le diviser. Emplacement de parking dans la cour. Gardienne digicode et interphone. 1 575 000 E. Contact: Laurence de Villeneuve. RESUME DES CARACTERISTIQUES : Surface de 213 m2, 6 Etages, 3 Etage, 5 Pieces, 4 Chambres, 1 Salle de bains, 1 Salle d'eau, 2 Toilettes, Toilettes Separees, Parquet, Television Par Cable, Ascenseur, 1 Parking, Situation : ville, Chauffage gaz, Cuisine americaine equipee, Interphone, Digicode, Gardien, Entree, 35 m2 Salle a manger, Salle de sejour : 85 m2, Orientation Est, Nord, Ouest..."
#texte_test = ""
#extraction_features(texte_test.lower())


#Test de la fonction traitement_fichier
#traitement_fichier('items_seLoger-10-12.json')




#Pour tester l'affichage de mes dictionnaires de coordonnées
#print Text_analysis().dict_yCoordonnees_lieux

#Test avec une annonce de test
#annoncetest = {"description": "henri martin-pompe quartier residentiel metros. bel appt 9p spacieux 296m2 4 etage asc traversant. bel imm pdt tres bon standing ensoleille double sejour 47m2 salle a manger 34m2 cuisine dinatoire 21m2, 6 chambres tres beaux volumes hsp 3,40m nbx rangements 2 s.bains, s.eau. 2 services reunissables inclus. tres bon plan modulable caves. ch. copro: 8004 e par an. hono. 4%ttc. dpe en cours.", "url": "http://www.fnaim.fr/annonce-immobiliere/36009398/17-acheter-appartement-paris-75.htm", "localisation": "paris 16", "prix": "2700000", "agence": "john arthur et tiffen, 130 avenue victor hugo", "titre": "appartement 9 piece(s) - 300 m2", "infos": "type d'habitation : appartement, numero d'etage : 4, nombre d'etage : 7, surface habitable : 300 m2, surface du sejour : 47 m2, nombre de chambres : 6, nombre de salles de bains : 2, nombre de salles deau : 1, cave : 2, type de chauffage : collectif"}
#print Text_analysis().traitement_annonce(annoncetest)

#Test avec impression propre sur des annonces aléatoires
Text_analysis().test_une_annonce()

#Pour tester sur certains fichiers
#Text_analysis().traitement_dossier('Test')

"""
Appel de la fonction traitement_dossier sur les vraies données
"""
#Text_analysis().traitement_dossier('appart_vente_11-02')