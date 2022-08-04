from gql import gql

from platon_aide.utils import get_gql


class Graphql:

    def __init__(self, uri: str):
        self.client = get_gql(uri)

    def execute(self, content):
        return self.client.execute(gql(content))
