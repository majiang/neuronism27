from myhandler import BranchGeneral
from google.appengine.ext.blobstore import BlobInfo

def delete_blob(key):
    try:
        BlobInfo.get(key).delete()
    except:
        return 'failed'
    else:
        return 'succeeded'

class BranchScoreCancelPage(BranchGeneral):

    def action_name(self):
        return 'canceling uploaded score'

    def get_real(self, bid):
        content = {'result': delete_blob(self.get_str('key'))}
        self.write_out('branch/score/cancel', content)
