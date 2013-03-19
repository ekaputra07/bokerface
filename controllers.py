import urllib2, urllib, json

import webapp2
from google.appengine.api import images

from libs import facebook

import settings
from utils import BaseHandler, crop_image
from templatetags import naturaltime, is_new
from models import *
from forms import *


class HomeHandler(BaseHandler):
    """ Homepage """

    template = 'index.html'

    def get(self):
        return self.render_response(self.template)


class UserHandler(BaseHandler):
    """User profile page"""
    template = 'user.html'

    def get(self, username):
        user = User.gql("WHERE username=:1", username).get()
        if user:
            return self.render_response(self.template, locals())
        self.abort(404)


class LoginHandler(BaseHandler):
    """Login required page"""

    template = 'login_required.html'

    def get(self):
        if not self.current_user:
            return self.render_response(self.template)
        else:
            next = self.request.get('next') or self.uri_for('home')
            self.redirect(next)



class LogoutHandler(BaseHandler):
    """Logout"""

    def get(self):
        if self.current_user is not None:
            self.session['user'] = None

        self.redirect('/')


class AboutHandler(BaseHandler):
    """ About Us page"""

    template = 'about.html'

    def get(self):
        return self.render_response(self.template)


class BokerViewHandler(BaseHandler):
    """ Single boker viewer"""

    template = 'photo.html'

    def get(self, boker_id):

        boker = Boker.get_by_id(int(boker_id))
        if boker:
            return self.render_response(self.template, locals())
        else:
            self.abort(404)


class BokerHandler(BaseHandler):
    """ Boker uploader view"""

    login_required = True
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

            cropped, img = crop_image(fd, 'post', False)
            photo_blob = Photo.create_blob(img)

            extension = 'jpg' if cropped==True else ext
            photo = Photo(user=user, file=photo_blob, extension=extension, is_used=False)
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

                # graph = facebook.GraphAPI(settings.PAGE_ACCESS_TOKEN)
                # attachment = {
                #     "name": "Link name",
                #     "link": "http://www.example.com/",
                #     "caption": "{*actor*} posted a new review",
                #     "description": "This is a longer description of the attachment",
                #     "picture": "http://www.bokerface.com/images/ag9zfmJva2VyZmFjZS1hcHByDQsSBVBob3RvGNGMAQw",
                # }
                # graph.put_wall_post(desc, attachment)
                # file = urllib2.urlopen('http://www.bokerface.com/images/ag9zfmJva2VyZmFjZS1hcHByDQsSBVBob3RvGNGMAQw')

                boker_url = settings.APP_DOMAIN + self.uri_for('boker_view', boker_id=boker.key().id())
                message = "%s\n%s\n\nApakah Anda lagi Boker hari ini? cekidot http://bokerface.com" % (desc, boker_url)

                graph = facebook.GraphAPI(settings.PAGE_ACCESS_TOKEN)
                file = urllib2.urlopen(settings.APP_DOMAIN + self.uri_for('image', photo_id=photo.key()))
                graph.put_photo(file, message=message, album_id=settings.TIMELINE_ALBUM_ID)

                self.redirect(self.uri_for('boker_view', boker_id=boker.key().id() ))
            else:
                return self.render_response(self.template, {
                            'errors': 'Photo dan Deskripsi harus diisi.',
                            'photokey': photokey,
                            'desc': desc,
                            })


class SettingHandler(BaseHandler):
    """ Settings Editor view"""

    login_required = True
    template = 'settings.html'

    def get(self):
        querystring = self.request.GET

        if self.request.get('tab') == 'profile' or not self.request.get('tab'):
            title = 'Page Settings'
            tab = 'profile'

            user = User.get_by_key_name(self.current_user['id'])
            form = ProfileForm(instance=user)

        elif self.request.get('tab') == 'sharing':
            title = 'Sharing Settings'
            tab = 'sharing'

        return self.render_response(self.template, locals())

    def post(self):

        if self.request.get('tab') == 'profile' or not self.request.get('tab'):
            title = 'Page Settings'
            tab = 'profile'

            user = User.get_by_key_name(self.current_user['id'])
            form = ProfileForm(self.request.POST, instance=user)

            if form.is_valid():
                form.save()
                self.redirect(self.uri_for('settings')+'?tab=profile&success=1')

            return self.render_response(self.template, locals())

        elif self.request.get('tab') == 'sharing':
            pass


class ImageHandler(BaseHandler):
    """ Image server"""

    def get(self, photo_id):
        photo = Photo.get(photo_id)
        if photo:

            if self.request.get('type'):
                cropped, img = crop_image(photo.file, self.request.get('type'), True)
                if img:
                    self.response.headers['Content-Type'] = 'image/jpg'
                    self.response.out.write(img)
                else:
                    self.response.out.write('No image')

            self.response.headers['Content-Type'] = str('image/%s' % photo.extension)
            self.response.out.write(photo.file)

        else:
            self.response.out.write('No image')

    def post(self, photo_id):
        if self.request.get('action') == 'delete':
            photo = Photo.get(photo_id)
            if photo:
                photo.delete()
        self.response.out.write('ok')


# ================== Below Parts is Json Stream providers ======== #

class StreamHandler(BaseHandler):

    def _build_qs(self, qs={}):
        """Build querystring format from dictionary"""

        query = [('%s=%s' % (k, v)) for k, v in qs.iteritems()]
        return '&'.join(query)

    def get(self):

        qs = {}
        page = int(self.request.get('page') or 1)
        limit = int(self.request.get('limit') or settings.PAGINATION_LIMIT)
        bokers = Boker.all().order('-created')

        user_filter = self.request.get('username')

        if user_filter:
            qs['username'] = user_filter
            user = User.gql("WHERE username=:1", user_filter).get()
            bokers.filter('user =', user)


        # calculate number of pages
        total = bokers.count()
        num_pages = total // limit
        if total % limit > 0:
            num_pages += 1

        # Get objects
        offset = limit*(page-1)
        bokers = bokers.run(limit=limit, offset=offset)

        # Build objects dict's
        objects = []
        for b in bokers:

            data = {
                'user': {
                    'id': b.user.id,
                    'username': b.user.username,
                    'name': b.user.name,
                    'url': self.uri_for('user', username=b.user.username),
                },
                'photo': {
                    'key': str(b.photo.key()),
                },
                'created': naturaltime(b.created),
                'is_new': is_new(b.created),
                'description': b.description,
                'permalink': self.uri_for('boker_view', boker_id=b.key().id()),
            }

            objects.append(data)

        # metadata
        qs.update({'page': page+1})
        next_qs = self._build_qs(qs)

        qs.update({'page': page-1})
        previous_qs = self._build_qs(qs)

        meta = {
            'count': len(objects),
            'limit': limit,
            'page': page,
            'next_url': '%s?%s' % (self.uri_for('streams'), next_qs) if page < num_pages else None,
            'previous_url': '%s?%s' % (self.uri_for('streams'), previous_qs) if page > 1 else None,
            'pages': num_pages,
        }

        streams = dict(
            meta=meta,
            objects=objects,
        )

        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(json.dumps(streams))