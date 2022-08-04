import time

from platon.main import get_default_modules
from platon.middleware import gplaton_poa_middleware

from platon_aide.calculator import Calculator
from platon_aide.contract import Contract
from platon_aide.delegate import Delegate
from platon_aide.economic import new_economic, Economic
from platon_aide.govern import Govern
from platon_aide.slashing import Slashing
from platon_aide.staking import Staking
from platon_aide.transfer import Transfer
from platon_aide.graphqls import Graphql
from platon_aide.utils import get_web3, ec_recover


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
    """ 主类，platon各个子模块的集合体，同时支持创建账户、解码等非交易类的操作
    """

    def __init__(self,
                 uri: str,
                 gql_uri: str = None,
                 chain_id: int = None,
                 hrp: str = None,
                 economic: Economic = None,
                 closed_api: list = None,
                 ):
        self.uri = uri
        self.gql_uri = gql_uri
        # web3相关设置
        modules = get_modules(closed_api)
        self.web3 = get_web3(uri, chain_id, hrp, modules=modules)
        self.web3.middleware_onion.inject(gplaton_poa_middleware, layer=0)
        self.hrp = hrp or self.web3.hrp
        self.chain_id = chain_id or self.web3.platon.chain_id
        self.__set_web3_attr()
        # 属性对象设置
        self.economic = new_economic(self.debug.economic_config()) if self.debug else economic
        self.calculator = Calculator(self.web3, economic=self.economic)
        self.transfer = Transfer(self.web3)
        self.staking = Staking(self.web3, economic=self.economic)
        self.delegate = Delegate(self.web3, economic=self.economic)
        self.slashing = Slashing(self.web3)
        self.govern = Govern(self.web3)
        self.contract = Contract(self.web3)
        self.graphql = Graphql(self.gql_uri) if self.gql_uri else None

    def __set_web3_attr(self):
        self.platon = self.web3.platon
        self.admin = self.web3.node.admin if hasattr(self.web3, 'admin') else None
        self.txpool = self.web3.node.txpool if hasattr(self.web3.node, 'txpool') else None
        self.personal = self.web3.node.personal if hasattr(self.web3.node, 'personal') else None
        self.debug = self.web3.debug if hasattr(self.web3, 'debug') else None

    def set_default_account(self, account):
        """ 设置默认账户
        """
        self.transfer.set_default_account(account)
        self.staking.set_default_account(account)
        self.delegate.set_default_account(account)
        self.slashing.set_default_account(account)
        self.govern.set_default_account(account)
        self.contract.set_default_account(account)

    def set_result_type(self, result_type):
        self.transfer.set_result_type(result_type)
        self.staking.set_result_type(result_type)
        self.delegate.set_result_type(result_type)
        self.slashing.set_result_type(result_type)
        self.govern.set_result_type(result_type)
        self.contract.set_result_type(result_type)

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
        # todo: coding
        pass

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
