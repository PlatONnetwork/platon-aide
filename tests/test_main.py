from tests.conftest import *


def test_main():
    assert uri == aide.uri
    assert aide.hrp == 'lat'
    assert aide.chain_id == 100


def test_set_returns():
    aide.set_returns('receipt')
    address = aide.platon.account.create().address
    transfer_result = aide.transfer.transfer(to_address=address, amount=aide.delegate._economic.add_staking_limit)
    assert transfer_result['status'] == 1

    aide.set_returns('hash')
    address = aide.platon.account.create().address
    transfer_result = aide.transfer.transfer(to_address=address, amount=aide.delegate._economic.add_staking_limit)
    assert isinstance(transfer_result, str)

    aide.set_returns('txn')
    address = aide.platon.account.create().address
    transfer_result = aide.transfer.transfer(to_address=address, amount=aide.delegate._economic.add_staking_limit)
    assert isinstance(transfer_result, dict)
    assert transfer_result['chainId'] == 100


def test_create_account():
    address, private_key = aide.create_account()
    assert address[:3] == aide.hrp


def test_create_hd_account():
    aide.create_hd_account()
    pass


def test_wait_block():
    block_number = aide.platon.block_number
    aide.wait_block(block_number + 160)
    block_number_after = aide.platon.block_number
    assert 0 <= block_number_after - block_number - 160 < 5


def test_ec_recover():
    node_id = aide.ec_recover(1)
    assert node_id


def test_set_default_account():
    account = Account().from_key(private_key='f90fd6808860fe869631d978b0582bb59db6189f7908b578a886d582cb6fccfa',
                                 hrp='lat')
    aide.set_default_account(account)
    assert aide.staking.default_account == 'lat1rzw6lukpltqn9rk5k59apjrf5vmt2ncv8uvfn7'
