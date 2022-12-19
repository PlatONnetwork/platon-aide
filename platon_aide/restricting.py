from typing import TYPE_CHECKING

from platon_aide.base import Module
from platon_aide.utils.utils import contract_transaction

if TYPE_CHECKING:
    from platon_aide import Aide


class Restricting(Module):
    restrictingGas: int = 100000

    def __init__(self, aide: "Aide"):
        super().__init__(aide, module_type='inner-contract')
        self.ADDRESS = self.aide.web3.restricting.address
        self._result_type = 'event'

    @contract_transaction()
    def restricting(self, release_address, plans, txn=None, private_key=None):
        return self.aide.web3.restricting.create_restricting(release_address, plans)

    def get_restricting_info(self, release_address):
        return self.aide.web3.restricting.get_restricting_info(release_address)
