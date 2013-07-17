from google.appengine.api import users
from google.appengine.ext.webapp import RequestHandler, WSGIApplication
from google.appengine.ext.webapp.util import run_wsgi_app
from user_auths.userdata import Master, Branch, Viewer
from user_auths.master_auth import MasterAuth
from user_auths.branch_auth import BranchAuth
from user_auths.viewer_auth import ViewerAuth
from user_auths.guest_auth import GuestAuth
import os
from google.appengine.ext.webapp import template

def get_user_auths(user):
    ret = []
    master = Master.all().filter('user_id =', user.user_id()).get()
    if master:
        ret.append(MasterAuth())
    for branch in Branch.all().filter('user_id =', user.user_id()):
        ret.append(BranchAuth(branch.key().id()))
    viewers = ViewerAuth()
    for viewer in Viewer.all().filter('user_id =', user.user_id()):
        viewers.target.append(viewer.branch_id, viewer.player_id)
    if viewers.target:
        ret.append(viewers)
    ret.append(GuestAuth())
    return ret


class MainPage(RequestHandler):

    def admin(self):
        user = users.get_current_user()
        if users.is_current_user_admin():
            Master(user=user, user_id=user.user_id()).put()

    def nimda(self):
        if users.is_current_user_admin():
            for master in Master.all().filter('user =', users.get_current_user()):
                master.delete()

    def get(self):
        user = users.get_current_user()
        if not user:
            self.redirect(users.create_login_url(self.request.uri))
            return
        auths = get_user_auths(user)
        action = self.request.get('action', default_value=None)

        if action is None:
            action = 'index'
        if action == 'admin':
            self.admin()
            return
        if action == 'nimda':
            self.nimda()
            return
        if action[0] == '_':
            self.error(403)
            return

        for auth in auths:
            operation = getattr(auth, action, None)
            if not (operation is None):
                break
        else:
            operation = auths[0].index
        try:
            template_name, result = operation(self.request)
        except:
            return
        self.response.out.write(template.render(
            os.path.join(os.path.dirname(__file__), 'template/%s.html' % template_name),
            result
        ))


if __name__ == '__main__':
    run_wsgi_app(WSGIApplication([
        ('/.*', MainPage),
    ], debug=True))

