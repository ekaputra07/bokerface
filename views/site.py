import urllib2, urllib, json

import webapp2
from google.appengine.api import images
from google.appengine.ext import deferred
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers

from libs import facebook

import settings
from utils import BaseHandler, crop_image
from templatetags import naturaltime, is_new
from models import User, Photo, Boker, Contest, Vote
from forms import ProfileForm
from workers import post_page_wall, post_vote_story, update_num_view, update_num_comment


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
    """Login page"""

    template = 'login.html'

    def get(self):
        if not self.current_user:
            msg = self.request.get('msg')
            return self.render_response(self.template, locals())
        else:
            next = self.request.get('next') or self.uri_for('home')
            self.redirect(next)


class LoginAdminHandler(BaseHandler):
    """Superadmin Login page"""

    template = 'login.html'

    def get(self):
        if not self.current_user:
            msg = self.request.get('msg')
            superadmin = True
            return self.render_response(self.template, locals())
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
        return self.render_response(self.template, {'page': 'about'})


class BokerViewHandler(BaseHandler):
    """ Single boker viewer"""

    template = 'photo.html'

    def get(self, boker_id):

        boker = Boker.get_by_id(int(boker_id))
        if boker:
            deferred.defer(update_num_view, str(boker.key()))
            
            active_contest = Contest.active_contest()
            if active_contest:
                is_nominee = Contest.is_nominee(boker)

            if self.current_user is not None:
                user = User.get_by_key_name(self.current_user['id'])
                can_vote = not Vote.already_vote(user, boker)
            else:
                can_vote = False
                
            querystring = self.request.GET
            return self.render_response(self.template, locals())
        else:
            self.abort(404)

    def post(self, boker_id):

        boker = Boker.get_by_id(int(boker_id))
        user = User.get_by_key_name(self.current_user['id'])
        if boker and user:
            # Avoid multi votes
            if not Vote.already_vote(user, boker):
                vote = Vote(contest=Contest.active_contest(), user=user, boker=boker)
                vote.put()

                # Trigger post action
                user_access_token = self.current_user['access_token']
                boker_url = settings.APP_DOMAIN + self.uri_for('boker_view', boker_id=boker_id)
                deferred.defer(post_vote_story, user_access_token, boker_url)

        self.redirect(self.uri_for('boker_view', boker_id=boker_id)+'?vote=1')


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

            explicit_share = self.request.get('explicit_share', False)
            photokey = self.request.get('photokey')
            desc = self.request.get('desc')

            photo = Photo.get(photokey)
            if photo and desc:
                # Save boker
                boker = Boker(user=user, photo=photo, description=desc)
                boker.put()
                # Set photo used
                photo.is_used = True
                photo.put()

                # Run task: Posting to page wall
                user_access_token = self.current_user['access_token']
                deferred.defer(post_page_wall, user_access_token, boker.key().id(), photokey, desc, explicit_share)

                self.redirect(self.uri_for('boker_view', boker_id=boker.key().id() ))
            else:
                return self.render_response(self.template, {
                            'errors': 'Photo dan Deskripsi harus diisi.',
                            'photokey': photokey,
                            'desc': desc,
                            })


class ContestListHandler(BaseHandler):
    """Display contest List"""

    template = 'contests.html'

    def get(self):
        page = 'contest'
        tab = self.request.get('tab', 'kontes')

        active_contest = Contest.active_contest()

        contests = Contest.all().order('-created')
        return self.render_response(self.template, locals())


class ContestSingleHandler(BaseHandler):
    """Display single contest detail"""

    template = 'contest.html'

    def get(self, contest_id):
        page = 'contest'
        contest = Contest.get_by_id(int(contest_id))
        if contest:
            if not contest.active:
                winners = Contest.get_winners(contest)
            return self.render_response(self.template, locals())
        self.abort(404)


class SettingHandler(BaseHandler):
    """ Settings Editor view"""

    login_required = True
    template = 'settings.html'

    def get(self):
        querystring = self.request.GET

        if self.request.get('tab') == 'profile' or not self.request.get('tab'):
            title = 'Profile Settings'
            tab = 'profile'

            user = User.get_by_key_name(self.current_user['id'])
            form = ProfileForm(self.session, instance=user)

        elif self.request.get('tab') == 'sharing':
            title = 'Sharing Settings'
            tab = 'sharing'

        return self.render_response(self.template, locals())

    def post(self):

        if self.request.get('tab') == 'profile' or not self.request.get('tab'):
            title = 'Profile Settings'
            tab = 'profile'

            user = User.get_by_key_name(self.current_user['id'])
            form = ProfileForm(self.session, self.request.POST, instance=user)

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


# ================== Below Parts is Ajax Action handler ======== #

class AjaxHandler(BaseHandler):

    def get(self):
        self.response.out.write('Invalid Request!.')

    def post(self):
        action = self.request.get('a')

        # Ajax comment count
        if action == 'inc_comment' or action == 'dec_comment':
            deferred.defer(update_num_comment, action, self.request.get('boker'))
        
        # Ajax vote
        if action == 'vote':
            deferred.defer(vote_boker, self.current_user['id'], self.request.get('boker'))

        self.response.out.write('ok')