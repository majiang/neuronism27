from myhandler import BranchGeneral
from google.appengine.ext.blobstore import BlobReader, BlobKey, BlobInfo
from scoredata import branch_newest_date, QueueScore
from score import valid
import util

# TODO: log

def check_date(line):
    branch_newest_date

def start_batch(key, bid):
    try:
        reader = BlobReader(BlobKey(key))
    except:
        return 'failed to find key: please re-upload.'
    newest_date = branch_newest_date(bid)
    dic = {}
    for line in reader:
        line = line.strip()
        try:
            game_date = valid(line)
            if game_date < newest_date:
                game_date = newest_date
        except:
            continue
        if util.tomorrow(util.today()) < game_date:
            continue
        if game_date not in dic:
            dic[game_date] = []
        dic[game_date].append(','.join(line.split(',')[:8]))
    for key_date in sorted(dic.keys()):
        qs = QueueScore(
          bid=bid, game_date=key_date, body=(
            '\n'.join(reversed(dic[key_date]))                                                 
        ))
        qs.put()
    BlobInfo.get(key).delete()
    return 'upload succeeded!'

class BranchScoreConfirmPage(BranchGeneral):

    def action_name(self):
        return 'confirming uploaded score'

    def get_real(self, bid):
        content = {'result': start_batch(self.get_str('key'), bid)}
        self.write_out('branch/score/confirm', content)
