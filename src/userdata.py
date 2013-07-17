from google.appengine.ext import db

class Viewer(db.Model):
    user = db.UserProperty(required=True)
    uid = db.StringProperty(required=True)
    bid = db.IntegerProperty(required=True)
    pid = db.IntegerProperty(required=True)


class PreViewer(db.Model):
    user = db.UserProperty()
    uid = db.StringProperty(required=True)
    bid = db.IntegerProperty(required=True)
    pid = db.IntegerProperty(required=True)
    since = db.DateTimeProperty(auto_now=True)


class Branch(db.Model):
    user = db.UserProperty(required=True)
    uid = db.StringProperty(required=True)
    name = db.StringProperty(required=True)
    bid = db.IntegerProperty(required=True)
    mstr = db.BooleanProperty(required=True, default=False)
    def additional_info(self):
        from scoredata import BranchState
        self.games = BranchState.all().filter('bid =', self.bid).get().counter.games
        return self

class PreBranch(db.Model):
    user = db.UserProperty(required=True)
    uid = db.StringProperty(required=True)
    name = db.StringProperty(required=True)
    bid = db.IntegerProperty(required=True)

class Master(db.Model):
    user = db.UserProperty(required=True)
    uid = db.StringProperty(required=True)


def get_branch(bid):
    return Branch.all().filter('bid =', bid).filter('mstr =', False).get()
