import wsgiref.handlers


from google.appengine.ext import webapp
from account import get_account


class MainHandler(webapp.RequestHandler):

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
