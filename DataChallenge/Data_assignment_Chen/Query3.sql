select PLACEMENT_KEY,
       country,
	   DEVICE_CATEGORY,
       video_plays, 
       facebook_shares + TWITTER_SHARES + EMAIL_SHARES + VINE_SHARES + CUSTOM_SHARES as SocialMedia_shares,
       AUTOPLAY_VIEWS,
       THREE_SECOND_VIEWS,
       TEN_SECOND_VIEWS,
       GUARANTEED_BRAND_SAFE,
       LOCATION_TYPE,
       LAYOUT_TYPE
from sharethroughdb.mpcde as m
inner join sharethroughdb.pl as P
on m.PLACEMENT_KEY = P.KEY
where TOTAL_ENGAGEMENTS >0