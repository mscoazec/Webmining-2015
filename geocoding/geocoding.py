# -*- coding: utf-8 -*-
"""
Created on Mon Oct 26 10:42:31 2015

@author: mscoazec

Geolocalisation des rues de paris.

"""

import urllib2
import json
import csv
import numpy as np
import unicodedata

filename = "voiesactuellesparis2012_5.csv"
out_filename = "rues_paris_5.csv"

##### ##### #####

# ouverture du csv
r = csv.reader(open(filename,"rb"),delimiter=',')
x = list(r)

# labels des colonnes du csv
labels = x[0]

# donnees du csv
data = x[1:]
data = np.array(data)

#

init = 0;

if init:
        
    data1 = data[1:len(data)/6]
    data2 = data[len(data)/6+1:2*len(data)/6]
    data3 = data[2*len(data)/6+1:3*len(data)/6]
    data4 = data[3*len(data)/6+1:4*len(data)/6]
    data5 = data[4*len(data)/6+1:5*len(data)/6]
    data6 = data[5*len(data)/6+1:len(data)]
    
    csvfile = open("voiesactuellesparis2012_1.csv", "w")
    writer = csv.DictWriter(csvfile, fieldnames=["voie"], lineterminator='\n')
    writer.writeheader()
    for d in data1:
        d = unicode(d[0], 'utf-8')
        d = unicodedata.normalize('NFD', d).encode('ascii', 'ignore')
        writer.writerow({"voie": d})
    csvfile.close()
    
    csvfile = open("voiesactuellesparis2012_2.csv", "w")
    writer = csv.DictWriter(csvfile, fieldnames=["voie"], lineterminator='\n')
    writer.writeheader()
    for d in data2:
        d = unicode(d[0], 'utf-8') 
        d = unicodedata.normalize('NFD', d).encode('ascii', 'ignore')
        writer.writerow({"voie": d})
    csvfile.close()
    
    csvfile = open("voiesactuellesparis2012_3.csv", "w")
    writer = csv.DictWriter(csvfile, fieldnames=["voie"], lineterminator='\n')
    writer.writeheader()
    for d in data3:
        d = unicode(d[0], 'utf-8')
        d = unicodedata.normalize('NFD', d).encode('ascii', 'ignore')
        writer.writerow({"voie": d})
    csvfile.close()
    
    csvfile = open("voiesactuellesparis2012_4.csv", "w")
    writer = csv.DictWriter(csvfile, fieldnames=["voie"], lineterminator='\n')
    writer.writeheader()
    for d in data4:
        d = unicode(d[0], 'utf-8')
        d = unicodedata.normalize('NFD', d).encode('ascii', 'ignore')
        writer.writerow({"voie": d})
    csvfile.close()
    
    csvfile = open("voiesactuellesparis2012_5.csv", "w")
    writer = csv.DictWriter(csvfile, fieldnames=["voie"], lineterminator='\n')
    writer.writeheader()
    for d in data5:
        d = unicode(d[0], 'utf-8')
        d = unicodedata.normalize('NFD', d).encode('ascii', 'ignore')
        writer.writerow({"voie": d})
    csvfile.close()
    
    csvfile = open("voiesactuellesparis2012_6.csv", "w")
    writer = csv.DictWriter(csvfile, fieldnames=["voie"], lineterminator='\n')
    writer.writeheader()
    for d in data6:
        d = unicode(d[0], 'utf-8')
        d = unicodedata.normalize('NFD', d).encode('ascii', 'ignore')
        writer.writerow({"voie": d})
    csvfile.close()
    
if 1:
    
    csvfile = open(out_filename, "w")
    writer = csv.DictWriter(csvfile, fieldnames=["requete","formattage","lat","lng"], lineterminator='\n')
    writer.writeheader()
    
    for adr in data:
        
        str_adr = unicode(adr[0], 'utf-8')
        str_adr = unicodedata.normalize('NFD', str_adr).encode('ascii', 'ignore')     
        
        if str_adr:
            
            str_adr = str_adr.replace(" ","+") + ",Paris,France"
            
            json_objet = urllib2.urlopen("http://maps.googleapis.com/maps/api/geocode/json?address=" + str_adr).read()
            json_objet = json.loads(json_objet)
            
            res = json_objet["results"]
            
            if res:
                
                res = res[0]
                
                s = res["formatted_address"]
                l1 = res["geometry"]["location"]["lat"]
                l2 = res["geometry"]["location"]["lng"]
                
                print s
                
                if 0:
                    print str_adr
                    print s
                    print str(l1) + " " + str(l2)
                    print ""
                
                s = unicodedata.normalize('NFD', s).encode('ascii', 'ignore')
            
                writer.writerow({"requete": str_adr, "formattage" : s, "lat" : l1, "lng" : l2})    
    
    csvfile.close()