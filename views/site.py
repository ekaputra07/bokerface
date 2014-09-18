import urllib2, urllib, json
import logging
logging.basicConfig(level=logging.INFO)

import webapp2
from google.appengine.api import images
from google.appengine.ext import deferred
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers

from libs import facebook

import settings
from utils import BaseHandler, crop_image, encode_url, decode_url
from templatetags import naturaltime, is_new
from models import User, Photo, Boker, Contest, Vote, Like
from forms import ProfileForm
from workers import (post_page_photo, post_page_video, publish_upload_action, publish_vote_action,
                     publish_posts_action, update_num_view, update_num_comment, like_boker)


class HomeHandler(BaseHandler):
    """ Homepage """

    template = 'index.html'

    def get(self):
        query = ''
        sort = self.request.get('top')
        if sort:
            query = 'sort='+sort
        return self.render_response(self.template, locals())

    def post(self):
        to = self.request.get('to', encode_url('/'))
        # self.redirect(self.uri_for('onfb') + '?next=' + to)
        self.redirect(decode_url(to))


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
        ispop = self.request.get('pop') == '1'
        if ispop:
            self.template = 'login_pop.html'

        if not self.current_user:
            msg = self.request.get('msg')
            return self.render_response(self.template, locals())
        else:
            next = self.request.get('next') or self.uri_for('home')
            if ispop:
                self.response.out.write(u'<script type="text/javascript">window.parent.window.location.href="/";</script>')
            else:
                self.redirect(str(next))


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


class FBCanvasHandler(BaseHandler):
    """FB Canvas page"""

    def get(self):
        next = self.request.get('next')
        redirect_uri = settings.APP_DOMAIN + self.uri_for('onfb') + '?next='+ next

        error = self.request.get('error')
        code = self.request.get('code')

        # If error on login
        if error:
            self.response.out.write('Anda gagal login ke Bokerface.com.')

        # If code received
        elif code:
            try:
                token = facebook.get_access_token_from_code(code, redirect_uri,
                                                            settings.FACEBOOK_APP_ID,
                                                            settings.FACEBOOK_APP_SECRET)
            except facebook.GraphAPIError as e:
                self.response.out.write(e)
            else:
                access_token = token['access_token']
                # Get user profile
                graph = facebook.GraphAPI(access_token)
                profile = graph.get_object('me')

                uid = profile.get('id')
                user = User.get_by_key_name(uid)

                # Update already user access-token
                if user:
                    if user.access_token != access_token:
                        user.access_token = access_token
                        user.put()

                # Create new user
                else:
                    user = User(
                        key_name = str(profile['id']),
                        id = str(profile['id']),
                        username = 'user%s' % str(profile['id'])[-4:],
                        name = profile['name'],
                        profile_url = profile['link'],
                        access_token = access_token
                    )
                    user.put()

                # Save user to session 
                self.session['user'] = dict(
                    username=user.username,
                    name=user.name,
                    profile_url=user.profile_url,
                    id=user.id,
                    access_token=user.access_token,
                    is_admin=user.is_admin,
                )

                self.redirect(decode_url(next))

        # Default action, authorize app
        else:
            fbauth_url = u'https://www.facebook.com/dialog/oauth?client_id=%s&scope=publish_actions&redirect_uri=%s' % (
                settings.FACEBOOK_APP_ID, redirect_uri
                )
            self.redirect(str(fbauth_url))


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

            # Check post type, Video or Photo
            if boker.video_id and boker.video_source:
                self.template = 'video.html'
                if self.current_user is not None:
                    user = User.get_by_key_name(self.current_user['id'])
                    can_like = not Like.already_like(user, boker)
                else:
                    can_like = False
            else:
                active_contest = Contest.active_contest()
                if active_contest:
                    is_nominee = Contest.is_nominee(boker)

                if self.current_user is not None:
                    user = User.get_by_key_name(self.current_user['id'])
                    can_vote = not Vote.already_vote(user)
                    can_like = not Like.already_like(user, boker)
                else:
                    can_vote = False
                    can_like = False
                    
                querystring = self.request.GET

            return self.render_response(self.template, locals())
        else:
            self.abort(404)

    def post(self, boker_id):
        action = self.request.get('action')
        boker = Boker.get_by_id(int(boker_id))
        user = User.get_by_key_name(self.current_user['id'])

        if boker and user and action == 'vote':
            # Avoid multi votes
            if not Vote.already_vote(user):
                vote = Vote(contest=Contest.active_contest(), user=user, boker=boker)
                vote.put()

                # Upate boker vote score
                boker.num_vote += 1
                boker.save()

                # Trigger post action
                user_access_token = self.current_user['access_token']
                boker_url = settings.APP_DOMAIN + self.uri_for('boker_view', boker_id=boker_id)
                deferred.defer(publish_vote_action, user_access_token, boker_url)

                self.redirect(self.uri_for('boker_view', boker_id=boker_id)+'?vote=1')
        self.redirect(self.uri_for('boker_view', boker_id=boker_id))
            

class BokerHandler(BaseHandler):
    """ Boker uploader view"""

    login_required = True
    template = 'boker.html'

    def get(self):
        if self.request.get('pop') == '1' and self.request.get('type') == 'photo':
            self.template = 'boker_pop.html'

        if self.request.get('pop') == '1' and self.request.get('type') == 'video':
            self.template = 'boker_video.html' 

        return self.render_response(self.template)


    def post(self):
        user = User.get_by_key_name(self.current_user['id'])

        #  action upload a photo
        if self.request.get('action') == 'upload':

            fd = self.request.get('photo')
            # ext = fd.file.name.split('.')[-1].lower()

            cropped, img = crop_image(fd, 'post', False)
            photo_blob = Photo.create_blob(img)

            extension = 'jpg' # if cropped==True else ext
            photo = Photo(user=user, file=photo_blob, extension=extension, is_used=False)
            photo.put()

            self.response.headers['Content-Type'] = 'application/json'
            self.response.out.write(json.dumps({'success': True, 'photo': str(photo.key())}))

        # Action create Photo post
        if self.request.get('action') == 'boker_photo':

            ispop = self.request.get('pop') == '1'
            if ispop:
                self.template = 'boker_pop.html'

            explicitly_shared = self.request.get('explicit_share', False)
            if explicitly_shared == 'on': explicitly_shared = True

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
                boker_url = "%s/boker/%s" % (settings.APP_DOMAIN, boker.key().id())
                user_access_token = self.current_user['access_token']

                # deferred.defer(post_page_photo, boker_url, photokey, desc)
                # deferred.defer(publish_upload_action, user_access_token, boker_url, explicitly_shared)
                deferred.defer(publish_posts_action, user_access_token, boker_url, explicitly_shared)

                boker_url = self.uri_for('boker_view', boker_id=boker.key().id())
                if ispop:
                    self.response.out.write(u'<script type="text/javascript">window.parent.window.location.href="%s";</script>' % boker_url);
                else:
                    self.redirect(boker_url)
            else:
                return self.render_response(self.template, {
                            'errors': 'Photo dan Ceritanya harus diisi.',
                            'photokey': photokey,
                            'desc': desc,
                            })

        # Action create Video Post
        if self.request.get('action') == 'boker_video':
            ispop = self.request.get('pop') == '1'
            if ispop:
                self.template = 'boker_video.html'

            explicitly_shared = self.request.get('explicit_share', False)
            if explicitly_shared == 'on': explicitly_shared = True

            video_url = self.request.get('video_url')
            video_id = self.request.get('video_id')
            video_source = self.request.get('video_source')
            desc = self.request.get('desc')

            if video_id and video_source and desc:
                boker = Boker(user=user, video_id=video_id, video_source=video_source, description=desc)
                boker.put()

                boker_url = "%s/boker/%s" % (settings.APP_DOMAIN, boker.key().id())
                user_access_token = self.current_user['access_token']

                # deferred.defer(post_page_video, boker_url, boker.description)
                deferred.defer(publish_posts_action, user_access_token, boker_url, explicitly_shared)

                boker_url = self.uri_for('boker_view', boker_id=boker.key().id())
                if ispop:
                    self.response.out.write(u'<script type="text/javascript">window.parent.window.location.href="%s";</script>' % boker_url);
                else:
                    self.redirect(boker_url)
            else:
                return self.render_response(self.template, {
                            'errors': 'Video dan Ceritanya harus diisi.',
                            'video_url': video_url,
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
                force_crop = self.request.get('crop', False)
                if force_crop: force_crop = True
                cropped, img = crop_image(photo.file, self.request.get('type'),
                                          strict=force_crop)
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
            deferred.defer(update_num_comment, action,
                           self.request.get('boker'), self.current_user)
        
        # Ajax vote
        if action == 'vote':
            deferred.defer(vote_boker, self.current_user['id'],
                           self.request.get('boker'))

        # Ajax like
        if action == 'like':
            user_key = self.current_user['id']
            deferred.defer(like_boker, user_key, self.request.get('boker'))

        self.response.out.write('ok')
