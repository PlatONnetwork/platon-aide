import pytest
from platon import Account

from platon_aide.main import PlatonAide

consensus_uri = 'http://192.168.16.121:6789'
consensus_aide = PlatonAide(consensus_uri)

uri = 'http://192.168.16.121:6790'
aide = PlatonAide(uri)
account = Account().from_key(private_key='f90fd6808860fe869631d978b0582bb59db6189f7908b578a886d582cb6fccfa', hrp='lat')
aide.set_default_account(account)


@pytest.fixture()
def proposal_id():
    version = 66048
    txn = {'gas': 2100000, 'gasPrice': 3000000000000000}
    proposal_result = aide.govern.version_proposal(version=version, txn=txn)
    proposal_list = aide.govern.proposal_list()
    transaction_proposal_id_list = [transaction.ProposalID for transaction in proposal_list]
    proposal_id = transaction_proposal_id_list[0]
    yield proposal_id