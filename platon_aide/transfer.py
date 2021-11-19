from module import Module
from economic import gas
from utils import contract_transaction


class Transfer(Module):

    # 转账交易
    def transfer(self, to_address, amount, txn=None, private_key=None):
        base_txn = {
            "to": to_address,
            "gasPrice": self.web3.platon.gas_price,
            "gas": gas.transferGas,
            "data": '',
            "chainId": self.web3.chain_id,
            "value": amount,
        }
        if txn:
            base_txn.update(txn)
        txn = base_txn
        if self.returns == 'txn':
            return txn
        private_key = private_key or self.default_account.privateKey.hex()[2:]
        return self.send_transaction(txn, private_key, self.returns)

    @contract_transaction
    def restricting(self, release_address, plans, txn=gas.restrictingGas, private_key=None):
        return self.web3.restricting.create_restricting(release_address, plans)

    def get_balance(self, account, block_identifier=None):
        return self.web3.platon.get_balance(account, block_identifier)

    def get_restricting_info(self, release_address):
        return self.web3.restricting.get_restricting_info(release_address)
