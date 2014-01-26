import cgi
import webapp2
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import urlfetch

import MySQLdb
import os
import jinja2

import logging


import tweepy
from BeautifulSoup import BeautifulSoup



# Configure the Jinja2 environment.
JINJA_ENVIRONMENT = jinja2.Environment(
  loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
  autoescape=True,
  extensions=['jinja2.ext.autoescape'])

# Define your production Cloud SQL instance information.
_INSTANCE_NAME = 'fortunatepun:datastore'

class MainPage(webapp2.RequestHandler):
    def get(self):
        logging.info("HOMEPAGE request!")
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('FORTUNATE PUN!!!!!!!!!!!!!!!!!!!!!')


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
    cursor.execute('SELECT twitter_id FROM tokens;')
    for row in cursor.fetchall():
      url = "http://fortunatepun.appspot.com/eatTweets?twitterId=" + str(row[0])
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
    # This query is broken
    # query_string = '''SELECT urlid, url, count(*) as votes, expanded_url, title FROM URLer JOIN URL USING(urlid) WHERE twitter_id = (select twitter_id FROM tokens WHERE twitter_handle = '{0}') AND DATE_SUB( tweet_time, INTERVAL 1 DAY) < tweet_time AND expanded_url IS NOT NULL GROUP BY urlid, url, expanded_url, title ORDER BY count(*) DESC;'''.format(twitter_handle)

    query_string = '''SELECT urlid, expanded_url, title, count(*) as votes, group_concat( DISTINCT twitter_handle ) as tweeters FROM URLer JOIN URL USING(urlid) WHERE twitter_id = (select twitter_id FROM tokens WHERE twitter_handle = '{0}') AND DATE_SUB( tweet_time, INTERVAL 1 DAY) < tweet_time AND expanded_url IS NOT NULL GROUP BY urlid, expanded_url, title ORDER BY count(*) DESC LIMIT 20;'''.format(twitter_handle)

    cursor.execute( query_string )

    urllist = []
    for row in cursor.fetchall():
      logging.info( 'row: %s', row )

      title = row[3]
      if not row[3]:
        title = row[2]

      temp_dict = dict([  ('urlid', row[0] ),
                          ('url',   row[1] ),
                          ('votes', row[2] ),
                          ('title', title ),
                          ('tweeters', row[4])
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
    # This query is broken
    # query_string = '''SELECT urlid, url, count(*) as votes, expanded_url, title FROM URLer JOIN URL USING(urlid) WHERE twitter_id = (select twitter_id FROM tokens WHERE twitter_handle = '{0}') AND DATE_SUB( tweet_time, INTERVAL 1 DAY) < tweet_time AND expanded_url IS NOT NULL GROUP BY urlid, url, expanded_url, title ORDER BY count(*) DESC;'''.format(twitter_handle)

    query_string = '''SELECT urlid, expanded_url, title, count(*) as votes, group_concat( DISTINCT twitter_handle ) as tweeters FROM URLer JOIN URL USING(urlid) WHERE DATE_SUB( tweet_time, INTERVAL 1 DAY) < tweet_time AND expanded_url IS NOT NULL GROUP BY urlid, expanded_url, title ORDER BY count(*) DESC LIMIT 1;'''

    cursor.execute( query_string )
    db.close()
    top_row = None
    for row in cursor.fetchall():
      logging.info( 'row: %s', row )
      top_row = row

    title = top_row[3]
    if not top_row[3]:
      title = top_row[2]

    consumer_key = '4w0zWZKRqt8vQJbmYfeQ'
    consumer_secret = 'NS6ZcUKGaaQx9k3lQekxzHQp7e6vZrnVf3OFas'
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    key = ''
    secret = '' 
    auth.set_access_token(key, secret)

    api = tweepy.API(auth)
    new_tweet = 'Top URL is: ' + title
    api.update_status(new_tweet)


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

    try:
      logging.info("result: %s", dir(result))
      expanded_url = row[1] # the url
      try:
        expanded_url = result.final_url
      except:
        pass
      logging.info("expanded_url: %s", expanded_url)
      logging.info("result.content: %s", result.content)

      try:
        soup = BeautifulSoup(result.content)
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
        except:
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

    return

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
      logging.info("row: %s", dir(row))
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
    for row in cursor.fetchall():
      try:
        logging.info( 'row: %s', row )
        result = urlfetch.fetch(row[1])
        if result.status_code == 200:
          self.clean_urlfetch_result(result, row)
        else:
          logging.error("Problem with row: %s", row)
          self.mark_bad_row(row)

      except Exception as e:
        logging.error("e: %s", e)

    db.close()


application = webapp2.WSGIApplication([('/', MainPage),
                ('/sign', Guestbook),
                ('/tasks/getalluserstweets', GetAllUsersTweetsHandler),
                ('/tasks/urlexpander', URLExpanderHandler),
                ('/tasks/tweettoplink', HourlyTopTweetHandler),
                ('/t/(.+)', GetUserURLsHandler)],
                debug=True)

def main():

    run_wsgi_app(application)

if __name__ == "__main__":
    main()
