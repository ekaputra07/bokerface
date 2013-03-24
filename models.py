from google.appengine.ext import db

class User(db.Model):
    """User account model"""

    id = db.StringProperty(required=True)
    profile_url = db.StringProperty(required=True)
    access_token = db.StringProperty(required=True)
    is_admin = db.BooleanProperty(default=False)

    username = db.StringProperty(required=True)
    name = db.StringProperty()
    avatar = db.BlobProperty()

    created = db.DateTimeProperty(auto_now_add=True)
    updated = db.DateTimeProperty(auto_now=True)


class Photo(db.Model):
    """Photos"""

    user = db.ReferenceProperty(User, collection_name='photos')
    file = db.BlobProperty(required=True)
    extension = db.StringProperty(required=True)
    is_used = db.BooleanProperty(default=False)
    uploaded = db.DateTimeProperty(auto_now_add=True)

    @classmethod
    def create_blob(self, fd):
        return db.Blob(fd)


class Boker(db.Model):
    """Boker posts"""

    user = db.ReferenceProperty(User, collection_name='bokers')
    photo = db.ReferenceProperty(Photo, required=True, collection_name='photos')
    description = db.TextProperty()
    created = db.DateTimeProperty(auto_now_add=True)


class Setting(db.Model):
    """User settings"""

    user = db.ReferenceProperty(User, collection_name='settings')
    name = db.StringProperty(required=True)
    value = db.StringProperty()
    
    @classmethod
    def get(self, u, n):
        return Setting.gql('WHERE name=:1 AND user=:2', n, u) or ''

    @classmethod
    def set(self, u, n, v):
        setting = Setting(user=u, name=n, value=v)
        setting.put()


class AdminSetting(db.Model):
    """Admin settings"""

    name = db.StringProperty(required=True)
    value = db.StringProperty()

    @classmethod
    def get(self, n):
        return AdminSetting.gql('WHERE name=:1', n) or ''

    @classmethod
    def set(self, n, v):
        setting = AdminSetting(name=n, value=v)
        setting.put()