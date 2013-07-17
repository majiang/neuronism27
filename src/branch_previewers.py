from myhandler import BranchGeneral
from userdata import PreViewer, Viewer, get_branch

class BranchPreviewersPage(BranchGeneral):

    def action_name(self):
        return 'getting previewers info'

    def accept(self, branch, vid):
        content = {'old_id': vid}
        try:
            v = PreViewer.get_by_id(vid)
            if (v is None) or (branch.bid != v.bid):
                raise ValueError
            viewer = Viewer(
              user=v.user, uid=v.uid,
              bid=v.bid, pid=v.pid
            )
            viewer.put()
            v.delete()
            content['viewer'] = viewer
            self.mail_from_admin(viewer.user.email(), 'NeuronISM: Accepted as viewer', 'see http://neuron-ism.appspot.com/ : index for viewers.\nFAQ is on http://neuron-ism.appspot.com/static/faq.html')
        except:
            template = 'fail'
        else:
            template = 'success'
        finally:
            self.write_out('branch/viewer_add/' + template, content)

    def reject(self, branch, vid):
        content = {'id': vid}
        try:
            v = PreViewer.get_by_id(vid)
            if (v is None) or (branch.bid != v.bid):
                raise ValueError
            v.delete()
        except:
            template = 'fail'
        else:
            template = 'success'
        finally:
            self.write_out('branch/previewer_del/' + template, content)

    def get_list(self, branch):
        content = {
          'bname': branch.name,
          'previewers': [v for v in PreViewer.all().filter('bid =', branch.bid)]
        }
        self.write_out('branch/previewer_list', content)

    def get_real(self, bid):
        branch = get_branch(bid)
        action = self.get_str('action')
        target = self.get_int('id')
        if action == 'accept':
            return self.accept(branch, target)
        elif action == 'reject':
            return self.reject(branch, target)
        else:
            return self.get_list(branch)
