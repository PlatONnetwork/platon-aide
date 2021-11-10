import functools
import rlp
from hexbytes import HexBytes
from platon import Web3
from platon.types import BlockData
from platon_account._utils.signing import to_standard_signature_bytes
from platon_hash.auto import keccak
from platon_keys.datatypes import Signature
from platon_typing import HexStr
from platon_utils import remove_0x_prefix, to_canonical_address


def send_transaction(web3: Web3, txn: dict, private_key: str, returns='receipt'):
    """
    签名交易并发送，可以获取交易hash或交易回执

    Args:
        web3: Web3对象
        txn: 要发送的交易dict
        private_key: 地址私钥，用于签名交易
        returns: 指定要返回的结果，取值如下：
                - 'hash': 返回交易哈希
                - 'receipt': 返回交易回执
    """
    if not txn.get('nonce'):
        account = web3.platon.account.from_key(private_key, hrp=web3.hrp)
        nonce = web3.platon.get_transaction_count(account.address)
        txn['nonce'] = nonce

    signed_txn = web3.platon.account.sign_transaction(txn, private_key, web3.hrp)
    tx_hash = web3.platon.send_raw_transaction(signed_txn.rawTransaction)
    if returns == 'hash':
        return bytes(tx_hash).hex()
    receipt = web3.platon.wait_for_transaction_receipt(tx_hash)
    if type(receipt) is bytes:
        receipt = receipt.decode('utf-8')
    return receipt


def contract_transaction(func):
    """
    包装类，用于在调用Module及其子类的方法时，自定义要返回的结果
    可以返回未发送的交易dict、交易hash、交易回执
    """

    @functools.wraps(func)
    def wrapper(self, *args, txn, private_key, **kwargs):
        private_key = private_key or self.default_account.private_key

        if not private_key:
            raise ValueError('arg错误')

        txn = func(*args, **kwargs).build_transaction(txn)
        if self.returns == 'txn':
            return txn
        return self.send_transaction(txn, private_key, self.returns)

    return wrapper


def contract_call(func):

    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        return func(*args, **kwargs).call()

    return wrapper


def ec_recover(block: BlockData):
    """ keccak解出区块的签名节点公钥
    """
    extra = block.extraData[:32]
    sign = block.extraData[32:]
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
                bytes.fromhex(remove_0x_prefix(block.nonce))
                ]
    message_hash = keccak(rlp.encode(raw_data)).digest()
    hash_bytes = HexBytes(message_hash)
    signature_bytes = HexBytes(sign)
    signature_bytes_standard = to_standard_signature_bytes(signature_bytes)
    signature = Signature(signature_bytes=signature_bytes_standard)
    return remove_0x_prefix(HexStr(signature.recover_public_key_from_msg_hash(hash_bytes).to_hex()))
