# -*- coding: utf-8 -*-

# TODO: Most of this settings should be stored in database
# rather than hardcoded, for now simplicity matter.

import os

DEBUG  = False

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), 'templates/')
STATIC_URL = '/static/'

PAGINATION_LIMIT = 2

APP_DOMAIN = 'http://www.bokerface.com'

SITE_TITLE = u'Boker Face • ini expresi gue, mana expresi loe'
SITE_DESCRIPTION = u'Ga harus perfect untuk bisa menjadi star idol, Kamu pun bisa. Ini expresi BF gue, mana expresi BF loe?'

IMAGE_SIZES = {
    'post': [620, 620],
    'winner': [300, 100],
}

TZ_OFFSET = +8 # WITA from UTC

# Facebook App related settings
# Long lived access token

FACEBOOK_APP_ID = '496912247033162'
FACEBOOK_APP_SECRET = '825d7cab759f02c098445bc2b0eede9e'

ADMIN_ACCESS_TOKEN = 'AAAHD8GX4DUoBAL5MV8OaA5ZACC4Ltt9Q20WB8yLQ7caA8bTEQQCsK57YYyJVfLiREZCr9XKYo3WJxajL6LmjpDly8Q9Q4rFAtGovJCZCwZDZD'
PAGE_ACCESS_TOKEN = 'AAAHD8GX4DUoBAKuzZBsrZAq08dZCn1xSK8Fe4ciHY1b0lZBf7hAoo3ZCkweQRiH3Dz9GarVTMD3J9JNSaVAldT7LNZCUBtkq0lPMGX6ZBIMcpzXdM0cpb5a'
TIMELINE_ALBUM_ID = '163850820438671'