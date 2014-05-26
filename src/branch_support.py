from myhandler import BranchGeneral
from google.appengine.api import mail

class BranchSupportPage(BranchGeneral):

    def get(self):
        self.write_out('viewer/support', {'email': self.user().email(), 'auth': 'branch'})
    def post(self):
        sender = self.user().email()
        to = 'r.97all@gmail.com'
        subject = self.get_str('subject')
        body = self.get_str('body')
        mail.send_mail(sender, to, subject, body)
