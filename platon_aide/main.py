import time
import warnings
from typing import Literal

import rlp
from hexbytes import HexBytes
from loguru import logger
from platon._utils.inner_contract import InnerContractEvent
from platon.main import get_default_modules
from web3.middleware import geth_poa_middleware
from eth_account import Account
from eth_account.signers.local import LocalAccount
from eth_utils import to_checksum_address, combomethod
from platon_aide.transfer import Transfer
from platon_aide.restricting import Restricting
from platon_aide.economic import new_economic, Economic
from platon_aide.calculator import Calculator
from platon_aide.contract import Contract
from platon_aide.staking import Staking
from platon_aide.delegate import Delegate
from platon_aide.slashing import Slashing
from platon_aide.govern import Govern
from platon_aide.graphqls import Graphql
from platon_aide.utils import get_web3
from eth_account._utils.signing import to_standard_signature_bytes
from eth_hash.auto import keccak
from eth_keys.datatypes import Signature
from eth_typing import HexStr
from eth_utils import remove_0x_prefix, to_canonical_address


def get_modules(exclude: list = None):
    """ 排除节点关闭的API
    """
    if not exclude:
        exclude = []

    modules = get_default_modules()
    if 'admin' in exclude:
        modules['node'][1].pop('admin')
    if 'debug' in exclude:
        modules.pop('debug')

    return modules


class Aide:
    """ 主类，功能如下：
    1. 各个子模块的集合体，通过它来调用子模块发送交易
    2. 持有设置数据，如：默认交易账户、经济模型数据、返回结果类型等
    3. 包含一些常用方法，如：创建账户、等待块高/周期、区块解码等
    """

    def __init__(self, uri: str, economic: Economic = None):
        """
        Args:
            uri: 节点开放的RPC链接
            economic: 链上经济模型数据，会自动获取（需要debug接口开放），缺少经济模型数据会导致部分功能不可用。
        """
        self.uri = uri
        self.economic = economic
        self.default_account: LocalAccount = None  # 发送签名交易时适用的默认地址
        self.result_type = 'auto'  # 交易返回的结果类型，包括：auto, txn, hash, receipt, event（仅适用于内置合约，其他合约必须要手动解析）
        # web3相关设置
        self.web3 = get_web3(uri)
        self.web3.middleware_onion.inject(geth_poa_middleware, layer=0)
        # self.hrp = self.web3.hrp
        self.chain_id = self.web3.platon.chain_id
        # 设置模块
        self.__init_web3__()
        self.__init_platon__()

    def __init_web3__(self):
        """ 设置web相关模块
        """
        self.platon = self.web3.platon
        self.txpool = self.web3.node.txpool
        self.personal = self.web3.node.personal
        self.admin = self.web3.node.admin
        self.debug = self.web3.debug

    def __init_platon__(self):
        """ 设置platon内置合约相关模块
        """
        if not self.economic:
            try:
                self.economic = new_economic(self.debug.economic_config())
            except IOError:
                warnings.warn('The debug api is not open, cannot get the economic data automatically')

        self.graphql = Graphql(f'{self.uri}/platon/graphql')
        self.calculator = Calculator(self)
        self.transfer = Transfer(self)
        self.restricting = Restricting(self)
        self.staking = Staking(self)
        self.delegate = Delegate(self)
        self.slashing = Slashing(self)
        self.govern = Govern(self)
        self.contract = Contract(self)

    @property
    def node_id(self):
        node_info = self.web3.node.admin.node_info()
        node_id = node_info['enode'].split('//')[1].split('@')[0]  # 请使用enode中的节点id
        return node_id

    @property
    def node_version(self):
        version_info = self.web3.node.admin.get_program_version()
        return version_info['Version']

    @property
    def bls_pubkey(self):
        node_info = self.web3.node.admin.node_info()
        return node_info['blsPubKey']

    @property
    def bls_proof(self):
        return self.web3.node.admin.get_schnorr_NIZK_prove()

    @property
    def version_sign(self):
        version_info = self.web3.node.admin.get_program_version()
        return version_info['Sign']

    @combomethod
    def create_account(self):
        """ 创建账户
        """
        return Account.create()

    @combomethod
    def create_hd_account(self):
        """ 创建HD账户
        """
        pass

    @combomethod
    def create_keystore(self, passphrase, key=None):
        """ 创建钱包文件
        """
        pass

    # @combomethod
    # def to_bech32_address(self, address, hrp=None):
    #     """ 任意地址转换为platon形式的bech32地址
    #     注意：非标准bech32地址
    #     """
    #     hrp = hrp or self.hrp or DEFAULT_HRP
    #     return to_bech32_address(address, hrp=hrp)

    @combomethod
    def to_checksum_address(self, address):
        """ 任意地址转换为checksum地址
        """
        return to_checksum_address(address)

    def wait_block(self, to_block, time_out=None):
        """ 等待块高
        """
        current_block = self.platon.block_number
        time_out = time_out or (to_block - current_block) * 3

        for i in range(time_out):
            time.sleep(1)
            current_block = self.platon.block_number

            if i % 10 == 0:
                logger.info(f'waiting block: {current_block} -> {to_block}')

            # 等待确定落链
            if current_block > to_block:
                logger.info(f'waiting block: {current_block} -> {to_block}')
                return

        raise TimeoutError('wait block timeout!')

    def wait_period(self,
                    period_type: Literal['round', 'consensus', 'epoch', 'increasing'] = 'epoch',
                    wait_count: int = 1,
                    ):
        """ 基于当前块高，等待n个指定周期
        """
        current_period, _, _ = self.calculator.get_period_info(period_type=period_type)
        dest_period = current_period + wait_count - 1  # 去掉当前的指定周期
        _, end_block = self.calculator.get_period_ends(dest_period, period_type=period_type)
        self.wait_block(end_block)

    def set_default_account(self, account: LocalAccount):
        """ 设置发送交易的默认账户
        """
        self.default_account = account

    def set_result_type(self,
                        result_type: Literal['auto', 'txn', 'hash', 'receipt', 'event']
                        ):
        """ 设置返回结果类型，建议设置为auto
        """
        self.result_type = result_type

    def send_transaction(self, txn: dict, private_key=None):
        """ 签名交易并发送，返回交易hash
        """
        if not private_key and self.default_account:
            private_key = self.default_account.key
        if not txn.get('nonce'):
            account = self.platon.account.from_key(private_key)
            txn['nonce'] = self.platon.get_transaction_count(account.address)

        signed_txn = self.platon.account.sign_transaction(txn, private_key)
        tx_hash = self.platon.send_raw_transaction(signed_txn.rawTransaction)
        return bytes(tx_hash).hex()

    @staticmethod
    def decode_data(receipt, func_id=None):
        return InnerContractEvent(func_id).processReceipt(receipt)

    def ec_recover(self, block_identifier):
        """ 使用keccak方式，解出区块的签名节点公钥
        """
        block = self.web3.platon.get_block(block_identifier)

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
        if not block.baseFeePerGas is None:
            raw_data.append(block.baseFeePerGas)
        hash_bytes = HexBytes(keccak(rlp.encode(raw_data)))
        signature_bytes = HexBytes(sign)
        signature_bytes_standard = to_standard_signature_bytes(signature_bytes)
        signature = Signature(signature_bytes=signature_bytes_standard)
        return remove_0x_prefix(HexStr(signature.recover_public_key_from_msg_hash(hash_bytes).to_hex()))
