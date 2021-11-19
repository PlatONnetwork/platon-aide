from tests.conftest import *


def test_chain_version():
    chain_version = aide.govern.chain_version
    assert chain_version.integer == 65793


def test_version_proposal():
    version = 66048
    txn = {'gas': 2100000, 'gasPrice': 3000000000000000}
    proposal_result = aide.govern.version_proposal(version=version, txn=txn)
    assert proposal_result['status'] == 1


def test_param_version():
    module = 'staking'
    name = 'unStakeFreezeDuration'
    value = '10'
    txn = {'gas': 2100000, 'gasPrice': 3000000000000000}
    param_version_result = aide.govern.param_version(
        module=module,
        name=name,
        value=value,
        # pip_number=second(),
        # node_id=None,
        txn=txn,
        # private_key=None
    )
    assert param_version_result['status'] == 1


def test_cancel_proposal(proposal_id):
    proposal_id = proposal_id
    txn = {'gas': 2100000, 'gasPrice': 3000000000000000}
    cancel_proposal_result = aide.govern.cancel_proposal(
        proposal_id=proposal_id,
        voting_rounds=1,
        # node_id=None,
        # pip_number=second(),
        txn=txn,
        # private_key=None,
    )
    assert cancel_proposal_result['status'] == 1


def test_text_proposal():
    txn = {'gas': 2100000, 'gasPrice': 3000000000000000}
    text_proposal_result = aide.govern.text_proposal(
        # pip_number=second(),
        # node_id=None,
        txn=txn,
        # private_key=None,
    )
    assert text_proposal_result['status'] == 1


def test_vote(proposal_id):
    proposal_id = proposal_id
    option = 1
    txn = {'gas': 2100000, 'gasPrice': 3000000000000000}
    vote_result = aide.govern.vote(
        proposal_id=proposal_id,
        option=option,
        # node_id=None,
        # version=None,
        # version_sign=None,
        txn=txn,
        # private_key=None,
    )
    assert vote_result['status'] == 1


def test_declare_version():
    declare_version_result = aide.govern.declare_version(
        # node_id=None,
        # version=None,
        # version_sign=None,
        # txn=None,
        # private_key=None,
    )
    assert declare_version_result['status'] == 1


def test_get_proposal_result(proposal_id):
    proposal_id = proposal_id
    current_block = aide.platon.block_number
    aide.wait_block(current_block + 160 * 4)
    result = aide.govern.get_proposal_result(proposal_id)
    assert result.proposalID == proposal_id


def test_get_proposal_votes(proposal_id):
    proposal_id = proposal_id
    proposal_votes = aide.govern.get_proposal_votes(proposal_id=proposal_id, block_identifier='latest')
    assert proposal_votes.accuVerifiers


def test_proposal_list():
    status = True
    try:
        proposal_list = aide.govern.proposal_list()
    except:
        status = False
    assert status is False

    version = 66048
    txn = {'gas': 2100000, 'gasPrice': 3000000000000000}
    proposal_result = aide.govern.version_proposal(version=version, txn=txn)
    transaction_block_number = proposal_result['blockNumber']
    proposal_list = aide.govern.proposal_list()
    transaction_block_number_list = [transaction.SubmitBlock for transaction in proposal_list]
    assert transaction_block_number in transaction_block_number_list


def test_get_govern_param():
    module = 'staking'
    name = 'unStakeFreezeDuration'
    govern_param = aide.govern.get_govern_param(module=module, name=name)
    assert govern_param == '2'
