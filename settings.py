# -*- coding: utf-8 -*-

# TODO: Most of this settings should be stored in database
# rather than hardcoded, for now simplicity matter.

import os

DEBUG  = True

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), 'templates/')
STATIC_URL = '/static/'

PAGINATION_LIMIT = 10

APP_DOMAIN = 'http://www.bokerface.com'

SITE_TITLE = u'Boker Face • Apakah Anda lagi Boker hari ini?'
SITE_DESCRIPTION = u'Boker Face • Apakah Anda lagi Boker hari ini?'

IMAGE_SIZES = {
    'list': [270, 0],
    'post': [670, 0],
    'winner': [300, 100],
}

TZ_OFFSET = +8 # WITA from UTC

# Facebook App related settings
# Long lived access token

FACEBOOK_APP_NAME = 'Boker'
FACEBOOK_APP_ID = '496912247033162'
FACEBOOK_APP_SECRET = '825d7cab759f02c098445bc2b0eede9e'
FACEBOOK_APP_ACCESS_TOKEN = '496912247033162|q6JcxHVPY1QJ9bEDSEX5ww5VUJc'

TIMELINE_ALBUM_ID = '163850820438671'