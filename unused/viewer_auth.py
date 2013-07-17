from auth import register_viewer

class ViewerAuth:
    def __init__(self):
        self.target = []

    def register_viewer(self, request):
        return register_viewer(request)
