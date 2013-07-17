from myhandler import MasterGeneral
from userdata import PreBranch, Branch

class MasterPrebranchesPage(MasterGeneral):

    def accept(self, wid):
        content = {'old_id': wid}
        try:
            b = PreBranch.get_by_id(wid)
            branch = Branch(
              user=b.user, uid=b.uid,
              name=b.name, bid=b.bid
            )
            branch.put()
            content['branch'] = branch
            b.delete()
        except:
            template = 'fail'
        else:
            template = 'success'
        finally:
            self.write_out('master/branch_add/' + template, content)

    def reject(self, wid):
        content = {'id': wid}
        try:
            b = PreBranch.get_by_id(wid)
            b.delete()
        except:
            template = 'fail'
        else:
            template = 'success'
        finally:
            self.write_out('master/prebranch_del/' + template, content)

    def get_list(self):
        content = {
          'prebranches': [b for b in PreBranch.all()]
        }
        self.write_out('master/prebranch_list', content)

    def get_real(self):
        action = self.get_str('action')
        target = self.get_int('id')
        if action == 'accept':
            return self.accept(target)
        if action == 'reject':
            return self.reject(target)
        return self.get_list()
