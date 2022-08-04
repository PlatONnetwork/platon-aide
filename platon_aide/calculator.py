from decimal import Decimal
from typing import Literal

from platon import Web3
from platon_aide.economic import Economic, new_economic

from platon_aide.utils import ec_recover


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

    def get_blocks_from_miner(self, start=None, end=None, node_id=None):
        """ 获取节点出块数
        """
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

    # def __calc_staking_reward(self, node_id=None, epoch=None, verifier_count=None):
    #     """ 根据结算周期，计算节点在结算周期的质押奖励
    #     注意：因底层实现逻辑原因，本方法预期功能未能实现，请勿使用
    #     """
    #     if epoch and (not verifier_count):
    #         Warning('when passing in epoch, it is recommended to pass in the verifier count of the epoch.')
    #
    #     node_id = node_id or self._node_id
    #     if not epoch:
    #         epoch, _ = self.get_period_info(self.web3.platon.block_number, 'epoch')
    #
    #     epoch_staking_reward, epoch_block_reward = self.get_rewards_from_epoch(epoch)
    #
    #     if not verifier_count:
    #         verifier_count = self.get_verifier_count(epoch)
    #
    #     start_bn, end_bn = (epoch - 1) * self.epoch_blocks + 1, epoch * self.epoch_blocks
    #     block_count = self.get_blocks_from_miner(start_bn, end_bn, node_id=node_id)
    #
    #     return self.calc_staking_reward(epoch_staking_reward,
    #                                     epoch_block_reward,
    #                                     verifier_count,
    #                                     block_count,
    #                                     )

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
        slashing_ratio = self.economic.slashing.slashFractionDuplicateSign
        slashing_amount = Decimal(staking_amount) * (Decimal(slashing_ratio) / 10000)

        reward_ratio = self.economic.slashing.duplicateSignReportReward
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
            'round': self.economic.round_blocks,
            'consensus': self.economic.consensus_blocks,
            'epoch': self.economic.epoch_blocks,
            'increasing': self.economic.round_blocks,
        }
        period_blocks = blocks[period_type]

        if not block_number:
            block_number = self.web3.platon.block_number

        period = (block_number // period_blocks) + 1
        end_block = period * period_blocks

        return period, end_block
