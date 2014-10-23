#from google.appengine.api import memcache
import logging
from webapp2 import RequestHandler
from google.appengine.api.users import get_current_user
from google.appengine.api import mail
from os.path import join, dirname
from userdata import Master, Branch, Viewer

import jinja2
jinja_env = jinja2.Environment(
    autoescape=True,
    loader=jinja2.FileSystemLoader(
        join(dirname(__file__), 'template')))

dir_path = join(dirname(__file__), 'template')

class MyHandler(RequestHandler):

    def mail_from_admin(self, to, subject, body):
        try:
            mail.send_mail('admin@neuron-ism.appspotmail.com', to, subject, body)
        except:
            logging.warning('failed to send e-mail')
        else:
            logging.debug('e-mail sent to %s. Subject="%s", Body="%s"' % (to, subject, body))


    def user(self):
        'gets current user'
        return get_current_user()

    def master(self):
        return [master for master in Master.all().filter('uid =', self.user().user_id())]

    def branch(self):
        return [branch for branch in Branch.all().filter('uid =', self.user().user_id())]

    def viewer(self):
        return [viewer for viewer in Viewer.all().filter('uid =', self.user().user_id())]

    def reject_request(self):
        self.error(403)

    def get_int(self, param, default=-1):
        'gets a non-negative integer parameter'
        try:
            return int(self.request.get(param))
        except:
            return default

    def get_str(self, param):
        'gets a string'
        return self.request.get(param)

    def write_out(self, file_name, content):
        'write content to response using template in fle_name'
        self.response.out.write(
            jinja_env.get_template(file_name + '.html').render(
          content
        ))

    def write_raw(self, content):
        self.response.out.write(content)


class BranchGeneral(MyHandler):

    def get_real(self, bid):
        raise NotImplementedError

    def action_name(self):
        raise NotImplementedError

    def branch_name(self):
        branches = self.branch() # todo:  = filter(lambda b: not (b.mstr), self.branch()) # username and mstr
        if branches == []:
            return ''
        return Branch.all().filter('bid =', branches[0].bid).filter('mstr =', False).get().name

    def get(self):
        branches = self.branch()
        if not branches:
            return self.reject_request()
        if len(branches) > 1:
            return self.write_out('branch/multiple', {'action': self.action_name()})
        self.get_real(branches[0].bid)


class MasterGeneral(MyHandler):

    def get(self):
        masters = self.master()
        if not masters:
            return self.reject_request()
        self.get_real()


class ViewerGeneral(MyHandler):

    def get(self):
        viewers = self.viewer()
        if len(viewers) == 1:
            return self.get_real(viewers[0])
        try:
            selected_viewer = Viewer.get_by_id(self.get_int('viewer'))
        except:
            self.reject_request()
        if selected_viewer.uid == self.user().user_id():
            return self.get_real(selected_viewer)
        if not viewers:
            return self.reject_request()
