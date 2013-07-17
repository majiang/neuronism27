from auth import register_viewer
from google.appengine.api.users import get_current_user
from userdata import PreBranch, Branch

class GuestAuth:

    def index(self, request):
        branches = []
        for branch in Branch.all():
            branches.append(branch)
        return 'guest/index', {'branches': branches}

    def register_viewer(self, request):
        return register_viewer(request)

    def register_branch(self, request):
        user = get_current_user()
        name = request.get('name', default_value=None)
        render_param = {'name': name}
        try:
            branch = PreBranch(
              user=user,
              user_id=user.user_id(),
              name=name
            )
            branch.put()
            render_param['id'] = branch.key().id()
        except:
            return 'guest/branch/fail', render_param
        return 'guest/branch/success', render_param


