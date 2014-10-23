from google.appengine.ext.webapp2 import WSGIApplication
from google.appengine.ext.webapp2.util import run_wsgi_app
from myhandler import MyHandler
from userdata import PreBranch, Branch

class GuestRegisterBranchPage(MyHandler):

    def post(self):
        user = self.user()
        name = self.get_str('name')
        bid = self.get_int('bid')
        content = {'name': name, 'bid': bid}
        try:
            proper_branch = Branch.all().filter('bid =', bid).get()
            if proper_branch:
                raise ValueError('branch ID %d is occupied by %s.' % (bid, proper_branch.name))
            if bid < 0:
                raise ValueError('branch ID must be positive.')
            branch = PreBranch(
              user=user, uid=user.user_id(),
              name=name, bid=bid
            )
            branch.put()
        except BaseException, e:
            template = 'fail'
            content['message'] = e.message
        else:
            template = 'success'
            content['wid'] = branch.key().id()
            self.mail_from_admin('stneuron@nifty.com', 'NeuronISM: New branch request',
                'see http://neuron-ism.appspot.com/master/prebranch')
        finally:
            self.write_out('guest/branch/' + template, content)

if __name__ == '__main__':
    run_wsgi_app(WSGIApplication([
      ('/guest/register/branch.*', GuestRegisterBranchPage),
    ], debug=True))
