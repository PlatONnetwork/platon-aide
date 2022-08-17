# platon-aide
它是一个小助手，能够帮助您快速访问PlatON区块链，并使用其基本功能 


# 安装方法
```shell
pip install platon_aide
```


# 使用方法
```python
from platon_account import Account

from platon_aide import Aide
from platon_aide.economic import new_economic

uri = 'http://192.168.120.121:6789'


"""
初始化部分
"""
# 实例化aide
aide = Aide(uri)

# 特殊情况实例化aide
# 这里因为节点关闭了admin、debug的api，aide将无法自动获取经济模型参数和节点信息
# 为了避免aide自动获取报错，需要自己生成经济模型对象，并指定关闭的接口
data = {"common":{"maxEpochMinutes":3,"nodeBlockTimeWindow":10,"perRoundBlocks":10,"maxConsensusVals":4,"additionalCycleTime":28},"staking":{"stakeThreshold":100000000000000000000000,"operatingThreshold":10000000000000000000,"maxValidators":5,"unStakeFreezeDuration":2,"rewardPerMaxChangeRange":500,"rewardPerChangeInterval":2},"slashing":{"slashFractionDuplicateSign":100,"duplicateSignReportReward":50,"maxEvidenceAge":1,"slashBlocksReward":5,"zeroProduceCumulativeTime":1,"zeroProduceNumberThreshold":1,"zeroProduceFreezeDuration":1},"gov":{"versionProposalVoteDurationSeconds":1600,"versionProposalSupportRate":6670,"textProposalVoteDurationSeconds":160,"textProposalVoteRate":5000,"textProposalSupportRate":6670,"cancelProposalVoteRate":5000,"cancelProposalSupportRate":6670,"paramProposalVoteDurationSeconds":160,"paramProposalVoteRate":5000,"paramProposalSupportRate":6670},"reward":{"newBlockRate":50,"platonFoundationYear":10,"increaseIssuanceRatio":250,"theNumberOfDelegationsReward":2},"restricting":{"minimumRelease":100000000000000000000},"innerAcc":{"platonFundAccount":"lat1drz94my95tskswnrcnkdvnwq43n8jt6dmzf8h8","platonFundBalance":0,"cdfAccount":"lat1kvurep20767ahvrkraglgd9t34w0w2g059pmlx","cdfBalance":421411981000000000000000000}}
economic = new_economic(data)
aide = Aide(uri, economic=economic, exclude_api=['admin', 'debug'])

# 设置默认账户，后续使用aide发交易，如果不指定私钥，则都会使用默认账户签名交易
account = Account.from_key('f51ca759562e1daf9e5302d121f933a8152915d34fcbc27e542baf256b5e4b74', aide.hrp)
aide.set_default_account(account)


"""
普通交易部分
"""
# 发送转账
to_account = Account.create(hrp='lat')
print(aide.transfer.transfer(to_account.address, 10 * 10 ** 18))

# 调用web3
print(aide.web3.clientVersion)

# 调用内置合约
print(aide.delegate.get_delegate_lock_info())


"""
调用合约部分
"""
false = False
ture = True
abi = [{"anonymous":false,"inputs":[{"indexed":false,"internalType":"uint256","name":"_chainId","type":"uint256"}],"name":"_putChainID","type":"event"},{"inputs":[],"name":"getChainID","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"putChainID","outputs":[],"stateMutability":"nonpayable","type":"function"}]
bytecode = '608060405234801561001057600080fd5b50610107806100206000396000f3fe6080604052348015600f57600080fd5b506004361060325760003560e01c806336319ab0146037578063564b81ef14603f575b600080fd5b603d6059565b005b60456099565b6040516050919060ae565b60405180910390f35b466000819055507f68e891aec7f9596d6e192c48cb82364ec392d423bce80abd6e1ee5ad05860256600054604051608f919060ae565b60405180910390a1565b600046905090565b60a88160c7565b82525050565b600060208201905060c1600083018460a1565b92915050565b600081905091905056fea264697066735822122037a1668252253271128182c71109922cb1e300fb08a7080a0587f360df4071ba64736f6c63430008060033'

# 部署新的合约
contract = aide.contract.deploy(abi=abi, bytecode=bytecode)
print(contract.address)

# 已有合约，直接初始化
contract_address = '0x00'
contract = aide.contract.init(abi=abi, address=contract_address)
print(contract.address)

# call调用
print(aide.contract.getChainID())

# 发送交易，和call一样
res = aide.contract.putChainID()

# 解析event
print(aide.contract.PutChainID(res))
```

