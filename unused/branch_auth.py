from userdata import Viewer, PreViewer

class BranchAuth:
    def __init__(self, branch_id):
        self.id = branch_id

    def previewer_list(self, request):
        previewers = []
        for previewer in PreViewer.all().filter('branch_id =', self.id):
            previewers.append(previewer)
        return 'branch/previewer_list', {'previewers': previewers}

    def previewer_del(self, request):
        vid = request.get('id', default_value=None)
        render_param = {'id': vid}
        try:
            previewer = PreViewer.get_by_id(int(vid))
            previewer.delete()
        except:
            return 'branch/previewer_del/fail', render_param
        return 'branch/previewer_del/success', render_param

    def viewer_add(self, request):
        vid = request.get('id', default_value=None)
        render_param = {'old_id': vid}
        try:
            previewer = PreViewer.get_by_id(int(vid))
            if previewer.branch_id != self.id:
                raise Exception()
            viewer = Viewer(
              user=previewer.user,
              user_id=previewer.user_id,
              branch_id=previewer.branch_id,
              player_id=previewer.player_id
            )
            viewer.put()
            previewer.delete()
            render_param['viewer'] = viewer
        except:
            return 'branch/viewer_add/fail', render_param
        return 'branch/viewer_add/success', render_param


    def viewer_list(self, request):
        viewers = []
        for viewer in Viewer.all().filter('branch_id =', self.id):
            viewers.append(viewer)
        return 'branch/viewer_list', {'viewers': viewers}
