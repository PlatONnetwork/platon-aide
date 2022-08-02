import warnings
from platon import Account
from platon import Web3
from platon_typing import Address

from platon_aide.utils import send_transaction, get_transaction_result


class Module:
    address: None

    def __init__(self, web3: Web3):
        self.web3 = web3
        self.default_account: Account = None
        # todo: 设置默认地址
        self.default_address: Address = None

        # 模块类型，目前仅用于判断是否可以返回event，包括：'inner-contract'
        self._module_type = ''
        # 返回结果类型，包括：txn, hash, receipt, event(仅内置合约可用)
        self._result_type = 'receipt'

    def set_default_account(self, account):
        self.default_account = account

    def _get_node_info(self):
        if hasattr(self.web3.node, 'admin'):
            node_info = self.web3.node.admin.node_info()
            # self._node_id = node_info['id']                                # todo: 增加不使用id字段的注释
            self._node_id = node_info['enode'].split('//')[1].split('@')[0]  # 请使用enode中的节点
            self._bls_pubkey = node_info['blsPubKey']
            self._bls_proof = self.web3.node.admin.get_schnorr_NIZK_prove()
            version_info = self.web3.node.admin.get_program_version()
            self._version = version_info['Version']
            self._version_sign = version_info['Sign']

    def send_transaction(self, txn, private_key, result_type=''):
        result_type = result_type or self._result_type

        if not private_key and self.default_account:
            private_key = self.default_account.privateKey.hex()[2:]

        tx_hash = send_transaction(self.web3, txn, private_key)
        return self._get_transaction_result(tx_hash, result_type)

    def _get_transaction_result(self, tx_hash, result_type):
        if result_type == 'event' and self._module_type != 'inner-contract':
            raise TypeError('result type "event" only support inner contract')

        return get_transaction_result(self.web3, tx_hash, result_type)

    def set_result_type(self, result_type):
        if result_type not in ('txn', 'hash', 'receipt', 'event'):
            raise ValueError('Unrecognized value')

        if result_type == 'event' and self._module_type != 'inner-contract':
            warnings.warn(f'result type "event" only support inner contract, '
                    f'try set {self.__class__.__name__} result type to "receipt"', RuntimeWarning)
            result_type = 'receipt'

        self._result_type = result_type
