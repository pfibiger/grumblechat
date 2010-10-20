from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.db import Key
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from datetime import datetime

from models import *
from utils import *


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
            
        upload_url = blobstore.create_upload_url('/room/' + str(room_key) + '/upload')
        
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
            'upload_url': str(upload_url)
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

class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    def post(self, room_key):
        upload_files = self.get_uploads('qqfile')  # 'qqfile' is file upload field in the form for the ajax plugin
        blob_info = upload_files[0]
        timestamp = datetime.now()
        account = get_account()
        room = Room.all().filter('__key__ =', Key(room_key)).get()
        message = Message(sender=account, room=room, timestamp=timestamp,
                          event=Message_event_codes['upload'], content="http://localhost.com:8080/room/" + room_key + "/download/" + blob_info.key, extra=blob_info.key)
        message.put()
        #self.redirect('/serve/%s' % blob_info.key())
        self.response.write('{success:true}')

class DownloadHandler(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, room_key, resource):
        resource = str(urllib.unquote(resource))
        blob_info = blobstore.BlobInfo.get(resource)
        self.send_blob(blob_info)



application = webapp.WSGIApplication([('/room/', RoomCollectionHandler),
                                      (r'/room/([^/]+)', RoomHandler),
                                      (r'/room/([^/]+)/leave', LeaveHandler),
                                      (r'/room/([^/]+)/upload', UploadHandler),
                                      (r'/room/([^/]+)/download/([^/]+)', DownloadHandler)],
                                     debug=True)

def main():
    webapp.template.register_template_library('filters')
    run_wsgi_app(application)

if __name__ == '__main__':
    main()
