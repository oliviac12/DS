select COUNTRY,
       CATEGORY,
       DEVICE_CATEGORY,
       l.LAYOUT_TYPE,
       l.LOCATION_TYPE,
       clicks,
       TOTAL_ENGAGEMENTS
from sharethroughdb.mpcde as m
	inner join sharethroughdb.pc as P
		on m.placement_key = p.placement_key
	inner join sharethroughdb.pl as l
		on m.PLACEMENT_KEY = l.KEY
where TOTAL_ENGAGEMENTS > 0 AND clicks/IMPRESSIONS*100 <= 1