import logging
import urllib2

import settings
from models import *
from libs import facebook



def post_user_wall(access_token, message, attachment={}):
    """ Post new boker to userwall wall"""

    if not settings.DEBUG:
        graph = facebook.GraphAPI(access_token)
        graph.put_wall_post(message, attachment)
    else:
        logging.info('Runtask: post_user_wall...')


def post_page_wall(access_token, boker_id, photo_key, message, **kwargs):
    """ Post new boker to Page wall"""

    if not settings.DEBUG:
        boker_url = "%s/boker/%s" % (settings.APP_DOMAIN, boker_id)
        photo_url = "%s/images/%s" % (settings.APP_DOMAIN, photo_key)

        final_message = "%s\n%s\n\nApakah Anda lagi Boker hari ini? cekidot http://bokerface.com" % (message, boker_url)

        graph = facebook.GraphAPI(settings.PAGE_ACCESS_TOKEN)

        # Post to page wall
        try:
            file = urllib2.urlopen(photo_url)
            graph.put_photo(file, message=final_message, album_id=settings.TIMELINE_ALBUM_ID)
        except:
            pass

        # Post to userwall
        attachment = {
            "name": message,
            "link": boker_url,
            "picture": photo_url,
            "description": 'Apakah Anda lagi Boker hari ini? cekidot http://bokerface.com',
        }
        try:
            post_user_wall(access_token, message, attachment)
        except:
            pass
    else:
        logging.info('Runtask: post_page_wall...')
