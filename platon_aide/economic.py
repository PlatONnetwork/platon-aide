import json
from typing import Union
from dataclasses import dataclass

from dacite import from_dict


@dataclass
class CommonData:
    maxEpochMinutes: int
    nodeBlockTimeWindow: int
    perRoundBlocks: int
    maxConsensusVals: int
    additionalCycleTime: int


@dataclass
class StakingData:
    stakeThreshold: int
    operatingThreshold: int
    maxValidators: int
    unStakeFreezeDuration: int
    rewardPerMaxChangeRange: int
    rewardPerChangeInterval: int


@dataclass
class SlashingData:
    slashFractionDuplicateSign: int
    duplicateSignReportReward: int
    maxEvidenceAge: int
    slashBlocksReward: int
    zeroProduceCumulativeTime: int
    zeroProduceNumberThreshold: int
    zeroProduceFreezeDuration: int


@dataclass
class GovernData:
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


@dataclass
class RewardData:
    newBlockRate: int
    platonFoundationYear: int
    increaseIssuanceRatio: int
    TheNumberOfDelegationsReward: int


@dataclass
class RestrictingData:
    minimumRelease: int


@dataclass
class Economic:
    common: CommonData

    # restricting: RestrictingData
    # staking: StakingData
    # gov: GovernData
    # reward: RewardData
    # slashing: SlashingData

    # 区块
    @property
    def block_time(self):
        """ 区块时长/s
        """
        # todo: 获取区块平均时间
        return int(self.common.nodeBlockTimeWindow // self.common.perRoundBlocks)

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
        return self.common.perRoundBlocks

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
        return (self.common.maxEpochMinutes * 60) // self.consensus_time

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
        # todo: 修改为实时计算
        return (self.common.additionalCycleTime * 60) // self.epoch_time

    @property
    def validator_count(self):
        """ 共识验证人数量
        """
        return self.common.maxConsensusVals

    @property
    def staking_limit(self):
        """ 质押最小金额限制
        """
        return self.staking.stakeThreshold

    @property
    def add_staking_limit(self):
        """ 增持质押最小金额限制
        """
        return self.staking.operatingThreshold

    @property
    def delegate_limit(self):
        """ 委托最小金额限制
        """
        return self.staking.operatingThreshold

    @property
    def unstaking_freeze_epochs(self):
        """ 解质押后，质押金额冻结的结算周期数
        """
        return self.staking.unStakeFreezeDuration

    @property
    def not_block_slash_rate(self):
        """ 节点零出块处罚时，罚金对应的区块奖励倍数
        """
        return self.slashing.slashBlocksReward

    @property
    def param_proposal_epochs(self):
        """ 参数提案投票期的结算周期数
        """
        return self.govern.paramProposalVoteDurationSeconds // self.epoch_time

    @property
    def text_proposal_epochs(self):
        """ 文本提案投票期的结算周期数
        """
        return self.govern.textProposalVoteDurationSeconds // self.epoch_time


def new_economic(data: Union[dict, str]):
    """ 将data转换为economic对象
    """
    if type(data) is str:
        data = json.loads(data)

    return from_dict(Economic, data)
