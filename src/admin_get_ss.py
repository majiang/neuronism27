from google.appengine.ext.webapp import RequestHandler
from scoredata import get_ss
from google.appengine.ext.webapp import WSGIApplication

class AdminGetSSPage(RequestHandler):

    def get(self):
        ss = get_ss(97, 18, 13)
        if ss is None:
            self.response.out.write('Error!')
            return
        self.response.out.write('Success!')

app = WSGIApplication([
    ('/admin/get_ss.*', AdminGetSSPage)
], debug=True)
