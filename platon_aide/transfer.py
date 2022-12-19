from platon_aide.base.module import Module


class Transfer(Module):
    transferGas: int = 21000

    def transfer(self, to_address, amount, txn=None, private_key=None):
        """ 发送转账交易
        """
        base_txn = {
            "to": to_address,
            "gasPrice": self.aide.platon.gas_price,
            "gas": self.transferGas,
            "data": '',
            "chainId": self.aide.chain_id,
            "value": amount,
        }

        if txn:
            base_txn.update(txn)

        return self._transaction_handler_(base_txn, private_key=private_key)

    def get_balance(self, address, block_identifier=None):
        """ 查询自由金额的余额
        """
        return self.aide.platon.get_balance(address, block_identifier)
