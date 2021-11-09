from economic import gas
from main import Module, custom_return


class Transfer(Module):

    # 转账交易
    def transfer(self, to_address, amount, txn=None, private_key=None):
        base_txn = {
            "to": to_address,
            "gasPrice": self.web3.platon.gas_price,
            "gas": gas.Transfer_gas,
            "data": '',
            "chainId": self.web3.chain_id,
            "value": amount,
        }
        if txn:
            txn = base_txn.update(txn)
        if self.returns == 'txn':
            return txn
        return self.send_transaction(txn, private_key, self.returns)

    @custom_return
    def restricting(self, release_address, plans, txn=gas.Restricting_gas, private_key=None):
        return self.web3.restricting.create_restricting(release_address, plans)

    def get_balance(self, account, block_identifier=None):
        return self.web3.platon.get_balance(account, block_identifier)

    def get_restricting_info(self, release_address):
        return self.web3.restricting.get_restricting_info(release_address)
