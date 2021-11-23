import json

from tests.conftest import *


def test_report_duplicate_sign():
    report_type = 1
    txn = {'gas': 2100000, 'gasPrice': 3000000000000000}
    data = json.dumps(
    {"prepareA":{"epoch":0,"viewNumber":0,"blockHash":"0xfa91e5dfe667d15d0122663f4ddc6f150575183374dc842f7445700cbaf1b077","blockNumber":287081,"blockIndex":0,"blockData":"0x32df83e9e9d0c6039d86d5a0dc1ab4f9ada9d2daa066a114a740f537e6761fee","validateNode":{"index":0,"nodeId":"e9ee916797e66c3e10eb272956525f62ac8f9b9b74af05a5b021c7b23d7b740359c62912fe5e7fef66f2a3f5358bc7d8c1af7d862269ed5db27b5cbcf9820ec8","blsPubKey":"5d5f3a56bf0217f7c8facbe7d2c8a28898a051b14f6f6209f484620df28979e1c963f63fd1f02359e03970b407c9a605434329cc1742bb5c9f975a5270c9f613f9de243e2a5074b0b7e8e79c6e0ce45b8ef93f6841c09af92ad82f25680a7b15"},"signature":"0xc5d2ab109123e1c3877b305c9c89222db472848c0867f3d437b28e7a7a188b395cc7292722191c579268ef09b316378200000000000000000000000000000000"},"prepareB":{"epoch":0,"viewNumber":0,"blockHash":"0x15c0d9c083947e457f1fa5be00cde62df832c4fd040e357c03a258fc65b39cc0","blockNumber":287081,"blockIndex":0,"blockData":"0x4bb1e21e99a0956331cc5998443f41ed5c517471a6d0653556aaa611f7078678","validateNode":{"index":0,"nodeId":"e9ee916797e66c3e10eb272956525f62ac8f9b9b74af05a5b021c7b23d7b740359c62912fe5e7fef66f2a3f5358bc7d8c1af7d862269ed5db27b5cbcf9820ec8","blsPubKey":"5d5f3a56bf0217f7c8facbe7d2c8a28898a051b14f6f6209f484620df28979e1c963f63fd1f02359e03970b407c9a605434329cc1742bb5c9f975a5270c9f613f9de243e2a5074b0b7e8e79c6e0ce45b8ef93f6841c09af92ad82f25680a7b15"},"signature":"0x0ffdaeaa1cff7ef01676ca18bf1eae0505037a1bbb54fd033b7124802f1c3693890c29ac1014bba3f1c744ae8b4ddc0f00000000000000000000000000000000"}})
    result = aide.slashing.report_duplicate_sign(
                            report_type=report_type,
                            data=data,
                            txn=txn,
                            # private_key=None,
                            )
    assert result['status'] == 1


def test_check_duplicate_sign():
    report_type = 1
    node_id = 'e9ee916797e66c3e10eb272956525f62ac8f9b9b74af05a5b021c7b23d7b740359c62912fe5e7fef66f2a3f5358bc7d8c1af7d862269ed5db27b5cbcf9820ec8'
    block_identifier = 2561
    txn = {'gas': 2100000, 'gasPrice': 3000000000000000}
    result = aide.slashing.check_duplicate_sign(
                            report_type=report_type,
                            block_identifier=block_identifier,
                            node_id=node_id,
                            txn=txn,
                            private_key=None,
                            )
    assert result[:2] == '0x'
