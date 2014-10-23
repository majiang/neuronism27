from google.appengine.ext.webapp2 import WSGIApplication
from google.appengine.ext.webapp2.util import run_wsgi_app
from myhandler import MyHandler
from userdata import PreViewer, Branch

class GuestRegisterViewerPage(MyHandler):

    def post(self):
        bid = self.get_int('bid')
        pid = self.get_int('pid')
        user = self.user()
        content = {'branch': bid, 'player': pid}
        try:
            if bid < 0 or pid < 0:
                raise ValueError
            branch = Branch.all().filter('bid =', bid).filter('mstr =', False).get()
            if branch is None:
                raise ValueError
            viewer = PreViewer(
                user=user, uid=user.user_id(),
                bid=bid, pid=pid
            )
            viewer.put()
        except:
            template = 'fail'
        else:
            template = 'success'
            self.mail_from_admin(branch.user.email(), 'NeuronISM: New viewer request',
                'see http://neuron-ism.appspot.com/branch/previewer')
        finally:
            self.write_out('guest/viewer/' + template, content)

if __name__ == '__main__':
    run_wsgi_app(WSGIApplication([
      ('/guest/register/viewer.*', GuestRegisterViewerPage),
    ], debug=True))
