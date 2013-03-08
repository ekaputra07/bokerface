#!/usr/bin/env python

import webapp2
from webapp2_extras.routes import RedirectRoute as R
import urllib2
import facebook
import settings

from utils import BaseHandler

class HomeHandler(BaseHandler):
    template = 'index.html'
    def get(self):
        return self.render_response(self.template)


class PhotoHandler(BaseHandler):
    template = 'photo.html'
    def get(self):
        return self.render_response(self.template)


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

    def post(self):
        url = self.request.get('url')
        file = urllib2.urlopen(url)
        graph = facebook.GraphAPI(settings.PAGE_ACCESS_TOKEN)
        response = graph.put_photo(file, "Foto ini di posting dari bokerface.com, it works!", settings.FACEBOOK_ALBUM_ID)
        photo_url = ("http://www.facebook.com/photo.php?fbid={0}".format(response['id']))
        self.redirect(str(photo_url))



config = {}
config['webapp2_extras.sessions'] = dict(secret_key='')

app = webapp2.WSGIApplication(
    [
        R('/', HomeHandler, name='home'),
        R('/logout', LogoutHandler, name='logout', strict_slash=True),
        R('/about', AboutHandler, name='about', strict_slash=True),
        R('/upload', UploadHandler, name='upload', strict_slash=True),
        R('/photo', PhotoHandler, name='photo', strict_slash=True),
    ],
    debug=True,
    config=config
)
