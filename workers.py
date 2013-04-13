import logging
import urllib2

import settings
from models import Boker
from libs import facebook


def post_user_wall(access_token, message, attachment={}):
    """ Post new boker to userwall wall"""

    if not settings.DEBUG:
        graph = facebook.GraphAPI(access_token)
        graph.put_wall_post(message, attachment)
    else:
        logging.info('Runtask: post_user_wall...')


def post_upload_story(access_token, url):
    """publish upload photo story on wall"""

    if not settings.DEBUG:
        graph = facebook.GraphAPI(access_token)
        graph.request('me/bokerface:upload', 
                post_args={'photo': url, 'fb:explicitly_shared': 'true'})
    else:
        logging.info('Runtask: post_upload_story...')


def post_vote_story(access_token, url):
    """publish vote photo story on wall"""

    if not settings.DEBUG:
        graph = facebook.GraphAPI(access_token)
        graph.request('me/bokerface:vote',
                post_args={'photo': url, 'fb:explicitly_shared': 'true'})
    else:
        logging.info('Runtask: post_vote_story...')



def post_page_wall(access_token, boker_id, photo_key, message, explicitly_shared):
    """ Post new boker to Page wall"""

    if not settings.DEBUG:
        boker_url = "%s/boker/%s" % (settings.APP_DOMAIN, boker_id)
        photo_url = "%s/images/%s" % (settings.APP_DOMAIN, photo_key)

        final_message = "%s\n%s\n\nApakah Anda lagi Boker hari ini? cekidot http://bokerface.com" % (
                        message, boker_url)

        graph = facebook.GraphAPI(settings.PAGE_ACCESS_TOKEN)

        # Post to page wall
        try:
            file = urllib2.urlopen(photo_url)
            graph.put_photo(file, message=final_message, 
                    album_id=settings.TIMELINE_ALBUM_ID)
        except:
            pass
            
        if explicitly_shared:
            try:
                post_upload_story(access_token, boker_url)
            except:
                pass

        # # Post to userwall
        # # will use this if upload story not approved by facebook
        # attachment = {
        #     "name": message,
        #     "link": boker_url,
        #     "picture": photo_url,
        #     "description": 'Apakah Anda lagi Boker hari ini? cekidot http://bokerface.com',
        # }
        # try:
        #     post_user_wall(access_token, message, attachment)
        # except:
        #     pass
    else:
        logging.info('Runtask: post_page_wall...')


def update_num_view(boker_key):
    """ Increment number of views each time boker detail page opened"""
    boker = Boker.get(boker_key)
    if boker:
        boker.num_view += 1
        boker.put()


def update_num_comment(action, boker_key):
    """ Update number of comment per Boker """

    boker = Boker.get(boker_key)
    if boker:
        if action=='inc_comment':
            boker.num_comment += 1
            boker.put()
        if action=='dec_comment':
            if boker.num_comment > 0:
                boker.num_comment -= 1
                boker.put()