
# To create the Voronoi diagrams, I used code from
# http://www.r-bloggers.com/making-staticinteractive-voronoi-map-layers-in-ggplotleaflet/
# with a few small changes:
# I pass in bounding box parameters to SPointsDF_to_voronoi_SPolysDF function
# I don't need arrange or size parameter in plot

#############################################
# r_input.csv is the output of medium.py:
#
# python2.7 medium.py > r_input.csv
#############################################
d<-read.csv("r_input.csv")

library(data.table)

SPointsDF_to_voronoi_SPolysDF <- function(sp,bbxmin, bbxmax, bbymin, bbymax) {
 
  # tile.list extracts the polygon data from the deldir computation

  #Carl's modification from blog post:
  vor_desc <- tile.list(deldir(sp@coords[,1], sp@coords[,2],rw=c(bbxmin, bbxmax, bbymin, bbymax)))
 
  lapply(1:(length(vor_desc)), function(i) {
 
    # tile.list gets us the points for the polygons but we
    # still have to close them, hence the need for the rbind
    tmp <- cbind(vor_desc[[i]]$x, vor_desc[[i]]$y)
    tmp <- rbind(tmp, tmp[1,])
 
    # now we can make the Polygon(s)
    Polygons(list(Polygon(tmp)), ID=i)
 
  }) -> vor_polygons
 
  # hopefully the caller passed in good metadata!
  sp_dat <- sp@data
 
  # this way the IDs _should_ match up w/the data & voronoi polys
  rownames(sp_dat) <- sapply(slot(SpatialPolygons(vor_polygons),
                                  'polygons'),
                             slot, 'ID')
 
  SpatialPolygonsDataFrame(SpatialPolygons(vor_polygons),
                           data=sp_dat)
}

for (k in 2:10){

	# for k=1, voronoi doesn't make sense so run code below manually commenting out 2nd goem_map
	# call

	dt<-as.data.table(d[d$k==k,])
	setkey(dt,"c")
	centers<-unique(dt)
	setkey(dt,NULL)

	cts<-data.frame(longitude=centers$clong,latitude=centers$clat)
	vor_pts <- SpatialPointsDataFrame(cbind(cts$longitude,cts$latitude),data=cts)
	vor <- SPointsDF_to_voronoi_SPolysDF(vor_pts,-127,-65,24,50)
	vor_df <- fortify(vor) 
	states <- map_data("state")

	jpeg(paste("2013_2014_wp_k",k,".jpg",sep=""),width=800,height=600)

	gg <- ggplot()
	# base map
	gg <- gg + geom_map(data=states, map=states,
						aes(x=long, y=lat, map_id=region),
						color="white", fill="#cccccc", size=0.5)
	# airports layer
	gg <- gg + geom_point(data=cts,
						  aes(x=longitude, y=latitude,size=10),
						  shape=21, color="white", fill="steelblue")
					  

	# this command won't work for k=1					  
	gg <- gg + geom_map(data=vor_df, map=vor_df,
						aes(x=long, y=lat, map_id=id),
						color="#a5a5a5", fill="#FFFFFF00", size=0.25)

	gg <- gg + scale_size(range=c(2, 9))
	gg <- gg + coord_map("albers", lat0=30, lat1=40)
	gg <- gg + theme_map()
	gg <- gg + theme(legend.position="none")
	gg

	dev.off()
}

#####################################################
# to look at mean distance versus k, we need a weighted mean:
#####################################################
dt<-as.data.table(d)
out=NULL
for (i in 1:10){
	m<-weighted.mean(dt[k==i]$cdistance,dt[k==i]$population)
	out<-rbind(out,c(i,m))
}
jpeg("distance_versus_k.jpg",width=800,height=600)
plot(out,type="l",xlab="k",ylab="Weighted average distance",col="steelblue",lwd=5)
dev.off()

#####################################################
# for weighted percentiles, we do the following:
#####################################################
library(Hmisc)
out=NULL
for (i in 1:10){
	m<-wtd.quantile(x=dt[k==i]$cdistance,weights=dt[k==i]$population)
	out<-rbind(out,c(i,m))
}

df<-data.frame(k=seq(1:10),p25=out[,3],p50=out[,4],p75=out[,5],p100=out[,6])
jpeg("distancemetrics_versus_k.jpg",width=800,height=600)
plot(df$k,df$p100,type="l",ylim=c(0,1800),col="steelblue",lwd=5,xlab="k",ylab="Weighted distance")
lines(df$k,df$p75,col="steelblue",lwd=5)
lines(df$k,df$p50,col="steelblue",lwd=5)
lines(df$k,df$p25,col="steelblue",lwd=5)
dev.off()
