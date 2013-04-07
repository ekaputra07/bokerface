from datetime import date, datetime, timedelta
import time

import webapp2
from google.appengine.api import images

from utils import jinja_environment
import settings


def naturaltime(value):
    """
    For date and time values shows how many seconds, minutes or hours ago
    compared to current timestamp returns representing string.

    This code snipets based on Django 1.4 Humanize tags.
    """
    if not isinstance(value, date): # datetime is a subclass of date
        return value

    value =  value
    now =  datetime.utcnow()

    delta = now - value

    if delta.seconds == 0:
        return 'Sekarang'
    elif delta.seconds < 60:
        return '%d detik yang lalu' % delta.seconds
    elif delta.total_seconds() // 60 < 60:
        count = delta.total_seconds() // 60
        return '%d menit yang lalu' % count
    elif delta.total_seconds() // 60 // 60 < 24:
        count = delta.total_seconds() // 60 // 60
        return '%d jam yang lalu' % count
    elif delta.total_seconds() // 60 // 60 // 24 < 30:
        count = delta.total_seconds() // 60 // 60 // 24
        return '%d hari yang lalu' % count
    else:
        count = delta.total_seconds() // 60 // 60 // 24 // 30
        return '%d bulan yang lalu' % count

def is_new(value):
    """ Return 'baru' if posted under a hour ago"""

    if not isinstance(value, date): # datetime is a subclass of date
        return value

    now = datetime.now()
    delta = now - value
    if delta.seconds // 60 < 60:
        return '<span class="label label-success">baru</span>'
    return ''

def mytime(value):
    """ return current timezone time"""

    offset = timedelta(hours=settings.TZ_OFFSET)
    return value+offset

def formattime(value):
    """ Format the time"""

    if not isinstance(value, date):
        return value

    return value.strftime('%d %B %Y %H:%M:%S')

# Register custom filters and globals variable
jinja_environment.filters['naturaltime'] = naturaltime
jinja_environment.filters['is_new'] = is_new
jinja_environment.filters['mytime'] = mytime
jinja_environment.filters['formattime'] = formattime
jinja_environment.globals['file_serve'] = images.get_serving_url
jinja_environment.globals['uri_for'] = webapp2.uri_for