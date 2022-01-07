from platon import Web3

from platon_aide.module import Module
from platon_aide.utils import contract_transaction


class Slashing(Module):

    def __init__(self, web3: Web3):
        super().__init__(web3)
        self.returns = 'ic-event'
        self._get_node_info()

    @contract_transaction
    def report_duplicate_sign(self,
                              report_type,
                              data,
                              txn=None,
                              private_key=None,
                              ):
        return self.web3.ppos.slashing.report_duplicate_sign(report_type, data)

    def check_duplicate_sign(self,
                             report_type,
                             block_identifier,
                             node_id=None,
                             ):
        node_id = node_id or self.node_id
        return self.web3.ppos.slashing.check_duplicate_sign(report_type, node_id, block_identifier)
