from google.appengine.ext.webapp2.blobstore_handlers import BlobstoreUploadHandler as BUH
from google.appengine.ext.blobstore import BlobKey, BlobReader
from os.path import join
from google.appengine.ext.webapp2.template import render
from myhandler import dir_path
from util import min_date, max_date, today, tomorrow
from score import valid
from scoredata import branch_newest_date, count_unprocessed
from google.appengine.api.users import get_current_user
from userdata import Branch

class BranchScorePreviewPage(BUH):

    def user(self):
        'gets current user'
        return get_current_user()

    def branch(self):
        return [branch for branch in Branch.all().filter('uid =', self.user().user_id())]

    def post(self):
        branches = self.branch()
        if not branches:
            self.error(403)
            return None
        if len(branches) > 1:
            self.response.out.write(render(
              join(dir_path, 'branch/multiple.html'),
              {'action': 'uploading score'}
        ))
            return None
        bid = branches[0].bid
        try:
            key = str(self.get_uploads('score')[0].key())
            reader = BlobReader(BlobKey(key))
        except:
            return self.redirect('/branch/score/upload')

        date_valid = branch_newest_date(bid)
        date_min = max_date
        date_max = min_date
        lines = 0
        correct = 0
        errors = []
        for line in reader:
            lines += 1
            try:
                date_cur = valid(line)
            except StandardError, e:
                errors.append('line #%d: %s' % (lines, e.message))
                continue
            else:
                date_min = min(date_min, date_cur)
                date_max = max(date_max, date_cur)
                correct += 1
        content = {
          'bname': branches[0].name, 'key': key,
          'min_date_error': (date_min < date_valid and correct),
          'max_date_error': (tomorrow(today()) < date_max and correct),
          'min_date': date_min, 'max_date': date_max,
          'lines': lines, 'correct': correct,
          'errors': errors, 'error_count': len(errors),
          'error_perc': len(errors)*100.0 / lines,
          'input_date': date_valid,
          'remain_queue': count_unprocessed(bid)
        }
        self.response.out.write(render(
          join(dir_path, 'branch/score/preview.html'),
          content
        ))
