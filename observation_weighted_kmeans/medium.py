from data_weighted_kmeans import *
import numpy as np
import csv
from haversine import haversine
import random

def find_nearest_zip(points,centers):
	for c in centers:
		clat=c['coords'][1]
		clong=c['coords'][0]
		ds=[]
		for p in points:
			plat=p['coords'][1]
			plong=p['coords'][0]
			d=distance(clat,clong,plat,plong)
			ds.append(d)
		idx = np.argmin(np.array(ds))
		c['nearest_zip']   = points[idx]['zip']
		c['nearest_state'] = points[idx]['state']
	return centers

random.seed(42)
k=4

points=[]
with open("us_census.csv", 'rb') as csvfile:
	reader = csv.reader(csvfile, delimiter=',', quotechar='"')
	header=reader.next()
	for row in reader:
		d = dict(zip(header,row))
		if not (d['state'] in ('AK','HI','PR')):
			points.append({"coords": np.array([float(d['longitude']),float(d['latitude'])]),"w":int(d['population']),"zip":d['zip'],"state":d["state"]})

points = random.sample(points,1000)
centers = equally_spaced_initial_clusters(points,k)

points,centers,it_num = data_weighted_kmeans(points,centers,k)

centers=find_nearest_zip(points,centers)

print "k,zip,state,latitude,longitude,population,c,clat,clong,cdistance,nearest_zip,nearest_state"

#create dictionary of centers keyed off their ID
d={}
for i,c in enumerate(centers):
	d[i]=c

for p in points:
	p1=p["coords"]
	p2=d[p['c']]['coords']
	dist=str(int(distance(p1[1],p1[0],p2[1],p2[0])))
	out=[k]
	out.append(p["zip"])
	out.append(p["state"])
	out.append(p["coords"][1]) #lat
	out.append(p["coords"][0]) #long
	out.append(p['w'])
	out.append(p['c'])
	out.append(d[p['c']]['coords'][1]) #lat
	out.append(d[p['c']]['coords'][0]) #long
	out.append(dist)
	out.append(d[p['c']]['nearest_zip'])
	out.append(d[p['c']]['nearest_state'])
	print ",".join([str(s) for s in out])
