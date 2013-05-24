import urllib2, urllib, json
import datetime

import webapp2
from google.appengine.ext import deferred
from google.appengine.ext import db
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers

from libs import facebook

import settings
from utils import BaseHandler
from models import Contest, AdminSetting
from forms import ContestForm, ContentForm


class AdminContestHandler(BaseHandler, blobstore_handlers.BlobstoreUploadHandler):
    template = 'admin_contest.html'

    login_required = True
    superadmin_required = True

    def get(self):
        contests = Contest.all().order('-created')
        querystring = self.request.GET
        today = datetime.datetime.now()

        c = self.request.get('c')
        if c:
            upload_url = blobstore.create_upload_url('/administration/contest?c='+c)
            try:
                ct = Contest.get(c)

                # Interrupt form when delete action available
                if self.request.get('action') == 'delete':
                    ct.delete()
                    self.redirect(self.uri_for('admin_contest')+'?success=2')

                form = ContestForm(instance=ct)
            except:
                form = ContestForm()
        else:
            upload_url = blobstore.create_upload_url('/administration/contest')
            form = ContestForm()

        return self.render_response(self.template, locals())

    def post(self):
        contests = Contest.all().order('-created')
        today = datetime.datetime.now()
        c = self.request.get('c')
        
        if c:
            upload_url = blobstore.create_upload_url('/administration/contest?c='+c)
            try:
                ct = Contest.get(c)
                form = ContestForm(self.request.POST, instance=ct)
            except:
                form = ContestForm(self.request.POST)
        else:
            upload_url = blobstore.create_upload_url('/administration/contest')
            form = ContestForm(self.request.POST)

        if form.is_valid():
            contest = form.save(commit=False)
            upload_files = self.get_uploads('file')
            if upload_files:
                contest.banner = upload_files[0]
            contest.put()

            self.redirect(self.uri_for('admin_contest')+'?success=1')

        return self.render_response(self.template, locals())


class AdminContentHandler(BaseHandler):
    template = 'admin_content.html'

    login_required = True
    superadmin_required = True

    def get(self):
        querystring = self.request.GET
        form = ContentForm()
        return self.render_response(self.template, locals())

    def post(self):
        form = ContentForm(self.request.POST)
        if form.is_valid():
            form.save()
            self.redirect(self.uri_for('admin_content')+'?success=1')
        return self.render_response(self.template, locals())


class AdminTokenHandler(BaseHandler):
    login_required = True
    superadmin_required = True

    def get(self):
        current_admin_AT = self.current_user['access_token']

        try:
            # Get long-lived admin access token
            og1 = facebook.GraphAPI(current_admin_AT)
            current_admin_ATL = og1.extend_access_token(settings.FACEBOOK_APP_ID,
                                                       settings.FACEBOOK_APP_SECRET)

            AdminSetting.set_setting('admin_at', current_admin_AT)
            AdminSetting.set_setting('admin_atl', current_admin_ATL.get('access_token'))

            # Get long-lived Page access token
            og2 = facebook.GraphAPI(current_admin_ATL.get('access_token'))
            accounts = og2.request('me/accounts')

            apps = accounts.get('data')
            for app in apps:
                if app.get('name') == settings.FACEBOOK_APP_NAME:
                    AdminSetting.set_setting('page_atl', app.get('access_token'))
                    break

            # Print the result
            self.response.out.write('Admin Token: %s\nAdmin Token L: %s\nPage Token: %s' % (
                AdminSetting.get_setting('admin_at'), AdminSetting.get_setting('admin_atl'), 
                AdminSetting.get_setting('page_atl')
                ))
        except Exception as e:
            self.response.out.write(e)



