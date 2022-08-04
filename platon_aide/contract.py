import warnings
from functools import wraps, partial
from typing import Literal
from platon._utils.abi import filter_by_name
from platon.contract import ContractFunction
from platon.types import ABI
from platon_typing import HexStr, AnyAddress

from platon_aide.base.module import Module
from platon_aide.utils import contract_call, contract_transaction


class Contract(Module):
    abi: ABI = None
    bytecode: HexStr = None
    address: AnyAddress = None
    vm_type: str = None

    def init(self,
             abi,
             bytecode=None,
             address=None,
             vm_type: Literal['solidity', 'wasm'] = 'solidity',
             ):
        self.__build_contract(abi, bytecode, address, vm_type)
        return self

    def deploy(self,
               abi,
               bytecode,
               vm_type: Literal['solidity', 'wasm'] = 'solidity',
               txn=None,
               private_key=None,
               *init_args,
               **init_kwargs):
        if self.address:
            warnings.warn(f'contract {self.address} already exists, it will be replaced.', RuntimeWarning)

        _temp_origin = self.web3.platon.contract(abi=abi, bytecode=bytecode, vm_type=vm_type)
        txn = _temp_origin.constructor(*init_args, **init_kwargs).build_transaction(txn)
        receipt = self.send_transaction(txn, private_key)

        address = receipt.get('contractAddress')
        if not address:
            raise Exception(f'deploy contract failed, because: {receipt}.')

        self.__build_contract(abi, bytecode, address, vm_type)

        return self

    def __build_contract(self,
                         abi,
                         bytecode=None,
                         address=None,
                         vm_type: Literal['solidity', 'wasm'] = 'solidity',
                         ):
        self.abi = abi
        self.bytecode = bytecode
        self.address = address
        self.vm_type = vm_type
        self._origin = self.web3.platon.contract(address=self.address, abi=self.abi, bytecode=self.bytecode, vm_type=self.vm_type)
        self.functions = self._origin.functions
        self.events = self._origin.events
        self._set_functions(self._origin.functions)
        self._set_events(self._origin.events)
        self._set_fallback(self._origin.fallback)

    def _set_functions(self, functions):
        # 合约event和function不会重名，因此不用担心属性已存在
        for func in functions:
            warp_function = self._function_wrap(getattr(functions, func))
            setattr(self, func, warp_function)

    def _set_events(self, events):
        # 合约event和function不会重名，因此不用担心属性已存在
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
        fn_abis = filter_by_name(func.fn_name, self.abi)
        if len(fn_abis) == 0:
            raise ValueError('The method ABI is not found.')

        # 对于重载方法，仅取其一个，但需要其方法类型相同
        # todo: 此处理存在隐患
        fn_abi = fn_abis[0]
        for _abi in fn_abis:
            if _abi.get('stateMutability') != fn_abi.get('stateMutability'):
                raise ValueError('override method are of different types')

        # 忽略首个参数 'self'，以适配公共合约包装类
        def fit_func(__self__, *args, **kwargs):
            return func(*args, **kwargs)

        if fn_abi.get('stateMutability') in ['view', 'pure']:
            return partial(contract_call(fit_func), self)
        else:
            return partial(contract_transaction(fit_func), self)

    @staticmethod
    def _event_wrap(func):

        @wraps(func)
        def wrapper(*args, **kwargs):
            return func().processReceipt(*args, **kwargs)

        return wrapper

    @staticmethod
    def _fallback_wrap(func):
        return contract_transaction(func)
