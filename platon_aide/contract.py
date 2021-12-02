from functools import wraps
from typing import Literal

from platon._utils.abi import filter_by_name
from platon.contract import ContractFunction

from module import Module
from utils import contract_call, contract_transaction


class Contract(Module):

    def __call__(self,
                 abi,
                 bytecode=None,
                 address=None,
                 vm_type: Literal['solidity', 'wasm'] = 'solidity',
                 ):
        self.abi = abi
        self.bytecode = bytecode
        self.vm_type = vm_type
        self.__build_contract(address)

    def __build_contract(self, address):
        self.contract = self.web3.platon.contract(address=address, abi=self.abi, bytecode=self.bytecode, vm_type=self.vm_type)
        self.address = address
        self.functions = self.contract.functions
        self.events = self.contract.events
        self._set_functions(self.contract.functions)
        self._set_events(self.contract.events)
        self._set_fallback(self.contract.fallback)

    def deploy(self, txn=None, private_key=None, *args, **kwargs):
        if self.address:
            raise ValueError('contract address already exists.')

        private_key = private_key or self.default_account.privateKey
        if not private_key:
            raise ValueError('private key is required.')

        txn = self.contract.constructor(*args, **kwargs).build_transaction(txn)

        receipt = self.send_transaction(txn, private_key)
        self.__build_contract(address=receipt['contractAddress'])

        return self

    def _set_functions(self, functions):
        for func in functions:
            warp_function = self._function_wrap(getattr(functions, func))
            setattr(self, func, warp_function)

    def _set_events(self, events):
        for event in events:
            # 通过方法名获取方法
            warp_event = self._event_wrap(event)
            setattr(self, event.event_name, warp_event)

    def _set_fallback(self, fallback):
        if type(fallback) is ContractFunction:
            warp_fallback = self._fallback_wrap(fallback)
            setattr(self, fallback, warp_fallback)
        else:
            self.fallback = fallback

    def _function_wrap(self, func):

        fn_abi = filter_by_name(func.fn_name, self.abi)
        if len(fn_abi) != 1:
            raise ValueError('The method not found in the ABI, or more than one.')

        if fn_abi[0].get('stateMutability') == 'view':
            return contract_call(func)
        else:
            return contract_transaction(func)

    @staticmethod
    def _event_wrap(func):

        @wraps(func)
        def wrapper(*args, **kwargs):
            return func().processReceipt(*args, **kwargs)

        return wrapper

    @staticmethod
    def _fallback_wrap(func):
        return contract_transaction(func)
