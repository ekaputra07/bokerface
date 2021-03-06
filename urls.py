from webapp2_extras.routes import RedirectRoute as R

from views.administration import AdminContestHandler, AdminContentHandler, AdminTokenHandler
from views.site import (HomeHandler, LoginHandler, LogoutHandler, LoginAdminHandler,
                        AboutHandler, BokerHandler, BokerViewHandler, ImageHandler,
                        SettingHandler, AjaxHandler, ContestListHandler, ContestSingleHandler,
                        UserHandler, FBCanvasHandler)
from views import api

url_patterns = [
    R('/', HomeHandler, name='home'),
    R('/login', LoginHandler, name='login', strict_slash=True),
    R('/login/superadmin', LoginAdminHandler, name='login_admin', strict_slash=True),
    R('/on_facebook/', FBCanvasHandler, name='onfb', strict_slash=True),
    R('/logout', LogoutHandler, name='logout', strict_slash=True),
    R('/about', AboutHandler, name='about', strict_slash=True),
    R('/boker', BokerHandler, name='boker', strict_slash=True),
    R('/boker/<boker_id>', BokerViewHandler, name='boker_view', strict_slash=True),
    R('/images/<photo_id>', ImageHandler, name='image', strict_slash=True),
    R('/settings', SettingHandler, name='settings', strict_slash=True),
    R('/ajax-action', AjaxHandler, name='ajax_handler', strict_slash=True),
    R('/api/streams', api.StreamHandler, name='streams', strict_slash=True),
    R('/kontes', ContestListHandler, name='contests', strict_slash=True),
    R('/kontes/<contest_id>', ContestSingleHandler, name='contest', strict_slash=True),

    R('/administration/contest', AdminContestHandler, name='admin_contest', strict_slash=True),
    R('/administration/content', AdminContentHandler, name='admin_content', strict_slash=True),
    R('/administration/regenerate_token', AdminTokenHandler, name='admin_token', strict_slash=True),

    R('/<username>', UserHandler, name='user', strict_slash=True),
]