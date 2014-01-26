DROP TABLE IF EXISTS URLer;
CREATE TABLE URLer(
   urlid			INT NOT NULL,
   twitter_id		BIGINT NOT NULL,
   twitter_handle	VARCHAR(16) NOT NULL,
   tweetid			BIGINT,
   tweet_time 		DATETIME,
   UNIQUE(tweetid, urlid)
);

DROP TABLE IF EXISTS URL;
CREATE TABLE URL(
	urlid			INT NOT NULL AUTO_INCREMENT,
	t_url			VARCHAR(24),
	url				VARCHAR(2000),
	expanded_url	VARCHAR(2000),
	title 			TEXT,
	unexpandable 	BOOLEAN not null default 0
	PRIMARY KEY ( urlid )
);

DROP TABLE IF EXISTS tokens;
CREATE TABLE tokens(
	twitter_id			BIGINT NOT NULL,
	twitter_handle		VARCHAR(16) NOT NULL,
	oauth_token			VARCHAR(128),
	oauth_token_secret 	text,
	UNIQUE( twitter_id, oauth_token )
);


INSERT INTO URLer VALUES(1,789, 'zimmeee', 1, NOW() );
INSERT INTO URLer VALUES(1,789, 'rbruggner', 2, NOW() );
INSERT INTO URLer VALUES(1,789, 'wasauce', 3, NOW() );

INSERT INTO URLer VALUES(3,789, 'zimmeee', 4, NOW() );
INSERT INTO URLer VALUES(2,789, 'rbruggner', 5, NOW() );
INSERT INTO URLer VALUES(3,789, 'wasauce', 6, NOW() );

INSERT INTO URL VALUES(1,'a.co', 'http://www.twitter.com', 'http://www.twitter.com/bonertown', 'Exciting Boner article' );
INSERT INTO URL VALUES(2,'b.co', 'http://www.kyron.com', 'http://www.kyron.com/bonertown', 'Less exciting boner article' );
INSERT INTO URL VALUES(3,'c.co', 'http://www.nytimes.com', 'http://www.nytimes.com/bonertown', 'Least important boner article' );
INSERT INTO URL VALUES(4,'c.co', 'http://www.nytimes.com', NULL, NULL );

