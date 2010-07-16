from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.db import Key
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app
from account import get_account
from datetime import datetime

from models import *


class RoomCollectionHandler(webapp.RequestHandler):

    def get(self):
        rooms = Room.all().order('name')
        self.response.out.write(template.render('templates/room_collection.html',
                                                {'rooms': rooms}
                                                ))

    def post(self):
        name = self.request.get('name')
        room = Room.all().filter('name =', name).get()
        if room:
            self.response.out.write(template.render('templates/room_collection.html',
                                                    {'error_msg': 'A room by that name already exists.',
                                                     'name': name}
                                                    ))
        else:
            room = Room(name=name)
            room.put()
            self.redirect('/room/' + str(room.key()))
            

class RoomHandler(webapp.RequestHandler):

    def get(self, room_key):
        room = Room.all().filter('__key__ =', Key(room_key)).get()
        if not room:
            # room doesn't exist
            self.error(404)
            self.response.out.write("no such room")
            return
        # return (up to) last 40 messages
        # FIXME should define '40' as a constant
        # need to enumerate query results to access last message below
        messages = [m for m in reversed(Message.all().filter('room =', room).order('-timestamp').fetch(40))]
        account = get_account()
        roomlist_query = RoomList.all()
        roomlist_query.filter('room = ', room)
        roomlist = roomlist_query.filter('account = ', account).get()
        if not roomlist:
            roomlist = RoomList(account=account, room=room)
            roomlist.put()
        roomlist = RoomList.all().filter('room = ', room)
        context = {
            'room': room,
            'roomlist': roomlist,
            'messages': messages,
            }
        if messages:
            context['message_last_key'] = messages[-1].key()
        self.response.out.write(template.render('templates/room.html', context))

                                                    
class LeaveHandler(webapp.RequestHandler):
    
    def post(self, room_key):
        room = Room.all().filter('__key__ =', Key(room_key)).get()
        account = get_account()
        roomlist_query = RoomList.all()
        roomlist_query.filter('room = ', room)
        roomlist = roomlist_query.filter('account = ', account).get()
        roomlist.delete()
        #send a message to the room about the part
        user = users.get_current_user()
        sender = Account.all().filter('user =', user).get()
        timestamp = datetime.now()
        content = "leaving"
        message = Message(sender=sender, room=room, timestamp=timestamp, content=content,
                          event=Message_event_codes['part'])
        message.put()
        self.redirect('/room/')

application = webapp.WSGIApplication([('/room/', RoomCollectionHandler),
                                      (r'/room/([^/]+)', RoomHandler),
                                      (r'/room/([^/]+)/leave', LeaveHandler)],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == '__main__':
    main()
