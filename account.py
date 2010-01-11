from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.db import Key
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app
import os

from models import *


class AccountCollectionHandler(webapp.RequestHandler):

    def get(self):
        user = users.get_current_user()
        account = Account.all().filter('user =', user).get()
        if account:
            self.redirect('/account/' + str(account.key()))
        else:
            self.response.out.write(template.render('templates/account_create.html', None))

    def post(self):
        user = users.get_current_user()
        nickname = self.request.get('nickname')
        if (len(nickname)):
            account = Account(user=user, nickname=nickname)
            account.put()
            self.redirect('/account/' + str(account.key()))
        else:
            self.response.out.write(template.render('templates/account_create.html',
                                                    {'error_msg': 'Please enter a nickname.'}
                                                    ))
            

class AccountHandler(webapp.RequestHandler):

    def get(self, account_key):
        account = Account.all().filter('__key__ =', Key(account_key)).get()
        self.response.out.write('nickname=%s ; user=%s' % (account.nickname, str(account.user)))


application = webapp.WSGIApplication([('/account/', AccountCollectionHandler),
                                      (r'/account/([^/]+)', AccountHandler)],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == '__main__':
    main()
