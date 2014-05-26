from google.appengine.ext.webapp import WSGIApplication
from google.appengine.ext.webapp.util import run_wsgi_app
from myhandler import MyHandler

class Page(MyHandler):

    def post(self):
        user = self.user()
        name = self.get_str('name')
        content = {}
        try:
            pass
        except:
            template = 'fail'
        else:
            template = 'success'
        finally:
            self.write_out('' + template, content)

if __name__ == '__main__':
    run_wsgi_app(WSGIApplication([
      ('/hoge.*', Page),
    ], debug=True))
