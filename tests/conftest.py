import pytest
from web3 import Account

from platon_aide.main import Aide

consensus_uri = 'http://192.168.16.121:6789'
consensus_aide = Aide(consensus_uri)

uri = 'http://192.168.16.121:6790'
aide = Aide(uri)
account = Account().from_key(private_key='f51ca759562e1daf9e5302d121f933a8152915d34fcbc27e542baf256b5e4b74')
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