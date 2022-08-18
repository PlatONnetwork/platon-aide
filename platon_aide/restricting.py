from platon import Web3

from platon_aide.base import Module
from platon_aide.utils.utils import contract_transaction


class Restricting(Module):
    restrictingGas: int = 100000

    def __init__(self, web3: Web3):
        super().__init__(web3)
        self._module_type = 'inner-contract'
        self._result_type = 'event'

    @contract_transaction()
    def restricting(self, release_address, plans, txn=None, private_key=None):
        return self.web3.restricting.create_restricting(release_address, plans)

    def get_restricting_info(self, release_address):
        return self.web3.restricting.get_restricting_info(release_address)
