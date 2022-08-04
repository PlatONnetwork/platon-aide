import functools
import os
import sys
from os.path import abspath

import rlp
from hexbytes import HexBytes

from platon import Web3, HTTPProvider, WebsocketProvider, IPCProvider
from platon._utils.inner_contract import InnerContractEvent
from platon._utils.threads import Timeout
from platon.types import BlockData
from platon_account._utils.signing import to_standard_signature_bytes
from platon_hash.auto import keccak
from platon_keys.datatypes import Signature
from platon_typing import HexStr
from platon_utils import remove_0x_prefix, to_canonical_address

from gql import Client
from gql.transport.aiohttp import AIOHTTPTransport
from gql.transport.websockets import WebsocketsTransport


def get_web3(uri, chain_id=None, hrp=None, timeout=10, modules=None):
    """ 通过rpc uri，获取web3对象。可以兼容历史platon版本
    """
    if uri.startswith('http'):
        provider = HTTPProvider
    elif uri.startswith('ws'):
        provider = WebsocketProvider
    elif uri.startswith('ipc'):
        provider = IPCProvider
    else:
        raise ValueError(f'unidentifiable uri {uri}')

    with Timeout(timeout) as t:
        while True:
            web3 = Web3(provider(uri), chain_id=chain_id, hrp=hrp, modules=modules)
            if web3.isConnected():
                break
            t.sleep(2)

    return web3


def get_gql(uri):
    """ 通过gql uri，获取gql对象。
    # todo: 增加超时处理
    """
    if uri.startswith('http'):
        transport = AIOHTTPTransport
    elif uri.startswith('ws'):
        transport = WebsocketsTransport
    else:
        raise ValueError(f'unidentifiable uri {uri}')

    return Client(transport=transport(uri), fetch_schema_from_transport=True)


def send_transaction(web3: Web3, txn: dict, private_key: str):
    """
    签名交易并发送，可以获取交易hash或交易回执

    Args:
        web3: Web3对象
        txn: 要发送的交易dict
        private_key: 地址私钥，用于签名交易
        returns: 指定要返回的结果，取值如下：
                - 'hash': 返回交易哈希
                - 'receipt': 返回交易回执
                - 'event': 返回内置合约的event内容
    """
    if not private_key:
        return web3.platon.send_transaction(txn)

    if not txn.get('nonce'):
        account = web3.platon.account.from_key(private_key, hrp=web3.hrp)
        txn['nonce'] = web3.platon.get_transaction_count(account.address)

    signed_txn = web3.platon.account.sign_transaction(txn, private_key, web3.hrp)
    return web3.platon.send_raw_transaction(signed_txn.rawTransaction)


def get_transaction_result(web3: Web3, tx_hash, result_type):
    """ 根据指定的result type，来获取交易的返回值
    """
    if result_type == 'hash':
        return bytes(tx_hash).hex()
    receipt = web3.platon.wait_for_transaction_receipt(tx_hash)
    if type(receipt) is bytes:
        receipt = receipt.decode('utf-8')
    if result_type == 'receipt':
        return receipt
    if result_type == 'event':
        return InnerContractEvent.get_event(receipt)


def contract_call(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        return func(self, *args, **kwargs).call()

    return wrapper


def contract_transaction(func):
    """ todo: 增加注释
    """

    @functools.wraps(func)
    def wrapper(self, *args, txn=None, private_key=None, **kwargs):
        # 预填充from地址，避免预估gas时地址相关检验不通过
        account = self.web3.platon.account.from_key(private_key, hrp=self.web3.hrp) if private_key else self.default_account
        if not txn.get('from'):
            txn['from'] = account.address

        # solidity合约方法不传入private key参数，避免abi解析问题
        if func.__name__ == 'fit_func':
            txn = func(self, *args, **kwargs).build_transaction(txn)
        else:
            txn = func(self, *args, private_key=private_key, **kwargs).build_transaction(txn)

        if self._result_type == 'txn':
            return txn
        return self.send_transaction(txn, private_key, self._result_type)

    return wrapper


def ec_recover(block: BlockData):
    """ 使用keccak方式，解出区块的签名节点公钥
    """
    extra = block.proofOfAuthorityData[:32]
    sign = block.proofOfAuthorityData[32:]
    raw_data = [bytes.fromhex(remove_0x_prefix(block.parentHash.hex())),
                to_canonical_address(block.miner),
                bytes.fromhex(remove_0x_prefix(block.stateRoot.hex())),
                bytes.fromhex(remove_0x_prefix(block.transactionsRoot.hex())),
                bytes.fromhex(remove_0x_prefix(block.receiptsRoot.hex())),
                bytes.fromhex(remove_0x_prefix(block.logsBloom.hex())),
                block.number,
                block.gasLimit,
                block.gasUsed,
                block.timestamp,
                extra,
                bytes.fromhex(remove_0x_prefix(block.nonce.hex()))
                ]
    hash_bytes = HexBytes(keccak(rlp.encode(raw_data)))
    signature_bytes = HexBytes(sign)
    signature_bytes_standard = to_standard_signature_bytes(signature_bytes)
    signature = Signature(signature_bytes=signature_bytes_standard)
    return remove_0x_prefix(HexStr(signature.recover_public_key_from_msg_hash(hash_bytes).to_hex()))


def run(cmd):
    """
    The machine executes the cmd command and gets the result
    :param cmd:
    :return:
    """
    r = os.popen(cmd)
    out = r.read()
    r.close()
    return out


def mock_duplicate_sign(dtype, sk, blskey, block_number, epoch=0, view_number=0, block_index=0, index=0):
    """
    forged double sign
    :param dtype:
    :param sk:
    :param blskey:
    :param block_number:
    :param epoch:
    :param view_number:
    :param block_index:
    :param index:
    :return:
    """
    if sys.platform in "linux,linux2":
        tool_file = abspath("tool/linux/duplicateSign")
        run("chmod +x {}".format(tool_file))
    else:
        tool_file = abspath("tool/win/duplicateSign.exe")
    print("{} -dtype={} -sk={} -blskey={} -blockNumber={} -epoch={} -viewNumber={} -blockIndex={} -vindex={}".format(
            tool_file, dtype, sk, blskey, block_number, epoch, view_number, block_index, index))
    output = run(
        "{} -dtype={} -sk={} -blskey={} -blockNumber={} -epoch={} -viewNumber={} -blockIndex={} -vindex={}".format(
            tool_file, dtype, sk, blskey, block_number, epoch, view_number, block_index, index))
    print(output)
    if not output:
        raise Exception("unable to use double sign tool")
    return output.strip("\n")
