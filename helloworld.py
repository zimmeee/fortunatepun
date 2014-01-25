import cgi
import webapp2
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import urlfetch

import MySQLdb
import os
import jinja2

import logging

import BeautifulSoup



# Configure the Jinja2 environment.
JINJA_ENVIRONMENT = jinja2.Environment(
  loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
  autoescape=True,
  extensions=['jinja2.ext.autoescape'])

# Define your production Cloud SQL instance information.
_INSTANCE_NAME = 'fortunatepun:datastore'

class MainPage(webapp2.RequestHandler):
    def get(self):
        logging.info("request!")
        # Display existing guestbook entries and a form to add new entries.
        if (os.getenv('SERVER_SOFTWARE') and
            os.getenv('SERVER_SOFTWARE').startswith('Google App Engine/')):
            db = MySQLdb.connect(unix_socket='/cloudsql/' + _INSTANCE_NAME, db='guestbook', user='root')
        else:
            # db = MySQLdb.connect(host='127.0.0.1', port=3306, user='root')
            # Alternately, connect to a Google Cloud SQL instance using:
            db = MySQLdb.connect(host='173.194.109.208', port=3306, db='guestbook', user='root', passwd='thatspunny' )

        cursor = db.cursor()
        cursor.execute('SELECT guestName, content, entryID FROM entries')

        # Create a list of guestbook entries to render with the HTML.
        guestlist = [];
        for row in cursor.fetchall():
          guestlist.append(dict([('name',cgi.escape(row[0])),
                                 ('message',cgi.escape(row[1])),
                                 ('ID',row[2])
                                 ]))

        variables = {'guestlist': guestlist}
        template = JINJA_ENVIRONMENT.get_template('main.html')
        self.response.write(template.render(variables))
        db.close()

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
    query_string = '''SELECT urlid, url, count(*) as votes FROM URLer JOIN URL USING(urlid) WHERE twitter_id = (select twitter_id FROM tokens WHERE twitter_handle = '{0}') AND tweet_time < (NOW() - 24) AND expanded_url != NULL GROUP BY 1 ORDER BY 2 DESC;'''.format(twitter_handle)

    cursor.execute( query_string )

    urllist = [];
    for row in cursor.fetchall():
      logging.info( 'row: %s', row )
      urllist.append(dict([ ('urlid', row[0] ),
                            ('url',   row[1] ),
                            ('votes', row[2] )
                             ]))

    variables = { 'urllist': urllist,
                  'twitter_handle': twitter_handle }
    template = JINJA_ENVIRONMENT.get_template('urls.html')

    self.response.write(template.render(variables))
    db.close()


class URLExpanderHandler(webapp2.RequestHandler):

  def clean_urlfetch_result(self, result, cursor, row):

    try:
      logging.info("result: %s", dir(result))
      expanded_url = row[1] # the url
      try:
        expanded_url = result.final_url
      except:
        pass
      soup = BeautifulSoup(result)
      title = soup.title.string

      if expanded_url and title:
        cursor.execute('UPDATE URL SET expanded_url=%s, title=%s WHERE urlid = %s', expanded_url, title, row[0])

      elif expanded_url:
        cursor.execute('UPDATE URL SET expanded_url=%s WHERE urlid = %s', expanded_url, row[0])

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
    cursor.execute('SELECT * from URL WHERE expanded_url is NULL')
    for row in cursor.fetchall():
      try:
        logging.info( 'row: %s', row )
        result = urlfetch.fetch(row[1])
        if result.status_code == 200:
          self.clean_urlfetch_result(result, cursor, row)
        else:
          logging.error("Problem with row: %s", row)
      except Exception as e:
        logging.error("e: %s", e)

    db.close()




application = webapp2.WSGIApplication([('/', MainPage),
                ('/sign', Guestbook),
                ('/tasks/getalluserstweets', GetAllUsersTweetsHandler),
                ('/tasks/urlexpander', URLExpanderHandler),
                ('/t/(.+)', GetUserURLsHandler)],
                debug=True)

def main():

    run_wsgi_app(application)

if __name__ == "__main__":
    main()
