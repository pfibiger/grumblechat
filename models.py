from google.appengine.ext import db


class Account(db.Model):
    user = db.UserProperty(required=True)
    nickname = db.StringProperty(required=True)
    url = db.StringProperty(default='')
    gravatar_tag = db.StringProperty(default='')


class Room(db.Model):
    name = db.StringProperty(required=True)
    topic = db.StringProperty(default='')

class RoomList(db.Model):
    account = db.ReferenceProperty(reference_class=Account, required=True)
    room = db.ReferenceProperty(reference_class=Room, required=True)
    status = db.StringProperty(default='')

Message_event_names = {
    0: 'message',
    1: 'topic',
    2: 'join',
    3: 'part',
    4: 'action',
    5: 'status',
    }
Message_event_codes = dict([(v, k) for (k, v) in Message_event_names.items()])
class Message(db.Model):
    sender = db.ReferenceProperty(reference_class=Account, required=True)
    room = db.ReferenceProperty(reference_class=Room, required=True)
    timestamp = db.DateTimeProperty(auto_now_add=True, required=True)
    event = db.IntegerProperty(required=True, choices=Message_event_codes.values())
    content = db.StringProperty(required=True)
