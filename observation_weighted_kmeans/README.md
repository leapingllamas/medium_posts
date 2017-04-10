# Observation-weighted k-means clustering

This is the code to accompany my medium post:

#### Clustering the US population: observation-weighted k-means

https://medium.com/towards-data-science/clustering-the-us-population-observation-weighted-k-means-f4d58b370002

## Code
`data_weighted_kmeans.py` is the workhorse library of functions that implemented observation-weighted kmeans.

`medium.py` is a script that takes the US census data, ie. ZIP code, latitude , longitude and population (in `us_census.csv`) and for some hard-coded value of k (number of clusters) outputs a CSV consisting of

`k,zip,state,latitude,longitude,population,c,clat,clong,cdistance,nearest_zip,nearest_state`

where `zip,state,latitude,longitude,population` are from the us_census file and `c,clat,clong,cdistance,nearest_zip,nearest_state` are results of the clustering (c = index of the c'th cluster).

`uscensus_loop.R` is R code that principally plots Voronoi diagrams on a map--the ones shown in the medium post--as well as some other diagnostic plots.


