from decimal import Decimal
from typing import Literal

from platon import Web3

from platon_aide.base import Module
from platon_aide.utils import ec_recover
from platon_aide.economic import Economic, new_economic
from platon_aide.staking import Staking


class Calculator:

    def __init__(self, web3: Web3, economic: Economic = None):
        self.web3 = web3
        self.economic = new_economic(web3.debug.economic_config()) if not economic and hasattr(web3, 'debug') else economic

    def get_verifier_count(self, epoch=None):
        """ 获取结算周期的验证人数
        """
        # todo: 无法获取历史增发周期的验证节点信息，需要底层改进实现逻辑自洽
        # if not epoch:
        #     epoch, _ = self.get_period_info(self.web3.platon.block_number, period_type='epoch')

        verifier_list = self.web3.ppos.staking.get_verifier_list()
        return len(verifier_list)

    def get_blocks_from_miner(self, node_id, start=None, end=None):
        """ 获取节点出块数
        """
        block_count = 0

        if not start:
            start = 0
        if not end:
            end = self.web3.platon.block_number

        for bn in range(start, end):
            block = self.web3.platon.get_block(bn)
            public_key = ec_recover(block)
            if node_id in public_key:
                block_count = block_count + 1

            if bn % 100 == 0:
                logger.info(f'analyzed to {bn}th block, count: {block_count}, waiting...')

        return block_count

    def get_period_info(self,
                        block_number=None,
                        period_type: Literal['round', 'consensus', 'epoch', 'increasing'] = 'epoch'
                        ):
        """ 通过区块高度和周期类型，获取区块所在的周期数和周期结束块高
        """
        if period_type not in ['round', 'consensus', 'epoch', 'increasing']:
            raise ValueError('unrecognized period type.')

        blocks = {
            'round': self._economic.round_blocks,
            'consensus': self._economic.consensus_blocks,
            'epoch': self._economic.epoch_blocks,
            'increasing': self._economic.round_blocks,
        }
        period_blocks = blocks[period_type]

        if not block_number:
            block_number = self.web3.platon.block_number

        period = math.ceil(block_number // period_blocks)
        start_bn, end_bn = self.get_period_ends(period)

        return period, start_bn, end_bn

    def get_period_ends(self,
                        period,
                        period_type: Literal['round', 'consensus', 'epoch', 'increasing'] = 'epoch'
                        ):
        """ 通过周期数和周期类型，获取周期的起始结束块高
        """
        if period_type not in ['round', 'consensus', 'epoch', 'increasing']:
            raise ValueError('unrecognized period type.')

        blocks = {
            'round': self._economic.round_blocks,
            'consensus': self._economic.consensus_blocks,
            'epoch': self._economic.epoch_blocks,
            'increasing': self._economic.round_blocks,
        }
        period_blocks = blocks[period_type]
        start_bn, end_bn = (period - 1) * period_blocks + 1, period * period_blocks

        return start_bn, end_bn

    def get_reward_info(self):
        """ 获取当前结算周期的奖励信息
        """
        total_staking_reward = self.web3.ppos.staking.get_staking_reward()
        per_block_reward = self.web3.ppos.staking.get_block_reward()
        return total_staking_reward, per_block_reward

    # def get_node_reward(self, node_id):
    #     """ 即时计算上一个结算周期，节点的总奖励
    #     """
    #     total_staking_reward = self.web3.ppos.staking.get_staking_reward()
    #     verifier_count = self.get_verifier_count()
    #     per_block_reward = self.web3.ppos.staking.get_block_reward()
    #     # 获取上一个结算周期内，节点的出块数
    #     epoch, _, _ = self.get_period_info(self.web3.platon.block_number, 'epoch')
    #     start_bn, end_bn = self.get_period_ends(epoch - 1)
    #     block_count = self.get_block_count(node_id, start_bn, end_bn)
    #     self.calc_node_reward(total_staking_reward,
    #                           verifier_count,
    #                           per_block_reward,
    #                           block_count
    #                           )

    @staticmethod
    def calc_node_reward(total_staking_reward,
                         verifier_count,
                         per_block_reward,
                         block_count,
                         ):
        """ 计算一个结算周期，节点的总奖励（交易gas奖励除外）

        Args:
            total_staking_reward: 结算周期的总质押奖励，可以通过self.get_reward_info获取
            verifier_count: 结算周期的验证人数，可以通过self.get_verifier_count获取
            per_block_reward: 结算周期的出块奖励，可以通过self.get_reward_info获取
            block_count: 节点在结算周期的出块数，可以通过self.get_block_count获取
        """
        staking_reward = int(Decimal(total_staking_reward) / Decimal(verifier_count))
        block_reward = int(Decimal(per_block_reward) * Decimal(block_count))
        node_reward = staking_reward + block_reward
        return node_reward

    # def get_staking_reward(self, node_id):
    #     """ 即时计算上一个结算周期，节点的质押奖励
    #     """
    #     total_staking_reward = self.web3.ppos.staking.get_staking_reward()
    #     verifier_count = self.get_verifier_count()
    #     per_block_reward = self.web3.ppos.staking.get_block_reward()
    #     # 获取上一个结算周期内，节点的出块数
    #     epoch, _, _ = self.get_period_info(self.web3.platon.block_number, 'epoch')
    #     start_bn, end_bn = self.get_period_ends(epoch - 1)
    #     block_count = self.get_block_count(node_id, start_bn, end_bn)
    #
    #     node_reward_ratio = self._staking.get_candidate_info(node_id).RewardPer
    #
    #     return self.calc_staking_reward(total_staking_reward,
    #                                     verifier_count,
    #                                     per_block_reward,
    #                                     block_count,
    #                                     node_reward_ratio,
    #                                     )

    @staticmethod
    def calc_staking_reward(epoch_staking_reward,
                            epoch_block_reward,
                            verifier_count,
                            per_block_reward,
                            block_count,
                            node_reward_ratio,
                            ):
        """
        计算一个结算周期，节点的质押奖励

        Args:
            epoch_staking_reward: 结算周期的质押奖励，可以通过self.get_rewards_from_epoch获取
            epoch_block_reward: 结算周期的出块奖励，可以通过self.get_rewards_from_epoch获取
            verifier_count: 结算周期的验证人数
            block_count: 节点在结算周期的出块数，可以通过self.get_blocks_from_miner获取
        """
        staking_reward = Decimal(epoch_staking_reward) / Decimal(verifier_count)
        block_reward = Decimal(epoch_block_reward) * Decimal(block_count)
        return int(staking_reward), int(block_reward)

    # def get_delegate_reward(self,
    #                         node_id,
    #                         delegate_amount,
    #                         delegate_total_amount,
    #                         ):
    #     """
    #     即时计算上一个结算周期，账户在节点的委托奖励
    #
    #     Args:
    #         node_id: 委托节点ID
    #         delegate_amount: 结算周期内，账户在节点的锁定期委托总额
    #         delegate_total_amount: 节点在该结算周期的锁定期委托总额
    #     """
    #     total_staking_reward = self.web3.ppos.staking.get_staking_reward()
    #     verifier_count = self.get_verifier_count()
    #     per_block_reward = self.web3.ppos.staking.get_block_reward()
    #     # 获取上一个结算周期内，委托节点的出块数
    #     epoch, _, _ = self.get_period_info(self.web3.platon.block_number, 'epoch')
    #     start_bn, end_bn = self.get_period_ends(epoch - 1)
    #     block_count = self.get_block_count(node_id, start_bn, end_bn)
    #
    #     node_reward_ratio = self._staking.get_candidate_info(node_id).RewardPer
    #
    #     return self.calc_delegate_reward(total_staking_reward,
    #                                      verifier_count,
    #                                      per_block_reward,
    #                                      block_count,
    #                                      node_reward_ratio,
    #                                      delegate_total_amount,
    #                                      delegate_amount,
    #                                      )

    @staticmethod
    def calc_delegate_reward(total_node_reward,
                             delegate_reward_ratio,
                             delegate_total_amount,
                             delegate_amount,
                             ):
        """
        计算一个结算周期内，账户在节点的委托奖励

        Args:
            total_staking_reward: 结算周期的总质押奖励，可以通过self.get_reward_info获取
            verifier_count: 结算周期的验证人数，可以通过self.get_verifier_count获取
            per_block_reward: 结算周期的出块奖励，可以通过self.get_reward_info获取
            block_count: 节点在结算周期的出块数，可以通过self.get_block_count获取
            node_reward_ratio: 节点在结算周期的委托分红比例
            delegate_total_amount: 节点在结算周期的锁定期委托总额
            delegate_amount: 结算周期内，账户对节点的锁定期委托总额
        """
        total_delegate_reward = Decimal(total_node_reward) * (Decimal(delegate_reward_ratio) / Decimal(10000))
        per_delegate_reward = Decimal(total_delegate_reward) / Decimal(delegate_total_amount)
        return int(per_delegate_reward * delegate_amount)

    def calc_report_multi_sign_reward(self, staking_amount):
        """ 计算举报双签的奖励
        """
        slashing_ratio = self.economic.slashing.slashFractionDuplicateSign
        slashing_amount = Decimal(staking_amount) * (Decimal(slashing_ratio) / 10000)

        reward_ratio = self.economic.slashing.duplicateSignReportReward
        report_reward = slashing_amount * (Decimal(reward_ratio) / 100)

        to_incentive_pool_amount = slashing_amount - report_reward
        return int(report_reward), int(to_incentive_pool_amount)
