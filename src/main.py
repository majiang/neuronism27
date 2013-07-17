from google.appengine.ext.webapp import WSGIApplication

from index import IndexPage
from master_prebranches import MasterPrebranchesPage
from master_branches import MasterBranchesPage, BranchSelfStatsPage
from branch_previewers import BranchPreviewersPage
from guest_register_branch import GuestRegisterBranchPage
from guest_register_viewer import GuestRegisterViewerPage

from branch_player_list import BranchPlayerListPage
from branch_score_upload import BranchScoreUploadPage
from branch_score_preview import BranchScorePreviewPage
from branch_score_confirm import BranchScoreConfirmPage
from branch_score_cancel import BranchScoreCancelPage
from branch_score_view import BranchScoreViewPage
from branch_player import BranchPlayerPage
from branch_rating_ranking import BranchRatingRankingPage
from branch_frequent_query import BranchFrequentQueryPage
from branch_report import BranchReportPage

from branch_player_active import BranchPlayerActivePage
from branch_player_inactive import BranchPlayerInactivePage
from branch_player_degree import BranchPlayerDegreePage

from viewer_score_default import ViewerScoreDefaultPage
from viewer_support import ViewerSupportPage
from viewer_rating_ranking import ViewerRatingRankingPage

app = WSGIApplication([
        ('/admin/report.*', AdminAutoReportPage),
        ('/admin.*', AdminPage),
        ('/master/prebranch.*', MasterPrebranchesPage),
        ('/master/branch.*', MasterBranchesPage),
        ('/branch/previewer.*', BranchPreviewersPage),
        ('/guest/register/branch.*', GuestRegisterBranchPage),
        ('/guest/register/viewer.*', GuestRegisterViewerPage),
        ('/branch/stats.*', BranchSelfStatsPage),
        ('/branch/player/list.*', BranchPlayerListPage),
        ('/branch/player/active.*', BranchPlayerActivePage),
        ('/branch/player/inactive.*', BranchPlayerInactivePage),
        ('/branch/player/degree.*', BranchPlayerDegreePage),
        ('/branch/player.*', BranchPlayerPage),
        ('/branch/score/upload.*', BranchScoreUploadPage),
        ('/branch/score/preview.*', BranchScorePreviewPage),
        ('/branch/score/confirm.*', BranchScoreConfirmPage),
        ('/branch/score/cancel.*', BranchScoreCancelPage),
        ('/branch/score/view.*', BranchScoreViewPage),
        ('/branch/rating.*', BranchRatingRankingPage),
        ('/branch/frequent.*', BranchFrequentQueryPage),
        ('/branch/report.*', BranchReportPage),
        ('/viewer/score.*', ViewerScoreDefaultPage),
        ('/viewer/support.*', ViewerSupportPage),
        ('/viewer/rating.*', ViewerRatingRankingPage),
    ] + [('/.*', IndexPage)], debug=True)
