import urllib
import hashlib
import re
from datetime import datetime
from google.appengine.api import users

from models import *


__all__ = ['leave_room', 'gravatar', 'get_account', 'transform_message']


def leave_room(room=None, account=None, session=None):
    """
    Handles app logic for a user leaving a room.

    Must be passed *either* a Room and Account object, or a RoomList object.

    Examples
    --------
    leave_room(room=room_obj, account=account_obj)
    leave_room(session=roomlist_obj)
    """
    if room is not None and account is not None:
        session = RoomList.all().filter('room =', room).filter('account =', account).get()
    elif session is not None:
        room = session.room
        account = session.account
    else:
        raise TypeError("must specify either room and account, or session")

    # clean up the session record
    session.delete()

    # send a message to the room about the part
    timestamp = datetime.now()
    content = "leaving"
    message = Message(sender=account, room=room, timestamp=timestamp, content=content,
                      event=Message_event_codes['part'])
    message.put()


def gravatar(email):
    size=30
    rating='g'
    default_image='identicon'
    gravatar_url = "http://www.gravatar.com/avatar.php?"
    #gravatar_url += hashlib.md5(email).hexdigest()
    gravatar_url += urllib.urlencode({
        'gravatar_id':hashlib.md5(email).hexdigest(),
        's':str(size),
        'r':rating,
        'd':default_image})
    return """<img src="%s" alt="gravatar" />""" % gravatar_url


def get_account():
    user = users.get_current_user()
    account = Account.all().filter('user =', user).get()
    return account
    
def transform_message(message):
    content = message.content
    r="((?:https?)://[^ \t\n\r()\"']+)"
    m = re.search(r, content)
    if (m):
        url = m.group(1)
        #content=re.sub(r,r'<img src="\1">',content)
        #content=re.sub(r,r'<a href="\1">\1</a>',content)
        r="(?i)\.(jpg|png|gif)$"
        m = re.search(r,url)
        if (m):
            content = '<img class="embedded-image" src="' + url + '">'
        else:
            content = '<a href="' + url + '" target=”_blank”>' + url + '</a>'
    message.content = content
    return message
