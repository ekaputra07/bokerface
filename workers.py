import logging
import urllib2

from libs import facebook

import settings
from utils import encode_url
from models import User, Boker, Like, AdminSetting



def post_user_wall(access_token, message, attachment={}):
    """ Post new boker to userwall wall"""

    if not settings.DEBUG:
        graph = facebook.GraphAPI(access_token)
        graph.put_wall_post(message, attachment)
    else:
        logging.info('Runtask: post_user_wall...')


def publish_upload_action(access_token, url, explicitly_shared=False):
    """publish upload photo story on wall"""

    if not settings.DEBUG:
        graph = facebook.GraphAPI(access_token)
        graph.request('me/bokerface:upload', 
                      post_args={'photo': url,
                                 'fb:explicitly_shared': str(explicitly_shared).lower()})
    else:
        logging.info('Runtask: post_upload_action...')


def publish_posts_action(access_token, url, explicitly_shared=False):
    """publish posting an object story"""

    if not settings.DEBUG:
        graph = facebook.GraphAPI(access_token)
        graph.request('me/og.posts',
                        post_args={'object': url, 'fb:explicitly_shared': str(explicitly_shared).lower()})
    else:
        logging.info('Runtask: post_posts_action...')


def publish_vote_action(access_token, url, explicitly_shared=False):
    """publish vote photo story on wall"""

    if not settings.DEBUG:
        graph = facebook.GraphAPI(access_token)
        graph.request('me/bokerface:vote',
                post_args={'photo': url,
                           'fb:explicitly_shared': str(explicitly_shared).lower()})
    else:
        logging.info('Runtask: post_vote_story...')


def post_page_photo(url, photo_key, message):
    """ Post new boker photo to Page wall"""

    if not settings.DEBUG:
        photo_url = "%s/images/%s" % (settings.APP_DOMAIN, photo_key)

        final_message = "%s\n%s\n\nApakah Anda lagi Boker hari ini? cekidot http://bokerface.com" % (
                        message, url)

        page_token = AdminSetting.get_setting('page_atl')
        graph = facebook.GraphAPI(page_token)

        # Post to page wall
        try:
            file = urllib2.urlopen(photo_url)
            graph.put_photo(file, message=final_message, 
                    album_id=settings.TIMELINE_ALBUM_ID)
        except Exception as e:
            print e
    else:
        logging.info('Runtask: post_page_photo...')


def post_page_video(url, message):
    """ Post new boker Video to Page wall"""

    if not settings.DEBUG:
        # video_image = 'http://img.youtube.com/vi/%s/hqdefault.jpg' % video_id
        # video_src = 'http://www.youtube.com/v/%s?version=3&amp;autohide=1' % video_id

        final_message = "%s\n%s" % (message, url)

        page_token = AdminSetting.get_setting('page_atl')
        graph = facebook.GraphAPI(page_token)

        # Post to page wall
        try:
            attachment = {
                "name": message,
                "link": url,
                "caption": settings.APP_DOMAIN,
                "description": settings.SITE_TITLE,
            }
            graph.put_wall_post(final_message, attachment)
        except Exception as e:
            print e
    else:
        logging.info('Runtask: post_page_video...')


def update_num_view(boker_key):
    """ Increment number of views each time boker detail page opened"""
    boker = Boker.get(boker_key)
    if boker:
        boker.num_view += 1
        boker.put()


def update_num_comment(action, boker_key, current_user):
    """ Update number of comment per Boker """

    boker = Boker.get(boker_key)
    if boker:
        if action=='inc_comment':
            boker.num_comment += 1
            boker.put()

            # Notify Boker owner
            notify_user = True
            if current_user:
                if current_user['id'] == boker.user.id:
                    notify_user = False

            if notify_user and not settings.DEBUG:
                try:
                    boker_url = encode_url("/boker/%s" % boker.key().id())
                    graph = facebook.GraphAPI(settings.FACEBOOK_APP_ACCESS_TOKEN)
                    graph.request('%s/notifications' % boker.user.id,
                                   post_args={
                                            'href': '?to='+boker_url,
                                            'template': 'Ada komentar baru untuk boker anda.',
                                            })
                except Exception as e:
                    print e
            else:
                logging.info('Runtask: notify new comment...')

        if action=='dec_comment':
            if boker.num_comment > 0:
                boker.num_comment -= 1
                boker.put()


def like_boker(user_key, boker_key, explicitly_shared=False):
    """Like a boker"""

    user = User.get_by_key_name(user_key)
    boker = Boker.get(boker_key)
    boker_owner = boker.user

    if user and boker and not Like.already_like(user, boker):
        # Create like
        like = Like(user=user, boker=boker)
        like.put()

        # Update like numbers
        boker.num_like += 1
        boker.put()

        if not settings.DEBUG:
            # Post to FB
            try:
                boker_url = "%s/boker/%s" % (settings.APP_DOMAIN, boker.key().id())
                graph = facebook.GraphAPI(user.access_token)
                graph.request('me/og.likes',
                        post_args={'object': boker_url, 'fb:explicitly_shared': str(explicitly_shared).lower()})
            except Exception as e:
                print e

            # Notify Boker owner
            if user != boker_owner:
                try:
                    boker_url = encode_url("/boker/%s" % boker.key().id())
                    graph = facebook.GraphAPI(settings.FACEBOOK_APP_ACCESS_TOKEN)
                    graph.request('%s/notifications' % boker_owner.id,
                                   post_args={
                                            'href': '?to=' + boker_url,
                                            'template': '@[%s] menyukai boker anda.' % user.id,
                                            })
                except Exception as e:
                    print e

        else:
            logging.info('Runtask: post_like_story...')