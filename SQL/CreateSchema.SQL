DROP TABLE IF EXISTS URLer;
CREATE TABLE URLer(
   urlid			INT NOT NULL,
   twitter_handle 	VARCHAR(16) NOT NULL,
   time 			DATETIME
);

DROP TABLE IF EXISTS URL;
CREATE TABLE URL(
	urlid		INT NOT NULL AUTO_INCREMENT,
	t_url		VARCHAR(24),
	url			VARCHAR(2000),
	tweetid		VARCHAR(200),
	PRIMARY KEY ( urlid ),
	UNIQUE(tweetid)
);

DROP TABLE IF EXISTS tokens;
CREATE TABLE tokens(
	twitter_id			BIGINT NOT NULL,
	twitter_handle		VARCHAR(16) NOT NULL,
	oauth_token			text,
	oauth_token_secret 	text
);