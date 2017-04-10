
import numpy as np
from matplotlib import pyplot
import random
import matplotlib.cm as cm
from haversine import haversine
import math

def show_kmeans(points, centers=None):
	#http://stackoverflow.com/questions/9401658/matplotlib-animating-a-scatter-plot
	xs=[]
	ys=[]
	c=[]
	wts=[]
	m=[]
	colors = list(iter(cm.rainbow(np.linspace(0, 1, len(centers)))))
	for p in points:
		xs.append(p['coords'][0])
		ys.append(p['coords'][1])
		c.append(colors[p['c']])
		#wts.append(40+p['w'])
		wts.append(3)
		m.append('o')

	if centers:
		for i,cl in enumerate(centers):
			xs.append(cl['coords'][0])
			ys.append(cl['coords'][1])
			c.append('yellow')
			wts.append(500)
			m.append('*')

	for _s, _c, _x, _y,_sz in zip(m, c, xs, ys,wts):
		pyplot.scatter(_x, _y, marker=_s, c=_c,s=_sz, lw = 0)

	pyplot.show()

def distance(lat1,long1,lat2,long2):
	return haversine((lat1,long1), (lat2,long2), miles=True)

def data_weighted_kmeans(points,centers,k,it_max=100):
	'''
		Implements weighted k-means where individual data points are weighted

		Code was ported from matlab code:
			http://people.sc.fsu.edu/~jburkardt/m_src/kmeans/kmeans.html

			specifically http://people.sc.fsu.edu/~jburkardt/m_src/kmeans/kmeans_w_03.m

		A natural extension of the K-Means problem allows us to include some more information, namely, 
		a set of weights associated with the data points. These might represent a measure of importance, 
		a frequency count, or some other information. The intent is that a point with a weight of 5.0 is 
		twice as "important" as a point with a weight of 2.5, for instance. This gives rise to the 
		"weighted" K-Means problem.

		In the weighted K-Means problem, we are given a set of N points X(I) in M-dimensions, and a 
		corresponding set of nonnegative weights W(I). The goal is to arrange the points into K clusters, 
		with each cluster having a representative point Z(J), usually chosen as the weighted centroid of 
		the points in the cluster:

		Z(J) = Sum ( all X(I) in cluster J ) W(I) * X(I) / Sum ( all X(I) in cluster J ) W(I).
	
		The weighted energy of cluster J is
			E(J) = Sum ( all X(I) in cluster J ) W(I) * || X(I) - Z(J) ||^2

		Inputs:

		points: list of dictionaries
			with keys: 
				coords: np.array of real/integer values
				w: positive real

		centers: list of dictionaries
			with keys: 
				coords: np.array of real/integer values

		k: number of clusters

		it_max: max number of iterations

	'''
	# number of dimensions
	d = len(points[0]['coords'])

	for c in centers:
		c['n'] = 0
		c['w'] = 0

	#Assign each observation to the nearest cluster center.
	for p in points:
		distances=[]
		for c in centers:
			distances.append(sum((p["coords"]-c["coords"])**2))
		idx = np.argmin(distances)
		p['c'] = idx
		centers[idx]["n"]+=1
		centers[idx]["w"]+=p['w']

	for j,c in enumerate(centers):
		c["coords"] = np.zeros(d)

	#Average the points in each cluster to get a new cluster center.
	for p in points:
		centers[p['c']]["coords"] += p["coords"] * p['w']
	for c in centers:
		c["coords"] /= c['w']

	it_num = 0
	distsq = np.zeros(k)
	while ( it_num < it_max ):
		it_num +=1
		#print it_num
		swap = 0
		for i,p in enumerate(points):
			ci=p['c']
			
			if centers[ci]['n'] <= 1:
				continue

			for cj,c in enumerate(centers):
				lat1=p["coords"][1]
				long1=p["coords"][0]
				lat2=c["coords"][1]
				long2=c["coords"][0]
				if ci==cj:
					distsq[cj]= ( (distance(lat1,long1,lat2,long2)**2) * c['w'] ) / ( c['w'] - p['w'] )
				elif centers[cj]['n']==0:
					centers[cj]["coords"] = np.copy(p["coords"])
					distsq[cj]=0 
				else:
					distsq[cj]= ( (distance(lat1,long1,lat2,long2)**2) * c['w'] ) / ( c['w'] + p['w'] )

			# Find the index of the minimum value of DISTSQ.
			nearest_cluster = np.argmin(distsq)

			# If that is not the cluster to which point I now belongs, move it there.
			if nearest_cluster == ci:
				continue

			cj = nearest_cluster
			centers[ci]["coords"] = ( centers[ci]['w'] * centers[ci]["coords"] - p['w'] * p["coords"] ) / ( centers[ci]['w'] - p['w'] )
			centers[cj]["coords"] = ( centers[cj]['w'] * centers[cj]["coords"] + p['w'] * p["coords"] ) / ( centers[cj]['w'] + p['w'] )
			centers[ci]['n'] -= 1
			centers[cj]['n'] += 1
			centers[ci]['w'] -= p['w']
			centers[cj]['w'] += p['w']

			# assign the point its new home
			p['c'] = cj

			swap += 1
		# Exit if no reassignments were made during this iteration.
		if swap==0: 
			break
	return [points,centers,it_num]

def randomize_initial_cluster(points,k,seed=None):
	'''
		randomly select k starting points
	'''
	if seed:
		random.seed( seed )
	indices=range(0,len(points))
	random.shuffle(indices)
	centers=[]
	for i in indices[:k]:
		centers.append({"coords":np.copy(points[i]['coords'])})
	return centers

def equally_spaced_initial_clusters(points,k):
	'''
	set them equally spaced across x
	'''
	xs=[]
	ys=[]
	for p in points:
		xs.append(p['coords'][0])
		ys.append(p['coords'][1])
	xs=np.array(xs)
	meany = np.mean(np.array(ys))
	minx=np.min(xs)
	maxx=np.max(xs)
	if k==1:
		return [{"coords":np.array([np.mean(np.array(xs)), meany])}] 
	step = (maxx-minx) / (k-1)
	centers=[]
	[centers.append({"coords":np.array([minx + i * step, meany])}) for i in range(k)]
	return centers
