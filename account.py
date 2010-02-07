from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.db import Key
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app
import urllib, hashlib
from models import *


class AccountCollectionHandler(webapp.RequestHandler):

    def get(self):
        #user = users.get_current_user()
        #account = Account.all().filter('user =', user).get()
        account = get_account()
        if account:
            # account exists
            if not account.gravatar_tag:
                account.gravatar_tag = gravatar(account.user.nickname())
                #account.gravatar_tag = "test123"
                account.put()
            self.redirect('/account/' + str(account.key()))
        else:
            # no account for this user
            self.response.out.write(template.render('templates/account_create.html', None))

    def post(self):
        user = users.get_current_user()
        nickname = self.request.get('nickname')
        email = self.request.get('nickname')
        if not len(nickname):
            # no nickname entered
            self.response.out.write(template.render('templates/account_create.html',
                                                    {'error_msg': 'Please enter a nickname.'}
                                                    ))
        else:
            account = Account(user=user, nickname=nickname, email=email)
            account.put()
            self.redirect('/account/' + str(account.key()))
            

class AccountHandler(webapp.RequestHandler):

    def get(self, account_key):
        account = Account.all().filter('__key__ =', Key(account_key)).get()
        if not account:
            # account doesn't exist
            self.error(404)
            self.response.out.write("no such account")
        else:
            self.response.out.write(template.render('templates/account.html', 
                                                    {'account': account}
                                                    ))


application = webapp.WSGIApplication([('/account/', AccountCollectionHandler),
                                      (r'/account/([^/]+)', AccountHandler)],
                                     debug=True)


def main():
    run_wsgi_app(application)

def gravatar(email):
    size=10
    rating='g'
    default_image=''
    gravatar_url = "http://www.gravatar.com/avatar/"
    gravatar_url += hashlib.md5(email).hexdigest()
    gravatar_url += urllib.urlencode({'s':str(size),
        'r':rating,
        'd':default_image})
    return """<img src="%s" alt="gravatar" />""" % gravatar_url

def get_account():
    user = users.get_current_user()
    account = Account.all().filter('user =', user).get()
    return account


if __name__ == '__main__':
    main()
