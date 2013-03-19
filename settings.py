import os

DEBUG  = False

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), 'templates/')
STATIC_URL = '/static/'

PAGINATION_LIMIT = 2

APP_DOMAIN = 'http://www.bokerface.com'
FACEBOOK_APP_ID = '496912247033162'
FACEBOOK_APP_SECRET = '825d7cab759f02c098445bc2b0eede9e'

# Long lived access token
ADMIN_ACCESS_TOKEN = 'AAAHD8GX4DUoBAMAbybbZAplZBloTXwOIAfN2ucoARxNyADNoIVFPynov8ZCPZBbvU5xL2NAkokY9l9NniigRh1vnGVfKReJyD7pZBuuUxmAZDZD'
PAGE_ACCESS_TOKEN = 'AAAHD8GX4DUoBAMMheXdSaFHEQ2jxGqzhxZA8phrVlf5FI3gyNopg6Y6pV4yzyRf1ZBH4ZCWHFxhCM4xBCZAm1PGhnoZCHDaDwNxap13Q4cRbo5tDXdtgH'
TIMELINE_ALBUM_ID = '163850820438671'

IMAGE_SIZES = {
    'post': [620, 620],
    'thumb': [150, 150],
}