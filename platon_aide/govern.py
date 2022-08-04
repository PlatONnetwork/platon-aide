from time import time

from platon import Web3
from platon.datastructures import AttributeDict

from platon_aide.base.module import Module
from platon_aide.utils import contract_transaction

second = lambda: str(int(time()))


def to_attribute_proposal(proposal):
    _type = proposal['ProposalType']
    wizard = {
        1: TextProposal,
        2: VersionProposal,
        3: ParamProposal,
        4: CancelProposal,
    }
    attribute_proposal = wizard[_type]
    return attribute_proposal(proposal)


class Govern(Module):
    governGasPrice: int = 2100000000000000

    def __init__(self, web3: Web3):
        super().__init__(web3)
        self._module_type = 'inner-contract'
        self._result_type = 'event'
        self._get_node_info()

    @property
    def chain_version(self):
        version = self.web3.pip.get_chain_version()
        version_byte = int(version).to_bytes(length=3, byteorder='big')
        return ChainVersion({
            'integer': version,
            'major': version_byte[0],
            'minor': version_byte[1],
            'patch': version_byte[2],
        })

    @contract_transaction
    def version_proposal(self,
                         version,
                         voting_rounds=4,
                         pip_number=second(),
                         node_id=None,
                         txn=None,
                         private_key=None,
                         ):
        """ 提交版本提案，实现链上共识硬分叉版本的升级
        """
        node_id = node_id or self._node_id
        return self.web3.pip.submit_version_proposal(node_id, pip_number, version, voting_rounds)

    @contract_transaction
    def param_proposal(self,
                       module,
                       name,
                       value,
                       pip_number=second(),
                       node_id=None,
                       txn=None,
                       private_key=None,
                       ):
        """ 提交参数提案，修改链上可治理参数
        """
        node_id = node_id or self._node_id
        return self.web3.pip.submit_param_proposal(node_id, pip_number, module, name, value)

    @contract_transaction
    def cancel_proposal(self,
                        proposal_id,
                        voting_rounds=4,
                        node_id=None,
                        pip_number=second(),
                        txn=None,
                        private_key=None,
                        ):
        """ 提交取消提案
        """
        node_id = node_id or self._node_id
        return self.web3.pip.submit_cancel_proposal(node_id, pip_number, voting_rounds, proposal_id)

    @contract_transaction
    def text_proposal(self,
                      pip_number=second(),
                      node_id=None,
                      txn=None,
                      private_key=None,
                      ):
        """ 提交文本提案，文本提案不对链上产生影响，仅做pip投票意见收集作用
        """
        node_id = node_id or self._node_id
        return self.web3.pip.submit_text_proposal(node_id, pip_number)

    @contract_transaction
    def vote(self,
             proposal_id,
             option,
             node_id=None,
             version=None,
             version_sign=None,
             txn=None,
             private_key=None,
             ):
        """ 对提案进行投票
        """
        node_id = node_id or self._node_id
        version = version or self._version
        version_sign = version_sign or self._version_sign
        return self.web3.pip.vote(node_id, proposal_id, option, version, version_sign)

    @contract_transaction
    def declare_version(self,
                        node_id=None,
                        version=None,
                        version_sign=None,
                        txn=None,
                        private_key=None,
                        ):
        """ 向链上声明节点版本，以获得参与共识出块的资格
        """
        node_id = node_id or self._node_id
        version = version or self._version
        version_sign = version_sign or self._version_sign
        return self.web3.pip.declare_version(node_id, version, version_sign)

    def get_proposal(self, proposal_id):
        """ 获取提案信息
        """
        proposal = self.web3.pip.get_proposal(proposal_id)
        return to_attribute_proposal(proposal)

    def get_proposal_result(self, proposal_id):
        """ 获取提案投票结果信息
        """
        proposal_result = self.web3.pip.get_proposal_result(proposal_id)
        if not proposal_result:
            raise ValueError('proposal is not found.')
        if type(proposal_result) is str:
            raise ValueError(f'{proposal_result}.')

        partici_count = proposal_result['yeas'] + proposal_result['nays'] + proposal_result['abstentions']
        proposal_result['particiRatio'] = partici_count / proposal_result['accuVerifiers']
        proposal_result['yeasRatio'] = proposal_result['yeas'] / partici_count if partici_count else 0

        return ProposalResult(proposal_result)

    def get_proposal_votes(self, proposal_id, block_identifier='latest'):
        """ 获取提案实时投票信息
        """
        proposal_votes = self.web3.pip.get_proposal_votes(proposal_id, block_identifier)
        if not proposal_votes:
            raise ValueError('proposal is not found.')

        partici_count = proposal_votes[1] + proposal_votes[2] + proposal_votes[3]

        return ProposalVotes({
            'accuVerifiers': proposal_votes[0],
            'yeas': proposal_votes[1],
            'nays': proposal_votes[2],
            'abstentions': proposal_votes[3],
            'particiRatio': partici_count / proposal_votes[0],
            'yeasRatio': proposal_votes[1] / partici_count if partici_count else 0,
        })

    def proposal_list(self, proposal_type=None):
        """ 获取提案列表，可以根据提案类型过滤
        """
        proposal_list = self.web3.pip.proposal_list()
        if type(proposal_list) is not list:
            raise ValueError('proposals is not found.')

        return [to_attribute_proposal(proposal) for proposal in proposal_list]

    def get_govern_param(self, module, name):
        """ 获取可治理参数的值
        """
        return self.web3.pip.get_govern_param(module, name)

    def govern_param_list(self, module=None):
        """ 获取可治理参数列表信息
        """
        return self.web3.pip.govern_param_list(module)


class ChainVersion(AttributeDict):
    integer: int
    major: int
    minor: int
    patch: int


class BaseProposal(AttributeDict):
    ProposalID: str
    Proposer: str
    ProposalType: int
    PIPID: str
    SubmitBlock: int
    EndVotingBlock: int


class VersionProposal(BaseProposal):
    EndVotingRounds: int
    ActiveBlock: int
    NewVersion: int


class ParamProposal(BaseProposal):
    Module: str
    Name: str
    NewVersion: str


class CancelProposal(BaseProposal):
    EndVotingRounds: str
    EndVotingBlock: str
    TobeCanceled: str


class TextProposal(BaseProposal):
    pass


class ProposalVotes(AttributeDict):
    accuVerifiers: int
    yeas: int
    nays: int
    abstentions: int
    particiRatio: float
    yeasRatio: float


class ProposalResult(ProposalVotes):
    proposalID: str
    status: int
    canceledBy: str
