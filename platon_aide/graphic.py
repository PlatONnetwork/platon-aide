from platon import Web3
from gql import gql

from platon_aide.module import Module
from platon_aide.utils import get_gql


class Graphql(Module):

    def __init__(self, uri: str, web3: Web3 = None):
        super().__init__(web3)
        self._gql = get_gql(uri)

    def execute(self, content):
        return self._gql.execute(gql(content))
