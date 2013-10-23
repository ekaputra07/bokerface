# -*- coding: utf-8 -*-

import os

DEBUG  = False

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
FACEBOOK_APP_NAME = 'Boker'
FACEBOOK_APP_ID = ''
FACEBOOK_APP_SECRET = ''
FACEBOOK_APP_ACCESS_TOKEN = ''

TIMELINE_ALBUM_ID = ''


try:
	from local_settings import *
except ImportError:
	pass

