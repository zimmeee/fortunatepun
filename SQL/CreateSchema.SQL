DROP TABLE IF EXISTS URLer;
CREATE TABLE URLer(
   urlid			INT NOT NULL,
   twitter_id		BIGINT NOT NULL,
   twitter_handle	VARCHAR(16) NOT NULL,
   tweetid			BIGINT,
   tweet_time 		DATETIME,
   UNIQUE(tweetid)
);

DROP TABLE IF EXISTS URL;
CREATE TABLE URL(
	urlid		INT NOT NULL AUTO_INCREMENT,
	t_url		VARCHAR(24),
	url			VARCHAR(2000),
	PRIMARY KEY ( urlid )
);

DROP TABLE IF EXISTS tokens;
CREATE TABLE tokens(
	twitter_id			BIGINT NOT NULL,
	twitter_handle		VARCHAR(16) NOT NULL,
	oauth_token			text,
	oauth_token_secret 	text
);


INSERT INTO URLer VALUES(1,789, 'zimmeee', 1, NOW() );
INSERT INTO URLer VALUES(1,789, 'rbruggner', 2, NOW() );
INSERT INTO URLer VALUES(1,789, 'wasauce', 3, NOW() );

INSERT INTO URLer VALUES(3,789, 'zimmeee', 4, NOW() );
INSERT INTO URLer VALUES(2,789, 'rbruggner', 5, NOW() );
INSERT INTO URLer VALUES(3,789, 'wasauce', 6, NOW() );

INSERT INTO URL VALUES(1,'a.co', 'http://www.twitter.com' );
INSERT INTO URL VALUES(2,'b.co', 'http://www.kyron.com' );
INSERT INTO URL VALUES(3,'c.co', 'http://www.nytimes.com' );

