from platon import Web3

from platon_aide.base.module import Module
from platon_aide.utils import contract_transaction


class Transfer(Module):

    def __init__(self, web3: Web3):
        super().__init__(web3)
        self._transfer = TransferBase(web3)
        self._restricting = RestrictingBase(web3)

    def transfer(self, to_address, amount, txn=None, private_key=None):
        return self._transfer.transfer(to_address, amount, txn=txn, private_key=private_key)

    def restricting(self, release_address, plans, txn=None, private_key=None):
        return self._restricting.restricting(release_address, plans, txn=txn, private_key=private_key)

    def get_balance(self, address, block_identifier=None):
        return self._transfer.get_balance(address, block_identifier)

    def get_restricting_info(self, release_address):
        return self._restricting.get_restricting_info(release_address)


class TransferBase(Module):
    transferGas: int = 21000

    # 转账交易
    def transfer(self, to_address, amount, txn=None, private_key=None):
        base_txn = {
            "to": to_address,
            "gasPrice": self.web3.platon.gas_price,
            "gas": self.transferGas,
            "data": '',
            "chainId": self.web3.chain_id,
            "value": amount,
        }
        if txn:
            base_txn.update(txn)
        txn = base_txn
        if self._result_type == 'txn':
            return txn
        return self.send_transaction(txn, private_key, self._result_type)

    def get_balance(self, address, block_identifier=None):
        return self.web3.platon.get_balance(address, block_identifier)


class RestrictingBase(Module):
    restrictingGas: int = 100000

    def __init__(self, web3: Web3):
        super().__init__(web3)
        self._module_type = 'inner-contract'
        self._result_type = 'event'

    @contract_transaction
    def restricting(self, release_address, plans, txn=None, private_key=None):
        return self.web3.restricting.create_restricting(release_address, plans)

    def get_restricting_info(self, release_address):
        return self.web3.restricting.get_restricting_info(release_address)
