from webapp2_extras.routes import RedirectRoute as R

from controllers import *

url_patterns = [
    R('/', HomeHandler, name='home'),
    R('/login', LoginHandler, name='login', strict_slash=True),
    R('/logout', LogoutHandler, name='logout', strict_slash=True),
    R('/about', AboutHandler, name='about', strict_slash=True),
    R('/boker', BokerHandler, name='boker', strict_slash=True),
    R('/boker/<boker_id>', BokerViewHandler, name='boker_view', strict_slash=True),
    R('/images/<photo_id>', ImageHandler, name='image', strict_slash=True),
    R('/streams', StreamHandler, name='streams', strict_slash=True),
    R('/settings', SettingHandler, name='settings', strict_slash=True),
    R('/<username>', UserHandler, name='user', strict_slash=True),
]