import urllib2, urllib, json
import webapp2
from google.appengine.api import images

from libs import facebook

import settings
from utils import BaseHandler
from models import *

class HomeHandler(BaseHandler):
    template = 'index.html'

    def get(self):
        bokers = Boker.all()
        bokers.order('-created')
        return self.render_response(self.template, {'bokers': bokers})


class LogoutHandler(BaseHandler):

    def get(self):
        if self.current_user is not None:
            self.session['user'] = None

        self.redirect('/')


class AboutHandler(BaseHandler):
    template = 'about.html'

    def get(self):
        return self.render_response(self.template)


class BokerViewHandler(BaseHandler):
    template = 'photo.html'

    def get(self, boker_id):
        boker = Boker.get_by_id(int(boker_id))
        if boker:
            return self.render_response(self.template, {'boker': boker})


class BokerHandler(BaseHandler):
    template = 'boker.html'

    def get(self):
        return self.render_response(self.template)

    def post(self):

        user = User.get_by_key_name(self.current_user['id'])

        #  action upload a photo
        if self.request.get('action') == 'upload':

            filename = self.request.get('photo')
            ext = filename.split('.')[-1].lower()

            fd = self.request.body
            photo_blob = Photo.create_blob(fd)

            photo = Photo(user=user, file=photo_blob, extension=ext, is_used=False)
            photo.put()

            self.response.headers['Content-Type'] = 'application/json'
            self.response.out.write(json.dumps({'success': True, 'photo': str(photo.key())}))

        # Action create post
        if self.request.get('action') == 'boker':

            photokey = self.request.get('photokey')
            desc = self.request.get('desc')

            photo = Photo.get(photokey)
            if photo and desc:
                boker = Boker(user=user, photo=photo, description=desc)
                boker.put()
                self.redirect(webapp2.uri_for('boker_view', boker_id=boker.key().id() ))
            else:
                return self.render_response(self.template, {
                            'errors': 'Photo dan Deskripsi harus diisi.',
                            'photokey': photokey,
                            'desc': desc,
                            }) 


class ImageHandler(BaseHandler):

    def get(self, photo_id):
        photo = Photo.get(photo_id)
        if photo:
            self.response.headers['Content-Type'] = str('image/%s' % photo.extension)

            if self.request.get('type') == 'home_thumb':
                img = images.Image(photo.file)

                if img.width > 620 or img.height > 620:
                    thumb = images.resize(photo.file, width=620, height=620)
                    self.response.out.write(thumb)

            self.response.out.write(photo.file)

        else:
            self.response.out.write('No image')

    def post(self, photo_id):
        if self.request.get('action') == 'delete':
            photo = Photo.get(photo_id)
            if photo:
                photo.delete()
        self.response.out.write('ok')