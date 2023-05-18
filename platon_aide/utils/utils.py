import functools
import json
import os
import sys
from os.path import abspath
from typing import cast

from web3 import HTTPProvider, WebsocketProvider, IPCProvider
from platon import Web3
from web3._utils.threads import Timeout
from web3.datastructures import AttributeDict
from web3.exceptions import ContractLogicError
from platon.types import CodeData

from gql import Client
from gql.transport.aiohttp import AIOHTTPTransport
from gql.transport.websockets import WebsocketsTransport


def get_web3(uri, timeout=10, modules=None):
    """ 通过rpc uri，获取web3对象。可以兼容历史platon版本
    """
    if uri.startswith('http'):
        provider = HTTPProvider
    elif uri.startswith('ws'):
        provider = WebsocketProvider
    elif uri.startswith('ipc'):
        provider = IPCProvider
    else:
        raise ValueError(f'unidentifiable uri {uri}')

    with Timeout(timeout) as t:
        while True:
            web3 = Web3(provider(uri), modules=modules)
            if web3.isConnected():
                break
            t.sleep(1)

    return web3


def get_gql(uri):
    """ 通过gql uri，获取gql对象。
    # todo: 增加超时处理
    """
    if uri.startswith('http'):
        transport = AIOHTTPTransport
    elif uri.startswith('ws'):
        transport = WebsocketsTransport
    else:
        raise ValueError(f'unidentifiable uri {uri}')

    return Client(transport=transport(uri), fetch_schema_from_transport=True)


def contract_call(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        return func(self, *args, **kwargs).call()

    return wrapper


# 合约交易装饰器，仅用于接受参数
def contract_transaction(func_id=None, default_txn=None):
    # 实际装饰器
    def decorator(func):

        @functools.wraps(func)
        def wrapper(self, *args, txn: dict = None, private_key=None, **kwargs):
            """
            """
            # 合并交易体
            if txn:
                if default_txn:
                    default_txn.update(txn)
                    txn = default_txn
            else:
                txn = default_txn if default_txn else {}

            # 填充from地址，以免合约交易在预估gas时检验地址失败
            if not txn.get('from'):
                account = self.aide.platon.account.from_key(private_key) if private_key else self.aide.default_account
                if account:
                    txn['from'] = account.address

            # 构造合约方法对象
            if func.__name__ == 'fit_func':
                # solidity合约方法不传入private key参数，避免abi解析问题
                fn = func(self, *args, **kwargs)
            else:
                # 内置合约有时候需要用到私钥信息，用于生成参数的默认值，如：staking
                fn = func(self, *args, private_key=private_key, **kwargs)

            # 构建合约交易体dict
            try:
                txn = fn.build_transaction(txn)
            except ContractLogicError as e:
                # 预估gas出现合约逻辑错误时，不再报错
                err = str(e)
                # 判断其是否为内置合约错误
                # todo: 优化这一段逻辑
                if err.startswith('inner contract exec failed: '):
                    event = err.split('inner contract exec failed: ')[1]
                    data = json.loads(event.replace('\'', '"'))
                    return cast(CodeData, AttributeDict.recursive(data))
                raise e

            return self._transaction_handler_(txn, func_id=func_id, private_key=private_key)

        return wrapper

    return decorator


def execute_cmd(cmd):
    r = os.popen(cmd)
    out = r.read()
    r.close()
    return out


def mock_duplicate_sign(dtype, sk, blskey, block_number, epoch=0, view_number=0, block_index=0, index=0):
    if sys.platform in "linux,linux2":
        tool_file = abspath("tool/linux/duplicateSign")
        execute_cmd("chmod +x {}".format(tool_file))
    else:
        tool_file = abspath("tool/win/duplicateSign.exe")
    print("{} -dtype={} -sk={} -blskey={} -blockNumber={} -epoch={} -viewNumber={} -blockIndex={} -vindex={}".format(
        tool_file, dtype, sk, blskey, block_number, epoch, view_number, block_index, index))
    output = execute_cmd(
        "{} -dtype={} -sk={} -blskey={} -blockNumber={} -epoch={} -viewNumber={} -blockIndex={} -vindex={}".format(
            tool_file, dtype, sk, blskey, block_number, epoch, view_number, block_index, index))
    print(output)
    if not output:
        raise Exception("unable to use double sign tool")
    return output.strip("\n")
