# -*- coding: utf-8 -*-
"""
Created on Wed Oct 21 15:51:09 2015

@author: Marion
"""

import csv
import numpy as np
from pylab import *
import matplotlib.pyplot as plt

filename = "apparts_cinq_sites_10-21_traite.csv"

r =csv.reader(open(filename,"rb"),delimiter=',')
x = list(r)

labels = x[0]
data = x[1:]

data = np.array(data)

# string vide to 0 pour cast
data[data=='']='0'

data = data.astype(np.float)

# prix en fonction de la surface

y = data[:,labels.index('prix')]
x = data[:,labels.index('surface')]
plt.scatter(x, y)
plt.show()

# nombre de donnees par arrondissement