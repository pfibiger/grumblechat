from google.appengine.ext import db
from google.appengine.ext import blobstore
from datetime import datetime


__all__ = ['Account', 'Room', 'Room_visibility_names', 'Room_visibility_codes', 'RoomList', 'Message_event_names', 'Message_event_codes', 'Message', 'FileInfo']


class Account(db.Model):
    user = db.UserProperty(required=True)
    nickname = db.StringProperty(required=True)
    url = db.StringProperty(default='')
    gravatar_tag = db.StringProperty(default='')    

Room_visibility_names = {
    0: 'public',
    1: 'hidden',
    2: 'private',
    }
Room_visibility_codes = dict([(v, k) for (k, v) in Room_visibility_names.items()])
class Room(db.Model):
    name = db.StringProperty(required=True)
    topic = db.StringProperty(default='')
    visibility = db.IntegerProperty(required=False, choices=Room_visibility_codes.values())


class RoomList(db.Model):
    account = db.ReferenceProperty(reference_class=Account, required=True)
    room = db.ReferenceProperty(reference_class=Room, required=True)
    status = db.StringProperty(default='')
    last_seen = db.DateTimeProperty(auto_now_add=True, required=True)
    status = db.StringProperty( default = '' )
    status_start = db.DateTimeProperty()

    def update_presence(self):
        self.last_seen = datetime.now()
        self.put()


Message_event_names = {
    0: 'message',
    1: 'topic',
    2: 'join',
    3: 'part',
    4: 'action',
    5: 'status',
    6: 'upload',
    }
Message_event_codes = dict([(v, k) for (k, v) in Message_event_names.items()])
class Message(db.Model):
    sender = db.ReferenceProperty(reference_class=Account, required=True)
    room = db.ReferenceProperty(reference_class=Room, required=True)
    timestamp = db.DateTimeProperty(auto_now_add=True, required=True)
    event = db.IntegerProperty(required=True, choices=Message_event_codes.values())
    content = db.TextProperty()
    extra = db.StringProperty()
    
class FileInfo(db.Model):
    blob = blobstore.BlobReferenceProperty(required=True)
    uploaded_by = db.UserProperty(required=True)
    uploaded_at = db.DateTimeProperty(required=True, auto_now_add=True)
    filename = db.StringProperty(required=True)
  