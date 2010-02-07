from google.appengine.ext import db


class Account(db.Model):
    user = db.UserProperty(required=True)
    nickname = db.StringProperty(required=True)
    gravatar_tag = db.StringProperty(default='')


class Room(db.Model):
    name = db.StringProperty(required=True)
    topic = db.StringProperty(default='')

class RoomList(db.Model):
    account = db.ReferenceProperty(reference_class=Account, required=True)
    room = db.ReferenceProperty(reference_class=Room, required=True)
    status = db.StringProperty(default='')

class Message(db.Model):
    sender = db.ReferenceProperty(reference_class=Account, required=True)
    room = db.ReferenceProperty(reference_class=Room, required=True)
    timestamp = db.DateTimeProperty(auto_now_add=True, required=True)
    content = db.StringProperty(required=True)
    
