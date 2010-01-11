import wsgiref.handlers


from google.appengine.ext import webapp


class MainHandler(webapp.RequestHandler):

  def get(self):
    self.response.out.write('Hello world!')


def main():
  application = webapp.WSGIApplication([('/', MainHandler)],
                                       debug=True)
  wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
  main()
