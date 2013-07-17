from google.appengine.ext import blobstore
from myhandler import BranchGeneral
from userdata import get_branch

class BranchScoreUploadPage(BranchGeneral):

    def action_name(self):
        return 'creating upload page'

    def get_real(self, bid):
        url = blobstore.create_upload_url('/branch/score/preview')
        content = {'url': url, 'bname': get_branch(bid).name}
        self.write_out('branch/score/upload', content)
