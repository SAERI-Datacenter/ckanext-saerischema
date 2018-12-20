#!/usr/bin/env python2

import numpy as np
import csv
import sys

filename="metadata_FK_export181112_new.csv"
#array=np.genfromtxt(filename, delimiter=',')
#array=np.genfromtxt(filename, delimiter=',', doublequote=False, escapechar='\\')
#print(array)

fp = open(filename)
reader = csv.DictReader(fp)
for row in reader:
	print(row['organisation'])
exit(0)

#rows = list(reader)
headers = rows[0]
print(headers)

#for row in rows[1:]:
#    print zip(headers, row)
