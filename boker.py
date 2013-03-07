#!/usr/bin/env python

import webapp2
import urllib2
import facebook

from utils import BaseHandler

class HomeHandler(BaseHandler):

    def get(self):
        return self.render_response('index.html')

    def post(self):
        url = self.request.get('url')
        file = urllib2.urlopen(url)
        graph = facebook.GraphAPI(self.current_user['access_token'])
        response = graph.put_photo(file, "Test Image")
        photo_url = ("http://www.facebook.com/"
                     "photo.php?fbid={0}".format(response['id']))
        self.redirect(str(photo_url))


class LogoutHandler(BaseHandler):

    def get(self):
        if self.current_user is not None:
            self.session['user'] = None

        self.redirect('/')


class AboutHandler(BaseHandler):
    template = 'about.html'

    def get(self):
        return self.render_response(self.template)


class UploadHandler(BaseHandler):
    template = 'upload.html'

    def get(self):
        return self.render_response(self.template)


config = {}
config['webapp2_extras.sessions'] = dict(secret_key='')

app = webapp2.WSGIApplication(
    [
        ('/', HomeHandler),
        ('/logout', LogoutHandler),
        ('/about', AboutHandler),
        ('/upload', UploadHandler),
    ],
    debug=True,
    config=config
)
