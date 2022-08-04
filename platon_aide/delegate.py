from platon import Web3
from platon.datastructures import AttributeDict

from platon_aide.economic import Economic, new_economic
from platon_aide.base.module import Module
from platon_aide.staking import Staking
from platon_aide.utils import contract_transaction


class Delegate(Module):

    def __init__(self, web3: Web3, economic: Economic = None):
        super().__init__(web3)
        self._module_type = 'inner-contract'
        self._result_type = 'event'
        self._get_node_info()
        self._economic = new_economic(web3.debug.economic_config()) if not economic and hasattr(web3, 'debug') else economic

    @property
    def _staking_block_number(self):
        staking = Staking(self.web3)
        return staking.staking_info.StakingBlockNum

    @contract_transaction
    def delegate(self,
                 amount=None,
                 balance_type=0,
                 node_id=None,
                 txn=None,
                 private_key=None,
                 ):
        """ 委托节点，以获取节点的奖励分红
        """
        amount = amount or self._economic.add_staking_limit
        node_id = node_id or self._node_id
        return self.web3.ppos.delegate.delegate(node_id, balance_type, amount)

    @contract_transaction
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
        node_id = node_id or self._node_id
        amount = amount or self._economic.add_staking_limit
        staking_block_identifier = staking_block_identifier or self._staking_block_number

        return self.web3.ppos.delegate.withdrew_delegate(node_id,
                                                         staking_block_identifier,
                                                         amount,
                                                         )

    def get_delegate_info(self,
                          address=None,
                          node_id=None,
                          staking_block_identifier=None,
                          ):
        """ 获取地址对某个节点的某次质押的委托信息
        注意：因为节点可能进行过多次质押/撤销质押，会使得委托信息遗留，因此获取委托信息时必须指定节点质押区块
        """
        if self.default_account:
            address = address or self.default_account.address
        node_id = node_id or self._node_id
        staking_block_identifier = staking_block_identifier or self._staking_block_number

        delegate_info = self.web3.ppos.delegate.get_delegate_info(address, node_id, staking_block_identifier)
        if delegate_info == 'Query delegate info failed:Delegate info is not found':
            return None
        else:
            return DelegateInfo(delegate_info)

    def get_delegate_list(self, address=None):
        """ 获取地址的全部委托信息
        """
        if self.default_account:
            address = address or self.default_account.address
        # return self.web3.ppos.delegate.get_delegate_list(address)
        delegate_list = self.web3.ppos.delegate.get_delegate_list(address)
        if delegate_list == 'Retreiving delegation related mapping failed:RelatedList info is not found':
            return None
        else:
            return [DelegateInfo(delegate_info) for delegate_info in delegate_list]

    @contract_transaction
    def withdraw_delegate_reward(self,
                                 txn=None,
                                 private_key=None,
                                 ):
        """ 提取委托奖励，会提取委托了的所有节点的委托奖励
        """
        return self.web3.ppos.delegate.withdraw_delegate_reward()

    def get_delegate_reward(self,
                            address=None,
                            node_ids=None
                            ):
        """ 获取委托奖励信息，可以根据节点id过滤
        """
        if self.default_account:
            address = address or self.default_account.address
        node_ids = node_ids or []
        return self.web3.ppos.delegate.get_delegate_reward(address, node_ids)


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
