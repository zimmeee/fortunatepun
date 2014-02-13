import cgi
import webapp2
import urllib2
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import urlfetch

import MySQLdb
import os
import jinja2

import logging


import tweepy
from BeautifulSoup import BeautifulSoup

def comma_split( value ):
  return value.split(',')

def link_tweetids( tweeters, tweetids ):
  ['|'.join( tweeters[i], tweetids[i]) for i in range(len(tweeters))]


# Configure the Jinja2 environment.
JINJA_ENVIRONMENT = jinja2.Environment(
  loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
  autoescape=True,
  extensions=['jinja2.ext.autoescape'])

JINJA_ENVIRONMENT.filters['comma_split'] = comma_split 
JINJA_ENVIRONMENT.filters['link_tweetids'] = link_tweetids

# Define your production Cloud SQL instance information.
_INSTANCE_NAME = 'fortunatepun:datastore'

class MainPage(webapp2.RequestHandler):
    def get(self):
        logging.info("HOMEPAGE request!")
        template = JINJA_ENVIRONMENT.get_template('index.html')

        self.response.write(template.render())


class Guestbook(webapp2.RequestHandler):
    def post(self):
        # Handle the post to create a new guestbook entry.
        fname = self.request.get('fname')
        content = self.request.get('content')

        if (os.getenv('SERVER_SOFTWARE') and
            os.getenv('SERVER_SOFTWARE').startswith('Google App Engine/')):
            db = MySQLdb.connect(unix_socket='/cloudsql/' + _INSTANCE_NAME, db='guestbook', user='root')
        else:
            # db = MySQLdb.connect(host='127.0.0.1', port=3306, user='root')
            # Alternately, connect to a Google Cloud SQL instance using:
            db = MySQLdb.connect(host='173.194.109.208', port=3306, db='guestbook', user='root', passwd='thatspunny' )

        cursor = db.cursor()
        # Note that the only format string supported is %s
        cursor.execute('INSERT INTO entries (guestName, content) VALUES (%s, %s)', (fname, content))
        db.commit()
        db.close()

        self.redirect("/")


class GetAllUsersTweetsHandler(webapp2.RequestHandler):

  def get(self):
    # Get a list of all of the users in the oauths table
    if (os.getenv('SERVER_SOFTWARE') and
        os.getenv('SERVER_SOFTWARE').startswith('Google App Engine/')):
        db = MySQLdb.connect(unix_socket='/cloudsql/' + _INSTANCE_NAME, db='fortunatepun', user='root')
    else:
        # db = MySQLdb.connect(host='127.0.0.1', port=3306, user='root')
        # Alternately, connect to a Google Cloud SQL instance using:
        db = MySQLdb.connect(host='173.194.109.208', port=3306, db='fortunatepun', 
                             user='root', passwd='thatspunny' )

    cursor = db.cursor()
    cursor.execute('SELECT twitter_id, twitter_handle, oauth_token, oauth_token_secret FROM tokens;')
    for row in cursor.fetchall():
      logging.info("token row: %s", row)
      url = "http://fortunatepun.appspot.com/enqueueTweets?twitterId=" + str(row[0])
      result = urlfetch.fetch(url)

    self.response.write("""<html><body>All Good</body></html>""")
    db.close()


class GetUserURLsHandler(webapp2.RequestHandler):

  def get(self, twitter_handle):
    logging.info("twitter_handle: %s", twitter_handle)
    # Get a list of the top URLs in the table.
    if (os.getenv('SERVER_SOFTWARE') and
        os.getenv('SERVER_SOFTWARE').startswith('Google App Engine/')):
        db = MySQLdb.connect(unix_socket='/cloudsql/' + _INSTANCE_NAME, db='fortunatepun', user='root')
    else:
        # db = MySQLdb.connect(host='127.0.0.1', port=3306, user='root')
        # Alternately, connect to a Google Cloud SQL instance using:
        db = MySQLdb.connect(host='173.194.109.208', port=3306, db='fortunatepun', 
                             user='root', passwd='thatspunny' )

    cursor = db.cursor()

    sql = ('SELECT expanded_url, title, count(DISTINCT(twitter_handle)) as votes, group_concat( DISTINCT twitter_handle ) as tweeters, group_concat( DISTINCT tweetid ) as tweetids '
            'FROM URLer JOIN URL USING(urlid) '
            'WHERE twitter_id = (select twitter_id FROM tokens WHERE twitter_handle = \'{0}\') '
            'AND expanded_url IS NOT NULL '
            'AND tweet_time >= now() - INTERVAL 1 DAY '
            'AND twitter_handle != \'lastwhale\' '
            'GROUP BY 1,2 '
            'ORDER BY count(DISTINCT(twitter_handle)) DESC LIMIT 50;' ).format( twitter_handle )

    logging.info( sql )

    cursor.execute( sql )

    urllist = []
    for row in cursor.fetchall():
      logging.info( 'row: %s', row )

      title = row[1]
      if not row[1]:
        title = row[0]

      tweeters = row[3].split(',')
      tweetids = row[4].split(',')

      handle_to_id = [(tweeters[i], tweetids[i]) for i in range(len(tweeters))]

      temp_dict = dict([  ('url',   row[0] ),
                          ('votes', row[2] ),
                          ('title', title ),
                          ('tweeters', row[3]),
                          ('tweetids', row[4]),
                          ('handle_to_id', handle_to_id)
                             ])

      logging.info("dict:%s", temp_dict)
      urllist.append(temp_dict)

    if not urllist:
      variables = { 'twitter_handle': twitter_handle }
      template = JINJA_ENVIRONMENT.get_template('nourls.html')
    else:
      variables = { 'urllist': urllist,
                    'twitter_handle': twitter_handle }
      template = JINJA_ENVIRONMENT.get_template('urls.html')

    self.response.write(template.render(variables))
    db.close()


class HourlyTopTweetHandler(webapp2.RequestHandler):

  def get(self):
    if (os.getenv('SERVER_SOFTWARE') and
        os.getenv('SERVER_SOFTWARE').startswith('Google App Engine/')):
        db = MySQLdb.connect(unix_socket='/cloudsql/' + _INSTANCE_NAME, db='fortunatepun', user='root')
    else:
        # db = MySQLdb.connect(host='127.0.0.1', port=3306, user='root')
        # Alternately, connect to a Google Cloud SQL instance using:
        db = MySQLdb.connect(host='173.194.109.208', port=3306, db='fortunatepun', 
                             user='root', passwd='thatspunny' )

    cursor = db.cursor()
 
    sql = ( 'SELECT expanded_url, title, count(DISTINCT(twitter_handle)) as votes, group_concat( DISTINCT twitter_handle ) as tweeters '
            'FROM URLer JOIN URL USING(urlid) '
            'WHERE expanded_url IS NOT NULL '
            'AND tweet_time >= now() - INTERVAL 1 DAY '
            'AND twitter_handle != \'lastwhale\' '
            'GROUP BY 1,2 '
            'ORDER BY count(DISTINCT(twitter_handle)) DESC LIMIT 1;' )

    cursor.execute( sql )
    db.close()
    top_row = None
    for row in cursor.fetchall():
      logging.info( 'row: %s', row )
      top_row = row

    title = top_row[2]
    if not top_row[2]:
      title = top_row[1]

    consumer_key = '4w0zWZKRqt8vQJbmYfeQ'
    consumer_secret = 'NS6ZcUKGaaQx9k3lQekxzHQp7e6vZrnVf3OFas'
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    key = '2311401133-C5mKacui80u9QOmIeIFa8FoCmr7cWwVnthZMYgH'
    secret = 'eXUpfDg4iMtVFlR9hE4Tlvp48aY7u7noHxKmfRzGam03y'
    auth.set_access_token(key, secret)

    api = tweepy.API(auth)
    new_tweet = 'Top URL: ' + top_row[1] + ' ' + title
    api.update_status(new_tweet)


class RedirectUserHandler(webapp2.RequestHandler):

  def post(self):
    redirect_str = '/'
    twitter_handle = self.request.get('twitter_handle')
    if twitter_handle:
      redirect_str = '/t/' + twitter_handle

    self.redirect(redirect_str)


class URLExpanderHandler(webapp2.RequestHandler):

  def clean_urlfetch_result(self, result, row):
    if (os.getenv('SERVER_SOFTWARE') and
        os.getenv('SERVER_SOFTWARE').startswith('Google App Engine/')):
        db = MySQLdb.connect(unix_socket='/cloudsql/' + _INSTANCE_NAME, db='fortunatepun', user='root')
    else:
        # db = MySQLdb.connect(host='127.0.0.1', port=3306, user='root')
        # Alternately, connect to a Google Cloud SQL instance using:
        db = MySQLdb.connect(host='173.194.109.208', port=3306, db='fortunatepun', 
                             user='root', passwd='thatspunny' )

    cursor = db.cursor()

    logging.info("row: %s", row)
    logging.info("result: %s", result)
    logging.info("dir result: %s", dir(result))

    try:
      expanded_url = row[1] # the url
      try:
        expanded_url = result.geturl()
        for bad_end in ['.pdf', '.gif']:
          if bad_end in expanded_url:
            logging.info("pdf or gif -- bad")
            return False
      except:
        pass
      logging.info("expanded_url: %s", expanded_url)
      try:
        soup = BeautifulSoup(result.read())
        title = soup.title.string
        logging.info("title: %s", title)
        title = cgi.escape(title)
        logging.info("title: %s", title)
      except Exception as e:
        logging.warning("Exception: %s", e)
        title = None

      fail = False
      if expanded_url and title:
        try:
          cursor.execute('''UPDATE URL SET expanded_url='{0}', title='{1}' WHERE urlid = {2}'''.format(expanded_url, title, row[0]))
        except Exception as e:
          logging.error("e: %s", e)
          fail = True
      elif expanded_url:
        cursor.execute('''UPDATE URL SET expanded_url='{0}' WHERE urlid = {1}'''.format(expanded_url, row[0]))

      if fail:
        if expanded_url:
          cursor.execute('''UPDATE URL SET expanded_url='{0}' WHERE urlid = {1}'''.format(expanded_url, row[0]))

      db.commit()
      db.close()

    except Exception as e:
      logging.error("e: %s", e)
      return False

    return True

  def mark_bad_row(self, row):
    if (os.getenv('SERVER_SOFTWARE') and
        os.getenv('SERVER_SOFTWARE').startswith('Google App Engine/')):
        db = MySQLdb.connect(unix_socket='/cloudsql/' + _INSTANCE_NAME, db='fortunatepun', user='root')
    else:
        # db = MySQLdb.connect(host='127.0.0.1', port=3306, user='root')
        # Alternately, connect to a Google Cloud SQL instance using:
        db = MySQLdb.connect(host='173.194.109.208', port=3306, db='fortunatepun', 
                             user='root', passwd='thatspunny' )

    cursor = db.cursor()

    try:
      cursor.execute('''UPDATE URL SET unexpandable={0} WHERE urlid = {1}'''.format(1, row[0]))      
      db.commit()
      db.close()
    except Exception as e:
      logging.error("e: %s", e)

    return


  def get(self):
    if (os.getenv('SERVER_SOFTWARE') and
        os.getenv('SERVER_SOFTWARE').startswith('Google App Engine/')):
        db = MySQLdb.connect(unix_socket='/cloudsql/' + _INSTANCE_NAME, db='fortunatepun', user='root')
    else:
        # db = MySQLdb.connect(host='127.0.0.1', port=3306, user='root')
        # Alternately, connect to a Google Cloud SQL instance using:
        db = MySQLdb.connect(host='173.194.109.208', port=3306, db='fortunatepun', 
                             user='root', passwd='thatspunny' )

    cursor = db.cursor()
    cursor.execute('SELECT * from URL WHERE expanded_url is NULL AND unexpandable = 0')
    bad_rows = []
    for row in cursor.fetchall():
      result = None
      try:
        logging.info( 'row: %s', row )
        if '.pdf' in row[2]:
          bad_rows.append(row)
          continue

        if '.gif' in row[2]:
          bad_rows.append(row)
          continue

        try:
          result = urllib2.urlopen(row[1])
          logging.info("result: %s", result)
          cleaned = self.clean_urlfetch_result(result, row)
          logging.info("cleaned: %s", cleaned)
          if not cleaned:
            bad_rows.append(row)
          else:
            logging.warning("Problem with row. Will mark bad. Row: %s", row)
            bad_rows.append(row)
        except Exception as e:
            logging.warning("Bad row: %s. e:%s", row, e)
            bad_rows.append(row)

      except Exception as e:
        logging.warning("Bad row. Will mark bad. e: %s. . row: %s", e, row)
        bad_rows.append(row)

    db.close()

    for bad in bad_rows:
      try:
        self.mark_bad_row(bad)
      except Exception as e:
        logging.error("e: %s", e)


application = webapp2.WSGIApplication([('/', MainPage),
                ('/sign', Guestbook),
                ('/tasks/getalluserstweets', GetAllUsersTweetsHandler),
                ('/tasks/urlexpander', URLExpanderHandler),
                ('/tasks/tweettoplink', HourlyTopTweetHandler),
                ('/redirectuser', RedirectUserHandler),
                ('/t/(.+)', GetUserURLsHandler)],
                debug=True)

def main():

    run_wsgi_app(application)

if __name__ == "__main__":
    main()
