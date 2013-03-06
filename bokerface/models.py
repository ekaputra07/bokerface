from google.appengine.ext import db

class Regency(db.Model):
    name = db.StringProperty(required=True)

class Station(db.Model):
    regency = db.ReferenceProperty(Regency, collection_name='stations')
    address = db.StringProperty()
    lat = db.StringProperty(required=True)
    long = db.StringProperty(required=True)
    picture = db.StringProperty()
