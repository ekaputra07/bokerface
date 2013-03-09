from webapp2_extras.routes import RedirectRoute as R

from controllers import *

url_patterns = [
    R('/', HomeHandler, name='home'),
    R('/logout', LogoutHandler, name='logout', strict_slash=True),
    R('/about', AboutHandler, name='about', strict_slash=True),
    R('/boker', BokerHandler, name='boker', strict_slash=True),
    R('/boker/<boker_id>', BokerViewHandler, name='boker_view', strict_slash=True),
    R('/images/<photo_id>', ImageHandler, name='photo_view', strict_slash=True),
    R('/streams', StreamHandler, name='stream', strict_slash=True),
]