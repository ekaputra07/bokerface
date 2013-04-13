#!/usr/bin/env python

import webapp2
from urls import url_patterns
import settings

config = {}
config['webapp2_extras.sessions'] = dict(secret_key='adwa&%*&!*#HOHIDHA())924903hda^&&&!#*)@@$_JF')

app = webapp2.WSGIApplication(
    url_patterns,
    debug=settings.DEBUG,
    config=config
)