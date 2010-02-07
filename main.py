import wsgiref.handlers


from google.appengine.ext import webapp
from account import get_account


class MainHandler(webapp.RequestHandler):

  def get(self):
    account = get_account()
    if (account):
        self.response.out.write('Hello ' + account.nickname)
        self.response.out.write("<br>")
        self.response.out.write("<a href='/room/'>Go join a room</a>")
    else:
        self.response.out.write("Welcome, new chatter. First you're going to need to \
                                <a href='/account/'>create a new account.</a>")


def main():
  application = webapp.WSGIApplication([('/', MainHandler)],
                                       debug=True)
  wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
  main()
