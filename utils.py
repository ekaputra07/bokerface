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

    login_required = False

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
                    username='ekaputra07',
                    name='Eka Putra',
                    profile_url='https://facebook.com/ekaputra07',
                    access_token='adadhkudghoiudaugfikafgiufsft87wt84rusgfugf8efgsu',
                )
                user.put()

            self.session['user'] = dict(
                username=user.username,
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
                            key_name=str(profile['id']),
                            id=str(profile['id']),
                            username=profile['username'],
                            name=profile['name'],
                            profile_url=profile['link'],
                            access_token=cookie['access_token']
                        )
                        user.put()
                    elif user.access_token != cookie['access_token']:
                        user.access_token = cookie['access_token']
                        user.put()
                    # User is now logged in
                    self.session['user'] = dict(
                        username=user.username,
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

            # Check user login if required
            self.if_login_required()

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


    def if_login_required(self):
        """ Check if user need loggedin"""

        if self.login_required:
            if not self.current_user:
                # Redirect to login page
                self.redirect('%s?next=%s' % (self.uri_for('login'), self.request.path))
            # else:
            #     # Make use user have set their username before using
            #     # this app further more.
            #     user = User.get_by_key_name(self.current_user['id'])

            #     # To avoid infinite redirect on settings page, redirect will only run on
            #     # pages other than settings page.
            #     if not user.username and self.request.path != self.uri_for('settings'):
            #         self.redirect(self.uri_for('settings')+'?tab=profile&welcome=1')
        return

    def render_response(self, tpl, context={}):
        """
        Wrapper function for rendering template and output.
        tpl      : String -Template file name
        context  : Dict - Dictionary of data to render in template
        """
        
        #add default/global data to context
        default_data = {
            'STATIC_URL': settings.STATIC_URL,
            'current_user' : self.current_user,
            'fbapp_id': settings.FACEBOOK_APP_ID,
        }
        context.update(default_data)

        template = jinja_environment.get_template(tpl)
        self.response.out.write(template.render(context))