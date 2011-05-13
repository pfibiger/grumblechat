from google.appengine.dist import use_library
use_library('django', '1.2')

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.db import Key
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app, login_required

from models import *
from utils import *


class AccountCollectionHandler(webapp.RequestHandler):

    @login_required
    def get(self):
        #user = users.get_current_user()
        #account = Account.all().filter('user =', user).get()
        account = get_account()
        if account:
            # account exists
            self.redirect('/account/' + str(account.key()))
        else:
            # no account for this user
            self.response.out.write(template.render('templates/account_create.html', None))

    def post(self):
        user = users.get_current_user()
        nickname = self.request.get('nickname')
        if not len(nickname):
            # no nickname entered
            self.response.out.write(template.render('templates/account_create.html',
                                                    {'error_msg': 'Please enter a nickname.'}
                                                    ))
        else:
            account = create_account(user, nickname)
            self.redirect('/account/' + str(account.key()))
            

class AccountHandler(webapp.RequestHandler):

    @login_required
    def get(self, account_key):
        account = get_account(account_key)
        if account is None:
            # account doesn't exist
            self.error(404)
            self.response.out.write("no such account")
        else:
            self.response.out.write(template.render('templates/account.html',
                                                    {'account': account}
                                                    ))


class AccountEditHandler(webapp.RequestHandler):
    @login_required
    def get(self, account_key):
        account = Account.get(account_key)
        if not account_is_current(account):
            self.error(403)
            self.response.out.write("cannot edit settings for other users")
        else:
            self.response.out.write(template.render('templates/account_edit.html',
                                                    { 'form': AccountForm(instance=account) }
                                                    ))

    def post(self, account_key):
        account = Account.get(account_key)
        if not account_is_current(account):
            self.error(403)
            self.response.out.write("cannot edit settings for other users")
        else:
            form = AccountForm(data=self.request.POST, instance=account)
            if form.is_valid():
                # Save the data, and redirect to the view page
                entity = form.save()
                self.redirect('/account/' + account_key)
            else:
                # Reprint the form
                self.response.out.write(template.render('templates/account_edit.html',
                                                        { 'form': form }
                                                        ))


application = webapp.WSGIApplication([('/account/', AccountCollectionHandler),
                                      (r'/account/([^/]+)', AccountHandler),
                                      (r'/account/([^/]+)/edit', AccountEditHandler)],
                                     debug=True)


def main():
    run_wsgi_app(application)


if __name__ == '__main__':
    main()
