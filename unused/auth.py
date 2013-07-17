from google.appengine.api import users

from userdata import PreViewer

def register_viewer(request):
    user = users.get_current_user()
    branch_id = request.get('branch_id', default_value=None)
    player_id = request.get('player_id', default_value=None)
    render_param = {'branch': branch_id, 'player': player_id}
    try:
        viewer = PreViewer(
          user=user,
          user_id=user.user_id(),
          branch_id=int(branch_id),
          player_id=int(player_id)
        )
        viewer.put()
    except:
        return 'guest/viewer/fail', render_param
    return 'guest/viewer/success', render_param
