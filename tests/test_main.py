from loguru import logger

from tests.conftest import *


def test_main():
    assert uri == aide.uri
    assert aide.chain_id == 201019


def test_set_returns():
    aide.set_result_type('receipt')
    address = aide.platon.account.create().address
    transfer_result = aide.transfer.transfer(to_address=address, amount=aide.delegate._economic.add_staking_limit)
    assert transfer_result['status'] == 1

    aide.set_result_type('hash')
    address = aide.platon.account.create().address
    transfer_result = aide.transfer.transfer(to_address=address, amount=aide.delegate._economic.add_staking_limit)
    assert isinstance(transfer_result, str)

    aide.set_result_type('txn')
    address = aide.platon.account.create().address
    transfer_result = aide.transfer.transfer(to_address=address, amount=aide.delegate._economic.add_staking_limit)
    assert isinstance(transfer_result, dict)
    assert transfer_result['chainId'] == 100


def test_create_account():
    address, private_key = aide.create_account()
    # assert address[:3] == aide.hrp


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
    account = Account().from_key(private_key='f90fd6808860fe869631d978b0582bb59db6189f7908b578a886d582cb6fccfa')
    aide.set_default_account(account)
    assert aide.staking.default_account == '0x189DAff2C1faC1328ed4B50Bd0c869A336B54F0C'


def test_inner_vrf_contract():
    """测试调用内置VRF合约"""
    abi_info = [
        {
            "inputs": [
                {
                    "internalType": "uint32",
                    "name": "numWords",
                    "type": "uint32"
                },
                {
                    "internalType": "uint256",
                    "name": "returnValueLength",
                    "type": "uint256"
                }
            ],
            "name": "InvalidRandomWords",
            "type": "error"
        },
        {
            "anonymous": False,
            "inputs": [
                {
                    "indexed": False,
                    "internalType": "uint256[]",
                    "name": "randomWords",
                    "type": "uint256[]"
                }
            ],
            "name": "RandomWords",
            "type": "event"
        },
        {
            "inputs": [
                {
                    "internalType": "uint32",
                    "name": "numWords",
                    "type": "uint32"
                }
            ],
            "name": "requestRandomWords",
            "outputs": [
                {
                    "internalType": "uint256[]",
                    "name": "",
                    "type": "uint256[]"
                }
            ],
            "stateMutability": "nonpayable",
            "type": "function"
        }
    ]
    with open(r'C:\Jw\code\github\platon-aide\build\VRF.bin') as f:
        bytecode = f.read()

    # init_aide = aide.contract.init(abi=result, bytecode=res)  # 链上已经有合约地址即可获得一个合约对象
    contract_obj = aide.contract.deploy(abi=abi_info, bytecode=bytecode)  # deploy 新合约对象
    receipt = contract_obj.requestRandomWords(5)
    result = contract_obj.RandomWords(receipt)
    logger.info(result)
    random_len = len(result[0].args.randomWords)
    logger.info(random_len)
    pass

