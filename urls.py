from webapp2_extras.routes import RedirectRoute as R

from controllers import *

url_patterns = [
    R('/', HomeHandler, name='home'),
    R('/logout', LogoutHandler, name='logout', strict_slash=True),
    R('/about', AboutHandler, name='about', strict_slash=True),
    R('/upload', UploadHandler, name='upload', strict_slash=True),
    R('/photo', PhotoHandler, name='photo', strict_slash=True),
]