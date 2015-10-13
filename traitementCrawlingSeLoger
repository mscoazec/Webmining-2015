# -*- coding: utf-8 -*-
"""
Éditeur de Spyder

Ceci est un script temporaire.
"""

from pprint import pprint

import json
import re


with open('items_seLoger-10-12.json') as data_file:    
    data = json.load(data_file)



longueur = len(data)
feat = 'm2'
featdict ={}



for j in range(longueur):
    
    #Surface
    
    curdata1 = data[j]['titre'].lower()
    m=re.search('([0-9,.]+)(( )?m2)', curdata1)
    if m!= None:
        featdict['surface'] = m.group(1)
        
        
        
    #prix
    curdata2 = data[j]['prix'].lower()           
    featdict['prix'] = curdata2
    
    #pièces
    curdata1 = data[j]['titre'].lower()
    m=re.search('([0-9,.]+)(( )?pieces)', curdata1)
    if m!= None:
        featdict['pieces'] = m.group(1)
    else:
        m = re.search('(studio)', curdata1)
        if m!= None:
           featdict['pieces'] = '1'
    
    #arrondissement
    curdata1 = data[j]['titre'].lower()
    m=re.search('([0-9,.]+)(( )?eme)', curdata1)
    if m!= None:
        featdict['arrondissement'] = m.group(1)
        
    
    
    #cave
    curdata1 = data[j]['description'].lower()
    m=re.search('(cave)', curdata1)
    if m!= None:
        featdict['cave'] = '1'
    else:
        featdict['cave'] = '0'
    
    
    #balcon
    curdata1 = data[j]['description'].lower()
    m=re.search('(balcon)', curdata1)
    if m!= None:
        featdict['balcon'] = '1'
    else:
        featdict['balcon'] = '0'
    
#    #etage
#    curdata1 = data[j]['description'].lower()
#    m=re.search('([0-9,.]+)(( )?eme?( )?er?etage)', curdata1)
#    if m!= None:
#        featdict['etage'] = m.group(1)
#        
#    else:
#        featdict['etage'] = 'NA'
        

    
    pprint(featdict)
    
    #Ecriture
    with open('items_seLoger-10-12-traite.json', mode='a+') as f:
        json.dump(featdict, f, indent=4)




