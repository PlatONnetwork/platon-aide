import json
from decimal import Decimal
from typing import Literal
from platon import Web3
from platon.datastructures import AttributeDict

from module import Module
from utils import ec_recover


class _ChainData(AttributeDict):
    maxEpochMinutes: int
    nodeBlockTimeWindow: int
    perRoundBlocks: int
    maxConsensusVals: int
    additionalCycleTime: int


class _StakingData(AttributeDict):
    stakeThreshold: int
    operatingThreshold: int
    maxValidators: int
    unStakeFreezeDuration: int
    rewardPerMaxChangeRange: int
    rewardPerChangeInterval: int


class _SlashingData(AttributeDict):
    slashFractionDuplicateSign: int
    duplicateSignReportReward: int
    maxEvidenceAge: int
    slashBlocksReward: int
    zeroProduceCumulativeTime: int
    zeroProduceNumberThreshold: int
    zeroProduceFreezeDuration: int


class _GovernData(AttributeDict):
    versionProposalVoteDurationSeconds: int
    versionProposalSupportRate: int
    textProposalVoteDurationSeconds: int
    textProposalVoteRate: int
    textProposalSupportRate: int
    cancelProposalVoteRate: int
    cancelProposalSupportRate: int
    paramProposalVoteDurationSeconds: int
    paramProposalVoteRate: int
    paramProposalSupportRate: int


class _RewardData(AttributeDict):
    newBlockRate: int
    platonFoundationYear: int
    increaseIssuanceRatio: int
    TheNumberOfDelegationsReward: int


class _RestrictingData(AttributeDict):
    minimumRelease: int


class _GasData:
    transferGas: int = 21000
    restrictingGas: int = 100000
    governGasPrice: int = 2100000


class GenesisData:
    """ PlatON创世数据
    """

    def __init__(self, web3: Web3):
        economic_config = json.loads(web3.debug.economic_config())
        self.chain = _ChainData(economic_config['common'])
        self.restricting = _RestrictingData(economic_config['restricting'])
        self.staking = _StakingData(economic_config['staking'])
        self.govern = _GovernData(economic_config['gov'])
        self.reward = _RewardData(economic_config['reward'])
        self.slashing = _SlashingData(economic_config['slashing'])
        self.gas = _GasData()


gas = _GasData()


class Economic(Module):

    def __init__(self, web3: Web3):
        super().__init__(web3)
        self.genesis = GenesisData(web3)
        self._get_node_info()

    # 区块
    @property
    def block_time(self):
        """ 区块时长/s
        """
        # todo: 获取区块平均时间  先放着看用例实际场景
        return int(self.genesis.chain.nodeBlockTimeWindow // self.genesis.chain.perRoundBlocks)

    # 窗口期
    @property
    def round_time(self):
        """ 窗口期时长/m
        """
        return self.round_blocks * self.block_time

    @property
    def round_blocks(self):
        """ 窗口期区块数量
        """
        return self.genesis.chain.perRoundBlocks

    # 共识轮
    @property
    def consensus_time(self):
        """ 共识轮时长/m
        """
        return self.consensus_rounds * self.round_time

    @property
    def consensus_blocks(self):
        """ 共识轮区块数量
        """
        return self.consensus_rounds * self.round_blocks

    @property
    def consensus_rounds(self):
        """ 共识轮窗口期数量
        """
        return self.validator_count

    # 结算周期
    @property
    def epoch_time(self):
        """ 结算周期时长/m
        """
        return self.epoch_consensus * self.consensus_time

    @property
    def epoch_blocks(self):
        """ 结算周期区块数量
        """
        return self.epoch_consensus * self.consensus_blocks

    @property
    def epoch_rounds(self):
        """ 结算周期窗口期数量
        """
        return self.epoch_consensus * self.consensus_rounds

    @property
    def epoch_consensus(self):
        """ 结算周期共识轮数量
        """
        return (self.genesis.chain.maxEpochMinutes * 60) // self.consensus_time

    @property
    def increasing_time(self):
        """ 增发周期时长/m
        """
        return self.increasing_epoch * self.epoch_time

    @property
    def increasing_blocks(self):
        """ 增发周期区块数
        """
        return self.increasing_rounds * self.round_blocks

    @property
    def increasing_rounds(self):
        """ 增发周期窗口期数
        """
        return self.increasing_consensus * self.consensus_rounds

    @property
    def increasing_consensus(self):
        """ 增发周期共识轮数
        """
        return self.increasing_epoch * self.epoch_consensus

    @property
    def increasing_epoch(self):
        """ 增发周期结算周期数
        """
        # todo: 修改为实时计算 先放着看用例实际场景
        return (self.genesis.chain.additionalCycleTime * 60) // self.epoch_time

    @property
    def validator_count(self):
        """ 共识验证人数量
        """
        return self.genesis.chain.maxConsensusVals

    @property
    def staking_limit(self):
        """ 质押最小金额限制
        """
        return self.genesis.staking.stakeThreshold

    @property
    def add_staking_limit(self):
        """ 增持质押最小金额限制
        """
        return self.genesis.staking.operatingThreshold

    @property
    def delegate_limit(self):
        """ 委托最小金额限制
        """
        return self.genesis.staking.operatingThreshold

    @property
    def unstaking_freeze_epochs(self):
        """ 解质押后，质押金额冻结的结算周期数
        """
        return self.genesis.staking.unStakeFreezeDuration

    @property
    def not_block_slash_rate(self):
        """ 节点零出块处罚时，罚金对应的区块奖励倍数
        """
        return self.genesis.slashing.slashBlocksReward

    def param_proposal_epochs(self):
        """ 参数提案投票期的结算周期数
        """
        return self.genesis.govern.paramProposalVoteDurationSeconds // self.epoch_time

    def text_proposal_epochs(self):
        """ 文本提案投票期的结算周期数
        """
        return self.genesis.govern.textProposalVoteDurationSeconds // self.epoch_time

    def get_verifier_count(self, epoch=None):
        """ 获取结算周期的验证人数
        注意：目前只能获取当前结算周期的验证人数，无法获取历史增发周期的验证人数
        # todo: 推动底层改进，以实现逻辑自洽
        """
        # if not epoch:
        #     epoch, _ = self.get_period_info(self.web3.platon.block_number, period_type='epoch')

        verifier_list = self.web3.ppos.staking.get_verifier_list()
        return len(verifier_list)

    def get_blocks_from_miner(self, start=None, end=None, node_id=None):
        """ 获取节点出块数
        """
        start = start or 1
        end = end or self.web3.platon.block_number
        node_id = node_id or self.node_id
        block_count = 0
        for bn in range(start, end):
            block = self.web3.platon.get_block(bn)
            public_key = ec_recover(block)
            if node_id in public_key:
                block_count = block_count + 1
        return block_count

    def get_rewards_from_epoch(self, epoch=None):
        """ 根据增发周期，获取增发周期的奖励信息
        注意：目前只能获取当前增发周期的奖励信息，无法获取历史增发周期的奖励信息
        # todo: 推动底层改进，以实现逻辑自洽
        """
        staking_reward = self.web3.ppos.staking.get_staking_reward()
        block_reward = self.web3.ppos.staking.get_block_reward()
        return staking_reward, block_reward

    @staticmethod
    def calc_staking_reward(epoch_staking_reward,
                            epoch_block_reward,
                            verifier_count,
                            block_count,
                            ):
        """
        计算一个结算周期内，节点的质押奖励

        Args:
            epoch_staking_reward: 结算周期的质押奖励，可以通过self.get_rewards_from_epoch获取
            epoch_block_reward: 结算周期的出块奖励，可以通过self.get_rewards_from_epoch获取
            verifier_count: 结算周期的验证人数
            block_count: 节点在结算周期的出块数，可以通过self.get_blocks_from_miner获取
        """
        staking_reward = Decimal(epoch_staking_reward) / Decimal(verifier_count)
        block_reward = Decimal(epoch_block_reward) * Decimal(block_count)
        return int(staking_reward), int(block_reward)

    def __calc_staking_reward(self, node_id=None, epoch=None, verifier_count=None):
        """ 根据结算周期，计算节点在结算周期的质押奖励
        注意：目前只能获取历史增发周期的奖励信息，无法获取当前增发周期的奖励信息
        """
        if epoch and (not verifier_count):
            Warning('when passing in epoch, it is recommended to pass in the verifier count of the epoch.')

        node_id = node_id or self.node_id
        if not epoch:
            epoch, _ = self.get_period_info(self.web3.platon.block_number, 'epoch')

        epoch_staking_reward, epoch_block_reward = self.get_rewards_from_epoch(epoch)

        if not verifier_count:
            verifier_count = self.get_verifier_count(epoch)

        start_bn, end_bn = (epoch - 1) * self.epoch_blocks + 1, epoch * self.epoch_blocks
        block_count = self.get_blocks_from_miner(start_bn, end_bn, node_id=node_id)

        return self.calc_staking_reward(epoch_staking_reward,
                                        epoch_block_reward,
                                        verifier_count,
                                        block_count,
                                        )

    @staticmethod
    def calc_delegate_reward(total_node_reward,
                             delegate_reward_ratio,
                             delegate_total_amount,
                             delegate_amount,
                             ):
        """
        计算一个结算周期内，账户在某个节点的委托奖励

        Args:
            total_node_reward: 节点在该结算周期的总质押奖励
            delegate_reward_ratio: 节点在该结算周期的委托分红比例
            delegate_total_amount: 节点在该结算周期的锁定期委托总额
            delegate_amount: 结算周期内，账户在该节点的锁定期委托总额
        """
        total_delegate_reward = Decimal(total_node_reward) * (Decimal(delegate_reward_ratio) / Decimal(10000))
        per_delegate_reward = Decimal(total_delegate_reward) / Decimal(delegate_total_amount)
        return int(per_delegate_reward * delegate_amount)

    def calc_report_multi_sign_reward(self, staking_amount):
        """ 计算举报双签的奖励
        """
        slashing_ratio = self.genesis.slashing.slashFractionDuplicateSign
        slashing_amount = Decimal(staking_amount) * (Decimal(slashing_ratio) / 10000)

        reward_ratio = self.genesis.slashing.duplicateSignReportReward
        report_reward = slashing_amount * (Decimal(reward_ratio) / 100)

        to_incentive_pool_amount = slashing_amount - report_reward
        return int(report_reward), int(to_incentive_pool_amount)

    def get_period_info(self,
                        block_number=None,
                        period_type: Literal['round', 'consensus', 'epoch', 'increasing'] = 'epoch'
                        ):
        """ 通过区块高度和周期类型，获取区块所在的周期数和周期结束块高
        """
        if period_type not in ['round', 'consensus', 'epoch', 'increasing']:
            raise ValueError('unrecognized period type.')

        blocks = {
            'round': self.round_blocks,
            'consensus': self.consensus_blocks,
            'epoch': self.epoch_blocks,
            'increasing': self.round_blocks,
        }
        period_blocks = blocks[period_type]

        if not block_number:
            block_number = self.web3.platon.block_number

        period = (block_number // period_blocks) + 1
        end_block = period * period_blocks

        return period, end_block
