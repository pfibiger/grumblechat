from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.db import Key
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app
from datetime import datetime

from models import *
from utils import *
import re


class RoomCollectionHandler(webapp.RequestHandler):

    def get(self):
        rooms = Room.all().order('name')
        roomlist = RoomList.all()
        self.response.out.write(template.render('templates/room_collection.html',
                                                {'rooms': rooms, 
                                                 'roomlist': roomlist}
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
            slug = name.lower()
            slug = re.sub(r'\W+', '', slug)
            room = Room.all().filter('slug =', slug).get()
            i = 1
            while room:
                slug = slug + str(i)
                room = Room.all().filter('slug =', slug).get()
                i += 1
            room = Room(name=name, slug=slug)
            room.put()
            self.redirect('/room/' + slug)
            

class RoomHandler(webapp.RequestHandler):

    def get(self, room_key):
        room = Room.all().filter('slug =', room_key).get()
        if not room:
            room = Room.all().filter('__key__ =', Key(room_key)).get()
            if not room:
                # room doesn't exist
                self.error(404)
                self.response.out.write("no such room")
                return
        # return (up to) last 70 messages
        # FIXME should define '70' as a constant
        # need to enumerate query results to access last message below
        # add a second .filter below to hide topic/join/part from template on render
        # filter('event =', 'message') this appears to break the user list though :(
        messages = [m for m in reversed(Message.all().filter('room =', room).order('-timestamp').fetch(70))]
        account = get_account()
        roomlist_query = RoomList.all()
        roomlist_query.filter('room = ', room)
        roomlist = roomlist_query.filter('account = ', account).get()
        if not roomlist:
            #add us to the room we've just joined.
            roomlist = RoomList(account=account, room=room)
            roomlist.put()
            #send a message to update everyone elses contact list
            user = users.get_current_user()
            sender = Account.all().filter('user =', user).get()
            timestamp = datetime.now()
            extra = sender.gravatar_tag
            message = Message(sender=sender, room=room, timestamp=timestamp,
                              event=Message_event_codes['join'], extra=extra)
            message.put()
            
        roomlist = RoomList.all().filter('room = ', room)
        messages = [transform_message(m) for m in messages]
        context = {
            'room': room,
            'account': account,
            'roomlist': roomlist,
            'messages': messages,
            'message_event_names': Message_event_names,
            }
        if messages:
            context['message_last_key'] = messages[-1].key()
        self.response.out.write(template.render('templates/room.html', context))

                                                    
class LeaveHandler(webapp.RequestHandler):
    
    def post(self, room_key):
        room = Room.all().filter('__key__ =', Key(room_key)).get()
        account = get_account()
        leave_room(room=room, account=account)
        self.redirect('/room/')

application = webapp.WSGIApplication([('/room/', RoomCollectionHandler),
                                      (r'/room/([^/]+)', RoomHandler),
                                      (r'/room/([^/]+)/leave', LeaveHandler)],
                                     debug=True)

def main():
    webapp.template.register_template_library('filters')
    run_wsgi_app(application)

if __name__ == '__main__':
    main()
