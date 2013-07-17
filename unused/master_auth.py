from userdata import Branch, PreBranch

class MasterAuth:

    def branch_list(self, request):
        branches = []
        for branch in Branch.all():
            branches.append(branch)
        return 'master/branch_list', {'branches': branches}

    def prebranch_list(self, request):
        prebranches = []
        for prebranch in PreBranch.all():
            prebranches.append(prebranch)
        return 'master/prebranch_list', {'prebranches': prebranches}

    def prebranch_del(self, request):
        bid = request.get('id', default_value=None)
        render_param = {'id': bid}
        try:
            prebranch = PreBranch.get_by_id(int(bid))
            prebranch.delete()
        except:
            return 'master/prebranch_del/fail', render_param
        return 'master/prebranch_del/success', render_param

    def branch_add(self, request):
        bid = request.get('id', default_value=None)
        render_param = {'old_id': bid}
        try:
            prebranch = PreBranch.get_by_id(int(bid))
            branch = Branch(
              user=prebranch.user,
              user_id=prebranch.user_id,
              name=prebranch.name
            )
            branch.put()
            prebranch.delete()
            render_param['branch'] = branch
        except:
            return 'master/branch_add/fail', render_param
        return 'master/branch_add/success', render_param

