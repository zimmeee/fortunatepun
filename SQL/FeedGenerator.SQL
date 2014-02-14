-- This is the one that actually works right!
SELECT expanded_url, title, count(DISTINCT(twitter_handle)) as votes, group_concat( DISTINCT twitter_handle ) as tweeters, group_concat( DISTINCT tweetid ) as tweetids
FROM URLer JOIN URL USING(urlid)
WHERE twitter_id = (select twitter_id FROM tokens WHERE twitter_handle = 'zimmeee')
AND expanded_url IS NOT NULL
AND tweet_time >= now() - INTERVAL 1 DAY
AND twitter_handle != 'lastwhale'
GROUP BY 1,2
ORDER BY count(DISTINCT(twitter_handle)) DESC;


-- Top hourly tweet
-- We've got some weird time zone stuff going on here. 
-- MySQL uses UTC, 
SELECT expanded_url, title, count(DISTINCT(twitter_handle)) as votes, group_concat( DISTINCT twitter_handle ) as tweeters
FROM URLer JOIN URL USING(urlid)
WHERE expanded_url IS NOT NULL
AND tweet_time >= now() - INTERVAL 1 DAY
AND twitter_handle != 'lastwhale'
GROUP BY 1,2
ORDER BY count(DISTINCT(twitter_handle)) DESC LIMIT 1

-- See who is pulling the maddest links
SELECT twitter_id, tokens.twitter_handle, count(urlid) 
FROM URLer join tokens using(twitter_id) 
GROUP BY 1, 2
ORDER BY 3 desc;


