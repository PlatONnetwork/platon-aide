from typing import TYPE_CHECKING
from web3.datastructures import AttributeDict

from platon_aide.base.module import Module
from platon_aide.utils import contract_transaction

if TYPE_CHECKING:
    from platon_aide import Aide


class Staking(Module):

    def __init__(self, aide: "Aide"):
        super().__init__(aide, module_type='inner-contract')
        self.ADDRESS = self.aide.web3.ppos.staking.address

    @property
    def staking_info(self):
        candidate_info = self.get_candidate_info(self.aide.node_id)
        if candidate_info:
            return candidate_info
        raise AttributeError('the node has no staking information.')

    @contract_transaction()
    def create_staking(self,
                       amount=None,
                       balance_type=0,
                       node_id=None,
                       benefit_address=None,
                       node_name='',
                       external_id='',
                       details='',
                       website='',
                       reward_per=0,
                       version=None,
                       version_sign=None,
                       bls_pubkey=None,
                       bls_proof=None,
                       txn=None,
                       private_key=None,
                       ):

        if not benefit_address:
            benefit_account = self.aide.platon.account.from_key(private_key) if private_key else self.aide.default_account
            if not benefit_account:
                raise ValueError('the benefit address cannot be empty')

            benefit_address = benefit_account.address

        node_id = node_id or self.aide.node_id
        amount = amount or self.aide.economic.staking_limit
        version = version or self.aide.node_version
        version_sign = version_sign or self.aide.version_sign
        bls_pubkey = bls_pubkey or self.aide.bls_pubkey
        bls_proof = bls_proof or self.aide.bls_proof
        return self.aide.web3.ppos.staking.create_staking(balance_type, benefit_address, node_id, external_id,
                                                          node_name, website, details, amount, reward_per,
                                                          version, version_sign, bls_pubkey, bls_proof
                                                          )

    @contract_transaction()
    def increase_staking(self,
                         balance_type=0,
                         node_id=None,
                         amount=None,
                         txn=None,
                         private_key=None,
                         ):
        node_id = node_id or self.aide.node_id
        amount = amount or self.aide.economic.add_staking_limit
        return self.aide.web3.ppos.staking.increase_staking(node_id, balance_type, amount)

    @contract_transaction()
    def withdrew_staking(self, node_id=None, txn=None, private_key=None):
        node_id = node_id or self.aide.node_id
        return self.aide.web3.ppos.staking.withdrew_staking(node_id)

    @contract_transaction()
    def edit_candidate(self,
                       benifit_address=None,
                       node_id=None,
                       reward_per=None,
                       external_id=None,
                       node_name=None,
                       website=None,
                       details=None,
                       txn=None,
                       private_key=None,
                       ):
        node_id = node_id or self.aide.node_id
        return self.aide.web3.ppos.staking.edit_staking(node_id, benifit_address, reward_per, external_id,
                                                        node_name, website, details
                                                        )

    def get_verifier_list(self):
        verifier_list = self.aide.web3.ppos.staking.get_verifier_list()
        return [StakingInfo(verifier) for verifier in verifier_list]

    def get_validator_list(self):
        validator_list = self.aide.web3.ppos.staking.get_validator_list()
        return [StakingInfo(validator) for validator in validator_list]

    def get_candidate_list(self):
        candidate_list = self.aide.web3.ppos.staking.get_candidate_list()
        return [StakingInfo(candidate) for candidate in candidate_list]

    def get_candidate_info(self, node_id=None):
        node_id = node_id or self.aide.node_id
        staking_info = self.aide.web3.ppos.staking.get_candidate_info(node_id)
        if staking_info == 'Query candidate info failed:Candidate info is not found':
            return None
        else:
            return StakingInfo(staking_info)

    def get_block_reward(self):
        return self.aide.web3.ppos.staking.get_block_reward()

    def get_staking_reward(self):
        return self.aide.web3.ppos.staking.get_staking_reward()

    def get_avg_block_time(self):
        return self.aide.web3.ppos.staking.get_avg_block_time()


class StakingInfo(AttributeDict):
    """ 质押信息的属性字典类
    """
    NodeId: str
    StakingAddress: str
    BenefitAddress: str
    RewardPer: int
    NextRewardPer: int
    StakingTxIndex: int
    ProgramVersion: int
    Status: int
    StakingEpoch: int
    StakingBlockNum: int
    Shares: int
    Released: int
    ReleasedHes: int
    RestrictingPlan: int
    RestrictingPlanHes: int
    ExternalId: int
    NodeName: str
    Website: str
    Details: str
    DelegateEpoch: int
    DelegateTotal: int
    DelegateTotalHes: int
    DelegateRewardTotal: int
