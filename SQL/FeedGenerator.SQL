SELECT expanded_url, title, count(DISTINCT(twitter_handle)) as votes, group_concat( DISTINCT twitter_handle ) as tweeters 
FROM URLer JOIN URL USING(urlid) 
WHERE twitter_id = (select twitter_id FROM tokens WHERE twitter_handle = 'zimmeee')
AND DATE_SUB( tweet_time, INTERVAL 1 DAY) < tweet_time 
AND expanded_url IS NOT NULL 
GROUP BY expanded_url, title ORDER BY count(DISTINCT(twitter_handle)) DESC LIMIT 50;


-- This is the one that actually works right!
SELECT expanded_url, title, count(DISTINCT(twitter_handle)) as votes
FROM URLer JOIN URL USING(urlid)
WHERE twitter_id = (select twitter_id FROM tokens WHERE twitter_handle = 'zimmeee')
AND expanded_url IS NOT NULL
AND tweet_time >= now() - INTERVAL 1 DAY
AND twitter_handle != 'lastwhale'
GROUP BY 1,2
ORDER BY count(DISTINCT(twitter_handle)) DESC
