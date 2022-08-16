from platon_aide.base.module import Module


class Transfer(Module):
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
