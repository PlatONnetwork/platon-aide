from typing import TYPE_CHECKING
from web3.datastructures import AttributeDict

from platon_aide.base.module import Module
from platon_aide.utils import contract_transaction

if TYPE_CHECKING:
    from platon_aide import Aide


class Delegate(Module):

    def __init__(self, aide: "Aide"):
        super().__init__(aide, module_type='inner-contract')
        self.ADDRESS = self.aide.web3.ppos.delegate.delegateBase.address
        self.REWARD_ADDRESS = self.aide.web3.ppos.delegate.delegateReward.address

    @property
    def staking_block_number(self):
        return self.aide.staking.staking_info.StakingBlockNum

    @contract_transaction()
    def delegate(self,
                 amount=None,
                 balance_type=0,
                 node_id=None,
                 txn=None,
                 private_key=None,
                 ):
        """ 委托节点，以获取节点的奖励分红
        """
        amount = amount or self.aide.economic.delegate_limit
        node_id = node_id or self.aide.node_id
        return self.aide.web3.ppos.delegate.delegate(node_id, balance_type, amount)

    @contract_transaction(1005)
    def withdrew_delegate(self,
                          amount=0,
                          staking_block_identifier=None,
                          node_id=None,
                          txn=None,
                          private_key=None,
                          ):
        """
        撤回对节点的委托，可以撤回部分委托
        注意：因为节点可能进行过多次质押/撤销质押，会使得委托信息遗留，因此撤回委托时必须指定节点质押区块
        """
        node_id = node_id or self.aide.node_id
        amount = amount or self.aide.economic.delegate_limit
        staking_block_identifier = staking_block_identifier or self.aide.staking.staking_info.StakingBlockNum

        return self.aide.web3.ppos.delegate.withdrew_delegate(node_id,
                                                              staking_block_identifier,
                                                              amount,
                                                              )

    @contract_transaction(1006)
    def redeem_delegate(self,
                        txn=None,
                        private_key=None,
                        ):
        """
        领取已经解锁的委托金
        """
        return self.aide.web3.ppos.delegate.redeem_delegate()

    def get_delegate_info(self,
                          address=None,
                          node_id=None,
                          staking_block_identifier=None,
                          ):
        """ 获取地址对某个节点的某次质押的委托信息
        注意：因为节点可能进行过多次质押/撤销质押，会使得委托信息遗留，因此获取委托信息时必须指定节点质押区块
        """
        if self.aide.default_account:
            address = address or self.aide.default_account.address
        node_id = node_id or self.aide.node_id
        staking_block_identifier = staking_block_identifier or self.aide.staking.staking_info.StakingBlockNum

        delegate_info = self.aide.web3.ppos.delegate.get_delegate_info(address, node_id, staking_block_identifier)
        if delegate_info == 'Query delegate info failed:Delegate info is not found':
            return None
        else:
            return DelegateInfo(delegate_info)

    def get_delegate_lock_info(self,
                               address=None,
                               ):
        """ 获取地址处于锁定期的委托信息
        """
        address = address or self.aide.default_account.address

        delegate_lock_info = self.aide.web3.ppos.delegate.get_delegate_lock_info(address)
        # todo: 根据实际情况补全
        if delegate_lock_info == 'Query delegate info failed:Delegate info is not found':
            return None
        else:
            return delegate_lock_info

    def get_delegate_list(self, address=None):
        """ 获取地址的全部委托信息
        """
        if self.aide.default_account:
            address = address or self.aide.default_account.address
        delegate_list = self.aide.web3.ppos.delegate.get_delegate_list(address)
        if delegate_list == 'Retreiving delegation related mapping failed:RelatedList info is not found':
            return []
        else:
            return [DelegateInfo(delegate_info) for delegate_info in delegate_list]

    @contract_transaction(5000)
    def withdraw_delegate_reward(self,
                                 txn=None,
                                 private_key=None,
                                 ):
        """ 提取委托奖励，会提取委托了的所有节点的委托奖励
        """
        return self.aide.web3.ppos.delegate.withdraw_delegate_reward()

    def get_delegate_reward(self,
                            address=None,
                            node_ids=None
                            ):
        """ 获取委托奖励信息，可以根据节点id过滤
        """
        if self.aide.default_account:
            address = address or self.aide.default_account.address
        node_ids = node_ids or []
        return self.aide.web3.ppos.delegate.get_delegate_reward(address, node_ids)


class DelegateInfo(AttributeDict):
    """ 委托信息的属性字典类
    """
    Addr: str
    NodeId: str
    StakingBlockNum: int
    DelegateEpoch: int
    Released: int
    ReleasedHes: int
    RestrictingPlan: int
    RestrictingPlanHes: int
    CumulativeIncome: int
    LockReleasedHes: int
    LockRestrictingPlanHes: int
