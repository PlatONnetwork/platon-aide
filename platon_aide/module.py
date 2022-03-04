from platon import Account
from platon import Web3

from platon_aide.utils import send_transaction


class Module:
    address: None

    def __init__(self, web3: Web3):
        self.web3 = web3
        self.default_account: Account = None
        self.returns = 'receipt'  # 包含：txn, hash, receipt, ic-event(仅内置合约可用)

    def _get_node_info(self):
        node_info = self.web3.node.admin.node_info()
        # self.node_id = node_info['id']
        self.node_id = node_info['enode'].split('//')[1].split('@')[0]
        self.bls_pubkey = node_info['blsPubKey']
        self.bls_proof = self.web3.node.admin.get_schnorr_NIZK_prove()
        version_info = self.web3.node.admin.get_program_version()
        self.version = version_info['Version']
        self.version_sign = version_info['Sign']

    def send_transaction(self, txn, private_key, returns='receipt'):
        return send_transaction(self.web3, txn, private_key, returns)

    def set_default_account(self, account):
        self.default_account = account

    def set_returns(self, returns):
        if returns in ('txn', 'hash', 'receipt', 'ic-event'):
            self.returns = returns
        else:
            raise ValueError('Unrecognized value')
