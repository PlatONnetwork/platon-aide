import math
import warnings

from decimal import Decimal
from typing import Literal
from loguru import logger

from platon_aide.base import Module


class Calculator(Module):

    def get_verifier_count(self):
        """ 获取结算周期的验证人数
        备注：目前链上只能获取当前结算周期的验证人数
        """
        verifier_list = self.aide.web3.ppos.staking.get_verifier_list()
        return len(verifier_list)

    def get_block_count(self, node_id, start_bn=None, end_bn=None):
        """ 获取节点出块数
        """
        start_bn = start_bn or 1
        end_bn = end_bn or self.aide.platon.block_number
        if end_bn - start_bn > 1000:
            warnings.warn('too many blocks to analyze, it will be a long wait')

        block_count = 0
        for bn in range(start_bn, end_bn):
            # block = self.aide.platon.get_block(bn)
            public_key = self.aide.ec_recover(bn)
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
            raise ValueError('unknown period type.')

        blocks = {
            'round': self.aide.economic.round_blocks,
            'consensus': self.aide.economic.consensus_blocks,
            'epoch': self.aide.economic.epoch_blocks,
            'increasing': self.aide.economic.increasing_blocks,
        }
        period_blocks = blocks[period_type]

        if not block_number:
            block_number = self.aide.platon.block_number

        period = math.ceil(block_number / period_blocks) or 1
        start_block, end_block = self.get_period_ends(period, period_type)

        return period, start_block, end_block

    def get_period_ends(self,
                        period,
                        period_type: Literal['round', 'consensus', 'epoch', 'increasing'] = 'epoch'
                        ):
        """ 通过周期数和周期类型，获取周期的起始结束块高
        """
        if period_type not in ['round', 'consensus', 'epoch', 'increasing']:
            raise ValueError('unknown period type.')

        blocks = {
            'round': self.aide.economic.round_blocks,
            'consensus': self.aide.economic.consensus_blocks,
            'epoch': self.aide.economic.epoch_blocks,
            'increasing': self.aide.economic.increasing_blocks,
        }
        period_blocks = blocks[period_type]
        start_block, end_block = (period - 1) * period_blocks + 1, period * period_blocks

        return start_block, end_block

    def get_reward_info(self):
        """ 获取当前结算周期的奖励信息
        """
        # todo: 删除该方法
        total_staking_reward = self.aide.web3.ppos.staking.get_staking_reward()
        per_block_reward = self.aide.web3.ppos.staking.get_block_reward()
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
    #     total_staking_reward = self.aide.web3.ppos.staking.get_staking_reward()
    #     verifier_count = self.get_verifier_count()
    #     per_block_reward = self.aide.web3.ppos.staking.get_block_reward()
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
    def calc_staking_reward(total_staking_reward,
                            verifier_count,
                            per_block_reward,
                            block_count,
                            node_reward_ratio,
                            ):
        """
        计算一个结算周期，节点的质押奖励

        Args:
            total_staking_reward: 结算周期的总质押奖励，可以通过self.get_reward_info获取
            verifier_count: 结算周期的验证人数，可以通过self.get_verifier_count获取
            per_block_reward: 结算周期的出块奖励，可以通过self.get_reward_info获取
            block_count: 节点在结算周期的出块数，可以通过self.get_block_count获取
            node_reward_ratio: 节点在结算周期的委托分红比例
        """
        node_reward = Calculator.calc_node_reward(total_staking_reward,
                                                  verifier_count,
                                                  per_block_reward,
                                                  block_count,
                                                  )

        delegate_reward = Calculator.calc_delegate_reward(total_staking_reward,
                                                          verifier_count,
                                                          per_block_reward,
                                                          block_count,
                                                          node_reward_ratio,
                                                          )

        staking_reward = node_reward - delegate_reward
        return staking_reward

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
    def calc_delegate_reward(total_staking_reward,
                             verifier_count,
                             per_block_reward,
                             block_count,
                             node_reward_ratio,
                             delegate_total_amount=None,
                             delegate_amount=None,
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
        dividend_ratio = Decimal(node_reward_ratio) / Decimal(10000)
        # 按照底层算法，计算质押奖励分红
        staking_reward = int(Decimal(total_staking_reward) / Decimal(verifier_count))
        staking_dividends = int(Decimal(staking_reward) * dividend_ratio)
        # 按照底层算法，计算出块奖励分红
        per_block_delegate_reward = Decimal(per_block_reward) * dividend_ratio
        block_dividends = per_block_delegate_reward * Decimal(block_count)
        # 计算节点所有委托分红
        all_delegate_reward = int(staking_dividends + block_dividends)
        if not delegate_total_amount and not delegate_amount:
            return all_delegate_reward
        # 计算账户的委托分红
        delegate_reward = math.floor(Decimal(all_delegate_reward) * Decimal(delegate_amount) / Decimal(delegate_total_amount))
        return delegate_reward

    def calc_report_multi_sign_reward(self, staking_amount):
        """ 计算举报双签的奖励
        """
        slashing_ratio = self.aide.economic.slashing.slashFractionDuplicateSign
        slashing_amount = Decimal(staking_amount) * (Decimal(slashing_ratio) / 10000)

        reward_ratio = self.aide.economic.slashing.duplicateSignReportReward
        report_reward = slashing_amount * (Decimal(reward_ratio) / 100)

        to_incentive_pool_amount = slashing_amount - report_reward
        return int(report_reward), int(to_incentive_pool_amount)
