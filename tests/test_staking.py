from tests.conftest import *


def test_staking_info():
    consensus_staking_info = consensus_aide.staking.staking_info
    assert consensus_staking_info.Status == 0
    status = True
    try:
        aide.staking.staking_info
    except AttributeError:
        status = False
    assert status is False


def test_create_staking():
    # aide.staking.set_default_account(account)
    result = aide.staking.create_staking(
                       amount=None,
                       balance_type=0,
                       node_id=None,
                       benifit_address=None,
                       node_name='',
                       external_id='',
                       details='',
                       website='',
                       reward_per=0,
                       version=None,
                       version_sign=None,
                       bls_pubkey=None,
                       bls_proof=None,
                       txn=None,
                       private_key=None)
    assert result['status'] == 1
    staking_info = aide.staking.get_candidate_info()
    assert staking_info.Status == 0
    assert staking_info.NodeId == aide.staking.node_id
    assert staking_info.Shares == aide.staking._economic.staking_limit

def test_create_staking_noprivate_key():
    account = aide.platon.account.create()
    address = account.address
    transfer_result = aide.transfer.transfer(to_address=address, amount=aide.delegate._economic.staking_limit * 2)
    private_key = account.privateKey.hex()[2:]
    result = aide.staking.create_staking(
        amount=None,
        balance_type=0,
        node_id=None,
        benifit_address=None,
        node_name='',
        external_id='',
        details='',
        website='',
        reward_per=0,
        version=None,
        version_sign=None,
        bls_pubkey=None,
        bls_proof=None,
        txn=None,
        private_key=private_key)
    assert result['status'] == 1
    staking_info = aide.staking.get_candidate_info()
    assert staking_info.Status == 0
    assert staking_info.NodeId == aide.staking.node_id
    assert staking_info.Shares == aide.staking._economic.staking_limit
    assert staking_info.StakingAddress == address


def test_increase_staking():
    block_number = aide.platon.block_number
    aide.wait_block(block_number+160)
    account = Account().from_key(private_key='f90fd6808860fe869631d978b0582bb59db6189f7908b578a886d582cb6fccfa', hrp='lat')
    aide.staking.set_default_account(account)
    result = aide.staking.increase_staking(
                         balance_type=0,
                         node_id=None,
                         amount=None,
                         txn=None,
                         private_key=None)
    assert result['status'] == 1
    staking_info = aide.staking.get_candidate_info()
    assert staking_info.ReleasedHes == aide.staking._economic.add_staking_limit



def test_edit_candidate():
    #  todo: 需要改迭代器
    account = Account().from_key(private_key='f90fd6808860fe869631d978b0582bb59db6189f7908b578a886d582cb6fccfa',
                                 hrp='lat')
    aide.staking.set_default_account(account)
    node_name = 'hello platon'
    result = aide.staking.edit_candidate(node_name=node_name)
    staking_info = aide.staking.get_candidate_info()
    assert staking_info.NodeName == node_name

def test_withdrew_staking():
    result = aide.staking.withdrew_staking()
    assert result['status'] == 1
    candidate_list = aide.staking.get_candidate_list()
    nodeid_list = [staking_info.NodeId for staking_info in candidate_list]
    assert aide.staking.node_id not in nodeid_list


def test_get_verifier_list():
    verifier_list = aide.staking.get_verifier_list()
    assert 4 <= len(verifier_list) <= 5
    assert verifier_list[0].NodeId

def test_get_validator_list():
    validator_list = aide.staking.get_validator_list()
    assert len(validator_list) == 4
    assert validator_list[0].NodeId


def test_get_candidate_list():
    candidate_list = aide.staking.get_candidate_list()
    print(candidate_list)
    nodeid_list = [staking_info.NodeId for staking_info in candidate_list]
    assert aide.staking.node_id in nodeid_list


def test_get_candidate_info():
    candidate_info = aide.staking.get_candidate_info()
    assert candidate_info.NodeId == aide.staking.node_id


def test_get_block_reward():
    block_reward = aide.staking.get_block_reward()
    assert isinstance(block_reward, int)


def test_get_staking_reward():
    staking_reward = aide.staking.get_staking_reward()
    assert isinstance(staking_reward, int)

def test_get_avg_block_time():
    avg_block_time = aide.staking.get_avg_block_time()
    assert isinstance(avg_block_time, int)