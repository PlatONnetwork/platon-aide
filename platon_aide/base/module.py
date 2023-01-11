from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from platon_aide import Aide


class Module:

    def __init__(self, aide: "Aide", module_type: Literal['', 'inner-contract'] = ''):
        self.aide = aide
        # 模块类型，当前仅用于判断是否自动解析内置合约的事件
        self.module_type = module_type

    def _transaction_handler_(self,
                              txn,
                              func_id=None,
                              private_key=None,
                              ):
        """
        发送签名交易，并根据结果类型获取交易结果

        Args:
            txn: 要发送的交易dict
            func_id: 方法id（仅内置合约需要用到）
            private_key: 用于签名交易的私钥
        """
        if self.aide.result_type == "txn":
            return txn

        tx_hash = self.aide.send_transaction(txn, private_key=private_key)

        if self.aide.result_type == 'hash':
            return tx_hash

        receipt = self.aide.web3.platon.wait_for_transaction_receipt(tx_hash)
        if type(receipt) is bytes:
            receipt = receipt.decode('utf-8')

        if self.module_type != 'inner-contract' and (self.aide.result_type == 'receipt' or self.aide.result_type == 'auto'):
            return receipt

        if self.module_type == 'inner-contract' and (self.aide.result_type == 'event' or self.aide.result_type == 'auto'):
            return self.aide.decode_data(receipt, func_id=func_id)

        raise ValueError(f'unsupported module type {self.module_type} or unknown result type {self.aide.result_type}')
