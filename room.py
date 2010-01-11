from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.db import Key
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

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
        messages = Message.all().filter('room =', room).order('timestamp')
        if not room:
            # room doesn't exist
            self.error(404)
            self.response.out.write("no such room")
        else:
            self.response.out.write(template.render('templates/room.html', 
                                                    {'room': room,
                                                     'messages': messages}
                                                    ))


application = webapp.WSGIApplication([('/room/', RoomCollectionHandler),
                                      (r'/room/([^/]+)', RoomHandler)],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == '__main__':
    main()
