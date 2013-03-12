#!/usr/bin/env python

# ----------------- Django ---------------------- #
# We need to put these line because we use djangoforms
# for form validation.
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
# ------------------------------------------------#

import webapp2
from urls import url_patterns
import settings

config = {}
config['webapp2_extras.sessions'] = dict(secret_key='')

app = webapp2.WSGIApplication(
    url_patterns,
    debug=settings.DEBUG,
    config=config
)