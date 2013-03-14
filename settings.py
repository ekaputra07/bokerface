import os

DEBUG = False

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), 'templates/')
STATIC_URL = '/static/'

PAGINATION_LIMIT = 2

APP_DOMAIN = 'http://www.bokerface.com/'
FACEBOOK_APP_ID = '496912247033162'
FACEBOOK_APP_SECRET = '825d7cab759f02c098445bc2b0eede9e'
PAGE_ACCESS_TOKEN = ''
FACEBOOK_ALBUM_ID = ''

IMAGE_SIZES = {
    'post': [620, 620],
    'thumb': [150, 150],
}