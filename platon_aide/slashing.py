from typing import TYPE_CHECKING

from platon_aide.base.module import Module
from platon_aide.utils import contract_transaction

if TYPE_CHECKING:
    from platon_aide import Aide


class Slashing(Module):

    def __init__(self, aide: "Aide"):
        super().__init__(aide, module_type='inner-contract')
        self.ADDRESS = self.aide.web3.ppos.slashing.address

    @contract_transaction()
    def report_duplicate_sign(self,
                              report_type,
                              data,
                              txn=None,
                              private_key=None,
                              ):
        return self.aide.web3.ppos.slashing.report_duplicate_sign(report_type, data)

    def check_duplicate_sign(self,
                             report_type,
                             block_identifier,
                             node_id=None,
                             ):
        node_id = node_id or self.aide.node_id
        return self.aide.web3.ppos.slashing.check_duplicate_sign(report_type, node_id, block_identifier)
