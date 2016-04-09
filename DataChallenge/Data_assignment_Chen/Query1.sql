select PLACEMENT_KEY, 
       country, 
	   device_category, 
       eligible_impression_requests, 
       TOTAL_IMPRESSION_REQUESTS, 
       filled_pages,
       IMPRESSIONS,
       VISIBLE_IMPRESSIONS,
       clicks,
       TOTAL_ENGAGEMENTS,
       VIDEO_PLAYS,
       AUTOPLAY_VIEWS,
       GUARANTEED_BRAND_SAFE,
       LOCATION_TYPE,
       LAYOUT_TYPE
from sharethroughdb.mpcde as m
inner join sharethroughdb.pl as P
on m.PLACEMENT_KEY = P.KEY


