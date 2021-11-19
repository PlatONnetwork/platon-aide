from tests.conftest import *


def test_transfer():
    address = aide.platon.account.create().address
    transfer_result = aide.transfer.transfer(to_address=address, amount=aide.delegate._economic.add_staking_limit)
    assert transfer_result['status'] == 1


def test_restricting():
    address = aide.platon.account.create().address
    amount = aide.staking._economic.staking_limit
    plans = [{'Epoch': 1, 'Amount': amount},
             {'Epoch': 2, 'Amount': amount}]
    result = aide.transfer.restricting(release_address=address, plans=plans)
    assert result['status'] == 1


def test_get_balance():
    address = aide.platon.account.create().address
    balance = aide.platon.get_balance(address)
    transfer_result = aide.transfer.transfer(to_address=address, amount=aide.delegate._economic.add_staking_limit)
    balance_after = aide.platon.get_balance(address)
    assert balance_after - balance == aide.delegate._economic.add_staking_limit


def test_get_restricting_info():
    address = aide.platon.account.create().address
    amount = aide.staking._economic.staking_limit
    plans = [{'Epoch': 1, 'Amount': amount},
             {'Epoch': 2, 'Amount': amount}]
    result = aide.transfer.restricting(release_address=address, plans=plans)
    restricting_info = aide.transfer.get_restricting_info(address)
    assert restricting_info['balance'] == amount * 2
