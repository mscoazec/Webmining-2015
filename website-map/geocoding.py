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

filename = "voiesactuellesparis2012.csv"

##### ##### #####

# ouverture du csv
r = csv.reader(open(filename,"rb"),delimiter=',')
x = list(r)

# labels des colonnes du csv
labels = x[0]

# donnees du csv
data = x[1:]
data = np.array(data)

csvfile = open("geo_ruesParis.csv", "w")
writer = csv.DictWriter(csvfile, fieldnames=["requete","formattage","lat","lng"], lineterminator='\n')
writer.writeheader()

for adr in data:
    
    str_adr = unicode(adr[0], 'utf-8')
    str_adr = unicodedata.normalize('NFD', str_adr).encode('ascii', 'ignore')     
                                   
    str_adr = str_adr.replace(" ","+") + ",Paris"
    
    json_objet = urllib2.urlopen("http://maps.googleapis.com/maps/api/geocode/json?address=" + str_adr).read()
    json_objet = json.loads(json_objet)
    
    r = json_objet["results"]
    
    if r:
        
        r = r[0]
        
        s = r["formatted_address"]
        l1 = r["geometry"]["location"]["lat"]
        l2 = r["geometry"]["location"]["lng"]
        
        if 0:
            print str_adr
            print s
            print str(l1) + " " + str(l2)
            print ""
        
        s = unicodedata.normalize('NFD', s).encode('ascii', 'ignore')
    
        writer.writerow({"requete": str_adr, "formattage" : s, "lat" : l1, "lng" : l2})    

csvfile.close()