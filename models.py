from google.appengine.ext import db

class User(db.Model):
    id = db.StringProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    updated = db.DateTimeProperty(auto_now=True)
    name = db.StringProperty(required=True)
    profile_url = db.StringProperty(required=True)
    access_token = db.StringProperty(required=True)


class Setting(db.Model):
    user = db.ReferenceProperty(User, collection_name='settings')
    name = db.StringProperty(required=True)
    value = db.StringProperty()


class Boker(db.Model):
    user = db.ReferenceProperty(User, collection_name='bokers')
    description = db.TextProperty(required=True)
    fb_image_id = db.IntegerProperty(required=True)