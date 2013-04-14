from collections import Counter

from google.appengine.ext import db
from google.appengine.ext import blobstore


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
    def create_blob(cls, fd):
        return db.Blob(fd)


class Boker(db.Model):
    """Boker posts"""

    user = db.ReferenceProperty(User, collection_name='bokers')
    photo = db.ReferenceProperty(Photo, required=True, collection_name='photos')
    description = db.TextProperty()
    created = db.DateTimeProperty(auto_now_add=True)
    num_comment = db.IntegerProperty(default=0)
    num_view = db.IntegerProperty(default=0)
    num_like = db.IntegerProperty(default=0)


class Contest(db.Model):
    """Contest"""

    active = db.BooleanProperty(default=False)
    name = db.StringProperty(required=True)
    start = db.DateTimeProperty()
    end = db.DateTimeProperty(required=True)
    num_winners = db.IntegerProperty(default=1)
    description = db.TextProperty(required=True)
    reward = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    banner = blobstore.BlobReferenceProperty()

    @classmethod
    def active_contest(cls):
        return Contest.gql('WHERE active=:1', True).get()

    @classmethod
    def is_nominee(cls, boker):
        from templatetags import mytime
        active_contest = cls.active_contest()
        if mytime(boker.created) >= active_contest.start and \
                mytime(boker.created) <= active_contest.end:
            return True
        return False

    @classmethod
    def get_winners(cls, contest):
        votes_dict = {}
        votes = Vote.gql('WHERE contest=:1', contest)

        # Create votes based rank
        for v in votes:
            if v in votes_dict:
                votes_dict[v] += 1
            else:
                votes_dict[v] = 1

        ranked_votes = Counter(votes_dict).most_common()[:contest.num_winners]

        # TODO: Create created-date based rank if some boker have same amount 
        # of votes. who created earlier, it gets higer rank.
        return ranked_votes


class Vote(db.Model):
    """Votes"""

    contest = db.ReferenceProperty(Contest, collection_name='votes')
    user = db.ReferenceProperty(User, collection_name='votes')
    boker = db.ReferenceProperty(Boker, collection_name='votes')
    created = db.DateTimeProperty(auto_now_add=True)

    @classmethod
    def already_vote(cls, user, boker):
        result = Vote.gql('WHERE user=:1 AND contest=:2', user, 
                                        Contest.active_contest()).get()
        if result:
            return True
        return False


# TODO: This Settings & AdminSetting not yet implemented,the main purpose of
# this Model is to store user and Admin specific settings.

class Setting(db.Model):
    """User settings"""

    user = db.ReferenceProperty(User, collection_name='settings')
    name = db.StringProperty(required=True)
    value = db.TextProperty()

    @classmethod
    def get_setting_obj(self, user, name):
        return Setting.gql('WHERE user=:1 AND name=:2', user, name).get()
    
    @classmethod
    def get_setting(cls, user, name):
        setting = Setting.get_setting_obj(user, name)
        if setting:
            return setting.value
        return

    @classmethod
    def set_setting(cls, user, name, value):
        setting = Setting.get_setting_obj(user, name)
        if setting:
            setting.value = value
            setting.put()
        else:
            setting = Setting(user=user, name=name, value=value)
            setting.put()


class AdminSetting(db.Model):
    """Admin settings"""

    name = db.StringProperty(required=True)
    value = db.TextProperty()

    @classmethod
    def get_setting_obj(cls, name):
        return AdminSetting.gql('WHERE name=:1', name).get()

    @classmethod
    def get_setting(cls, name):
        setting = AdminSetting.get_setting_obj(name)
        if setting:
            return setting.value
        return

    @classmethod
    def set_setting(cls, name, value):
        setting = AdminSetting.get_setting_obj(name)
        if setting:
            setting.value = value
            setting.put()
        else:
            setting = AdminSetting(name=name, value=value)
            setting.put()