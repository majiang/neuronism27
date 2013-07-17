from myhandler import BranchGeneral
from scoredata import FrequentQuery

class BranchFrequentQueryPage(BranchGeneral):
    def get_real(self, bid):
        fq = FrequentQuery.by_bid(bid)
        additional_message = ''
        add = self.get_int('add', 0)
        remove = self.get_int('del', 0)
        if add > 0:
            additional_message = fq.append(add)
        elif remove > 0:
            additional_message = fq.remove(remove)
        self.write_out('branch/frequent', {
            'additional_message': additional_message,
            'bname': self.branch_name(),
            'datum': fq.query()
        })
