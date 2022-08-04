from platon_aide.base.module import Module
from platon_aide.utils import contract_transaction


class Transfer(Module):
    transferGas: int = 21000
    restrictingGas: int = 100000

    # 转账交易
    # todo: 交易不支持返回类型为ic-event
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

    @contract_transaction
    def restricting(self, release_address, plans, txn=None, private_key=None):
        return self.web3.restricting.create_restricting(release_address, plans)

    def get_balance(self, account, block_identifier=None):
        return self.web3.platon.get_balance(account, block_identifier)

    def get_restricting_info(self, release_address):
        return self.web3.restricting.get_restricting_info(release_address)
