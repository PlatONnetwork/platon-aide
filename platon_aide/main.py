import time
from platon import Web3, HTTPProvider, WebsocketProvider, IPCProvider
from platon.middleware import gplaton_poa_middleware

from delegate import Delegate
from economic import gas, Economic
from govern import Govern
from contract import Contract
from module import Module
from slashing import Slashing
from staking import Staking
from transfer import Transfer
from utils import send_transaction, ec_recover


def get_web3(uri, chain_id=None, hrp=None):
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

    return Web3(provider(uri), chain_id=chain_id, hrp=hrp)


class PlatonAide:
    """ 主类，platon各个子模块的集合体，同时支持创建账户、解码等非交易类的操作
    """

    def __init__(self, uri: str, chain_id: int = None, hrp: str = None):
        self.uri = uri
        self.web3 = get_web3(uri, chain_id, hrp)
        self.web3.middleware_onion.inject(gplaton_poa_middleware, layer=0)
        self.hrp = hrp or self.web3.hrp
        self.chain_id = chain_id or self.web3.platon.chain_id
        # 加入接口和模块
        self.platon = self.web3.platon
        self.admin = self.web3.node.admin
        self.personal = self.web3.node.personal
        self.txpool = self.web3.node.txpool
        self.debug = self.web3.debug
        # self.economic = gas
        self.economic = Economic(self.web3)
        self.transfer = Transfer(self.web3)
        self.staking = Staking(self.web3)
        self.govern = Govern(self.web3)
        self.solidity = Contract(self.web3)
        self.delegate = Delegate(self.web3)
        self.slashing = Slashing(self.web3)

    def set_returns(self, returns):
        self.transfer.set_returns(returns)
        self.staking.set_returns(returns)
        self.govern.set_returns(returns)
        # self.solidity.set_returns(returns)
        self.delegate.set_returns(returns)
        self.slashing.set_returns(returns)

    def create_account(self):
        """ 创建账户
        """
        account = self.platon.account.create(hrp=self.hrp)
        address = account.address
        private_key = account.privateKey.hex()[2:]
        return address, private_key

    def create_hd_account(self):
        """ 创建HD账户
        """
        # todo: coding  初版先不用写这个
        pass

    def send_transaction(self, txn, private_key, returns='receipt'):
        """ 签名交易并发送
        """
        return send_transaction(self.web3, txn, private_key, returns)

    def wait_block(self, to_block=None, interval=3):
        """ 等待块高
        """
        current_block = self.platon.block_number
        while current_block < to_block:
            time.sleep(interval)
            current_block = self.platon.block_number

    def ec_recover(self, block_identifier):
        """ 获取出块节点公钥
        """
        block = self.web3.platon.get_block(block_identifier)
        return ec_recover(block)

    def set_default_account(self, account):

        """ 设置默认账户
        """
        self.transfer.set_default_account(account)
        self.staking.set_default_account(account)
        self.govern.set_default_account(account)
        # self.solidity.set_default_account(account)
        self.delegate.set_default_account(account)
        self.slashing.set_default_account(account)