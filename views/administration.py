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
from models import Contest
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
