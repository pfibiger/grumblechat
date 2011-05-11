import wsgiref.handlers


from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import login_required
from utils import *


class MainHandler(webapp.RequestHandler):

  @login_required
  def get(self):
    account = get_account()
    if (account):
        self.redirect('/room/')
    else:
        self.redirect('/account/')

def main():
  application = webapp.WSGIApplication([('/', MainHandler)],
                                       debug=True)
  wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
  main()
