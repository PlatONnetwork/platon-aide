from decimal import Decimal

from tests.conftest import *


def test_block_time():
    block_time = aide._economic.block_time
    assert block_time == 1


def test_round_time():
    round_time = aide._economic.round_time
    assert round_time == 10


def test_round_blocks():
    round_blocks = aide._economic.round_blocks
    assert round_blocks == 10


def test_consensus_time():
    consensus_time = aide._economic.consensus_time
    assert consensus_time == 40


def test_consensus_blocks():
    consensus_blocks = aide._economic.consensus_blocks
    assert consensus_blocks == 40


def test_consensus_rounds():
    consensus_rounds = aide._economic.consensus_rounds
    assert consensus_rounds == 4


def test_epoch_time():
    epoch_time = aide._economic.epoch_time
    assert epoch_time == 160


def test_epoch_blocks():
    epoch_blocks = aide._economic.epoch_blocks
    assert epoch_blocks == 160


def test_epoch_rounds():
    epoch_rounds = aide._economic.epoch_rounds
    assert epoch_rounds == 16


def test_epoch_consensus():
    epoch_consensus = aide._economic.epoch_consensus
    assert epoch_consensus == 4


def test_increasing_time():
    increasing_time = aide._economic.increasing_time
    assert increasing_time == 1600


def test_increasing_blocks():
    increasing_blocks = aide._economic.increasing_blocks
    assert increasing_blocks == 1600


def test_increasing_rounds():
    increasing_rounds = aide._economic.increasing_rounds
    assert increasing_rounds == 160


def test_increasing_consensus():
    increasing_consensus = aide._economic.increasing_consensus
    assert increasing_consensus == 40


def test_increasing_epoch():
    increasing_epoch = aide._economic.increasing_epoch
    assert increasing_epoch == 1600


def test_validator_count():
    validator_count = aide._economic.validator_count
    assert validator_count == 4


def test_staking_limit():
    staking_limit = aide._economic.staking_limit
    assert staking_limit == 100000000000000000000000


def test_add_staking_limit():
    add_staking_limit = aide._economic.add_staking_limit
    assert add_staking_limit == 10000000000000000000


def test_delegate_limit():
    delegate_limit = aide._economic.delegate_limit
    assert delegate_limit == 10000000000000000000


def test_unstaking_freeze_epochs():
    unstaking_freeze_epochs = aide._economic.unstaking_freeze_epochs
    assert unstaking_freeze_epochs == 2


def test_not_block_slash_rate():
    not_block_slash_rate = aide._economic.not_block_slash_rate
    assert not_block_slash_rate == 5


def test_param_proposal_epochs():
    param_proposal_epochs = aide._economic.param_proposal_epochs()
    assert param_proposal_epochs == 1


def test_text_proposal_epochs():
    text_proposal_epochs = aide._economic.text_proposal_epochs()
    assert text_proposal_epochs == 1


def test_get_verifier_count():
    verifier_count = aide._economic.get_verifier_count()
    assert isinstance(verifier_count, int)


def test_get_blocks_from_miner():
    node_id = '3ea97e7d098d4b2c2cc7fb2ef9e2c1b802d27f01a4a0d1f7ca5ab5ce2133d560c6f703f957162a580d04da59f45707dae40107c99762509278adf1501692e0a6'
    blocks_from_miner = aide._economic.get_block_count(node_id=node_id)
    assert isinstance(blocks_from_miner, int)


def test_get_rewards_from_epoch():
    staking_reward, block_reward = aide._economic.get_rewards_from_epoch()
    assert isinstance(staking_reward, int) and isinstance(block_reward, int)


def test_calc_staking_reward():
    epoch_staking_reward, epoch_block_reward = aide._economic.get_rewards_from_epoch()
    verifier_count = aide._economic.get_verifier_count()
    # block_count = aide._economic.get_blocks_from_miner()
    block_count = 1
    staking_reward, block_reward = aide._economic.calc_staking_reward(
                            total_staking_reward=epoch_staking_reward,
                            per_block_reward=epoch_block_reward,
                            verifier_count=verifier_count,
                            block_count=block_count,)
    assert staking_reward == int(Decimal(epoch_staking_reward) / Decimal(verifier_count))
    assert block_reward == block_reward * block_count



def test_calc_delegate_reward():
    _, total_node_reward = aide._economic.get_rewards_from_epoch()
    delegate_reward_ratio = 0.5
    delegate_total_amount = aide.delegate._economic.delegate_limit
    delegate_amount = aide.delegate._economic.delegate_limit
    calc_delegate_reward = aide._economic._calc_delegate_reward(
                            total_node_reward=total_node_reward,
                            delegate_reward_ratio=delegate_reward_ratio,
                            delegate_total_amount=delegate_total_amount,
                            delegate_amount=delegate_amount,
                            )
    assert calc_delegate_reward * 2 == total_node_reward


def test_calc_report_multi_sign_reward():
    staking_amount = aide.staking._economic.staking_limit * 2
    report_reward, to_incentive_pool_amount = aide._economic.calc_report_multi_sign_reward(staking_amount=staking_amount)
    assert report_reward == to_incentive_pool_amount == aide.staking._economic.staking_limit * (aide._economic.genesis.slashing.slashFractionDuplicateSign / 10000)


def test_get_period_info():
    period, end_block = aide._economic.get_period_info()
    assert end_block == period * 160

    period, end_block = aide._economic.get_period_info(
                        block_number=None,
                        period_type='round')
    assert end_block == period * 10

    period, end_block = aide._economic.get_period_info(
                        block_number=None,
                        period_type='consensus')
    assert end_block == period * 40

    period, end_block = aide._economic.get_period_info(
                        block_number=None,
                        period_type='increasing')
    assert end_block == period * 10

    block_number = 1
    period, end_block = aide._economic.get_period_info(
                        block_number=block_number)
    assert end_block == period * 160

