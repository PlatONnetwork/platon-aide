from tests.conftest import *


def test_staking_block_number():
    staking_block_number = aide.delegate._staking_block_number
    assert isinstance(staking_block_number, int)


def test_delegate():
    account = aide.platon.account.create()
    address = account.address
    aide.transfer.transfer(to_address=address, amount=aide.delegate._economic.staking_limit)
    private_key = account.privateKey
    result = aide.delegate.delegate(private_key=private_key)
    assert result['status'] == 1
    delegate_info = aide.delegate.get_delegate_info(address=address)
    assert delegate_info.Addr == address


def test_withdrew_delegate():
    account = aide.platon.account.create()
    address = account.address
    aide.transfer.transfer(to_address=address, amount=aide.delegate._economic.staking_limit)
    private_key = account.privateKey
    result = aide.delegate.delegate(private_key=private_key)
    withdrew_result = aide.delegate.withdrew_delegate(
        amount=0,
        staking_block_identifier=None,
        node_id=None,
        txn=None,
        private_key=private_key,
    )
    assert withdrew_result['status'] == 1
    delegate_info = aide.delegate.get_delegate_info(address=address)
    assert delegate_info is None


def test_get_delegate_info():
    account = aide.platon.account.create()
    address = account.address
    aide.transfer.transfer(to_address=address, amount=aide.delegate._economic.staking_limit)
    private_key = account.privateKey
    result = aide.delegate.delegate(private_key=private_key)
    assert result['status'] == 1
    delegate_info = aide.delegate.get_delegate_info(address=address)
    assert delegate_info.Addr == address

    account = aide.platon.account.create()
    address = account.address
    delegate_info = aide.delegate.get_delegate_info(address=address)
    assert delegate_info is None


def test_get_delegate_list():
    account = aide.platon.account.create()
    address = account.address
    delegate_list = aide.delegate.get_delegate_list(address)
    assert delegate_list is None
    aide.transfer.transfer(to_address=address, amount=aide.delegate._economic.staking_limit)
    private_key = account.privateKey
    result = aide.delegate.delegate(private_key=private_key)
    delegate_list = aide.delegate.get_delegate_list(address)
    delegate_address_list = [delegate_info.Addr for delegate_info in delegate_list]
    assert address in delegate_address_list


def test_withdraw_delegate_reward():
    account = aide.platon.account.create()
    address = account.address
    private_key = account.privateKey
    status = True
    try:
        delegate_reward_result = aide.delegate.withdraw_delegate_reward(txn=None,
                                                                        private_key=private_key)
    except:
        status = False
    assert status is False
    aide.transfer.transfer(to_address=address, amount=aide.delegate._economic.staking_limit)
    result = aide.delegate.delegate(private_key=private_key)
    balance = aide.platon.get_balance(address)
    print(balance)
    block_number = aide.platon.block_number
    aide.wait_block(block_number + 160)
    delegate_reward_result = aide.delegate.withdraw_delegate_reward(txn=None,
                                                                    private_key=private_key)
    assert delegate_reward_result['status'] == 1
    balance_after = aide.platon.get_balance(address)
    assert balance_after - balance < 0

    block_number = aide.platon.block_number
    aide.wait_block(block_number + 160)
    delegate_reward_result = aide.delegate.withdraw_delegate_reward(txn=None,
                                                                    private_key=private_key)
    assert delegate_reward_result['status'] == 1
    balance_delegate_reward = aide.platon.get_balance(address)
    assert balance_delegate_reward - balance_after > 0


def test_get_delegate_reward():
    account = aide.platon.account.create()
    address = account.address
    private_key = account.privateKey
    delegate_reward = aide.delegate.get_delegate_reward(address=address,
                                                        node_ids=None)
    assert delegate_reward == 'Delegation info not found'

    aide.transfer.transfer(to_address=address, amount=aide.delegate._economic.staking_limit)
    result = aide.delegate.delegate(private_key=private_key)
    block_number = aide.platon.block_number
    aide.wait_block(block_number + 160)
    delegate_reward = aide.delegate.get_delegate_reward(address=address,
                                                        node_ids=[])
    assert delegate_reward[0]['nodeID'] == aide.staking._node_id
