from datetime import date, datetime, timedelta

import webapp2
import jinja2
from webapp2_extras import sessions

from libs import facebook

import settings
from models import User

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(settings.TEMPLATES_DIR))


class BaseHandler(webapp2.RequestHandler):
    """Provides access to the active Facebook user in self.current_user

    The property is lazy-loaded on first access, using the cookie saved
    by the Facebook JavaScript SDK to determine the user ID of the active
    user. See http://developers.facebook.com/docs/authentication/ for
    more information.
    """

    @property
    def current_user(self):
        if settings.DEBUG:


            # Since we can't test real FB user on localhost
            # I made a fake account
            user = User.get_by_key_name('111')
            if not user:
                user = User(
                    key_name='111',
                    id='111',
                    name='Eka Putra',
                    profile_url='https://facebook.com/ekaputra07',
                    access_token='adadhkudghoiudaugfikafgiufsft87wt84rusgfugf8efgsu',
                )
                user.put()

            self.session['user'] = dict(
                name=user.name,
                profile_url=user.profile_url,
                id=user.id,
                access_token=user.access_token
            )
            return self.session.get('user');


        else:
            if self.session.get("user"):
                # User is logged in
                return self.session.get("user")
            else:
                # Either used just logged in or just saw the first page
                # We'll see here
                cookie = facebook.get_user_from_cookie(self.request.cookies,
                                                   settings.FACEBOOK_APP_ID,
                                                   settings.FACEBOOK_APP_SECRET
                                                   )
                if cookie:
                    # Okay so user logged in.
                    # Now, check to see if existing user
                    user = User.get_by_key_name(cookie["uid"])
                    if not user:
                        # Not an existing user so get user info
                        graph = facebook.GraphAPI(cookie["access_token"])
                        profile = graph.get_object("me")
                        user = User(
                            key_name=str(profile["id"]),
                            id=str(profile["id"]),
                            name=profile["name"],
                            profile_url=profile["link"],
                            access_token=cookie["access_token"]
                        )
                        user.put()
                    elif user.access_token != cookie["access_token"]:
                        user.access_token = cookie["access_token"]
                        user.put()
                    # User is now logged in
                    self.session["user"] = dict(
                        name=user.name,
                        profile_url=user.profile_url,
                        id=user.id,
                        access_token=user.access_token
                    )
                    return self.session.get("user")
            return None

    def dispatch(self):
        """
        This snippet of code is taken from the webapp2 framework documentation.
        See more at
        http://webapp-improved.appspot.com/api/webapp2_extras/sessions.html

        """
        self.session_store = sessions.get_store(request=self.request)
        try:
            webapp2.RequestHandler.dispatch(self)
        finally:
            self.session_store.save_sessions(self.response)

    @webapp2.cached_property
    def session(self):
        """
        This snippet of code is taken from the webapp2 framework documentation.
        See more at
        http://webapp-improved.appspot.com/api/webapp2_extras/sessions.html

        """
        return self.session_store.get_session()

    def render_response(self, tpl, context={}):
        """
        Wrapper function for rendering template and out put.
        tpl      : String -Template file name
        context  : Dict - Dictionary of data to render in template
        """
        print self.current_user
        
        #add default/global data to context
        default_data = {
            'STATIC_URL': settings.STATIC_URL,
            'user' : self.current_user,
            'fbapp_id': settings.FACEBOOK_APP_ID,
        }
        context.update(default_data)

        template = jinja_environment.get_template(tpl)
        self.response.out.write(template.render(context))



def naturaltime(value):
    """
    For date and time values shows how many seconds, minutes or hours ago
    compared to current timestamp returns representing string.

    This code snipets based on Django 1.4 Humanize tags.
    """
    if not isinstance(value, date): # datetime is a subclass of date
        return value

    now = datetime.now()

    delta = now - value
    if delta.seconds == 0:
        return 'Sekarang'
    elif delta.seconds < 60:
        return '%d detik yang lalu' % delta.seconds
    elif delta.seconds // 60 < 60:
        count = delta.seconds // 60
        return '%d menit yang lalu' % count
    elif delta.seconds // 60 // 60 < 24:
        count = delta.seconds // 60 // 60
        return '%d jam yang lalu' % count
    elif delta.seconds // 60 // 60 // 24 < 30:
        count = delta.seconds // 60 // 60 // 24
        return '%d hari yang lalu' % count
    else:
        count = delta.seconds // 60 // 60 // 24 // 30
        return '%d bulan yang lalu' % count

jinja_environment.filters['naturaltime'] = naturaltime


def is_new(value):
    """ Return 'baru' if posted under a hour ago"""

    if not isinstance(value, date): # datetime is a subclass of date
        return value

    now = datetime.now()
    delta = now - value
    if delta.seconds // 60 < 60:
        return '<span class="label label-success">baru</span>'
    return ''

jinja_environment.filters['is_new'] = is_new