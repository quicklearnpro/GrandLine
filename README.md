<div align="center">

# GrandLine

![data](https://socialify.git.ci/B1ue1nWh1te/GrandLine/image?description=1&font=Rokkitt&forks=1&issues=1&language=1&owner=1&pattern=Circuit%20Board&stargazers=1&theme=Dark)

GrandLine 是一个用于与 BSC 链上的 PancakeSwap Dapp 进行简单交互的工具。

[![Lisence](https://img.shields.io/github/license/B1ue1nWh1te/GrandLine)](https://github.com/B1ue1nWh1te/GrandLine/blob/main/LICENSE)
[![Release](https://img.shields.io/github/v/release/B1ue1nWh1te/GrandLine)](https://github.com/B1ue1nWh1te/GrandLine/releases/)
[![Python Version](https://img.shields.io/badge/python-3.7+-blue)](https://www.python.org/)
[![Poseidon](https://img.shields.io/badge/Poseidon-purple)](https://github.com/B1ue1nWh1te/Poseidon)

</div>

# 实际背景

众所周知，交易对于时效性的要求很高，机会转瞬即逝，在区块链金融市场更是如此，有时仅仅比其他人慢了几秒也会造成很大的损失，而通过浏览器访问[PancakeSwap UI](https://pancakeswap.finance/)进行交易的这一系列过程中存在较多繁琐且耗时的操作，难免会影响交易效率，导致错失最佳时机。出于简化交易流程、尽可能争取先机的目的，这一工具通过调用接口函数，直接在合约层面进行交互，实现了链上交易流程的最简化。

# 功能介绍

目前开源的这个版本只支持`BSC`链上的`PancakeSwap`的**买入和卖出**操作（**且后续不会更新其他功能**），但由于`EVM`链的共性，理论上你可以通过修改`RPC`以及`RouterAddress`，使得这一工具在任意`EVM`链上的任意`DEX`都能发挥作用，同时由于我为代码留下了足够的二次开发空间，理论上你可以通过二次开发来实现更多自己需要的功能，这正好也符合了我开源这一工具的最初想法：**技术交流分享**。

具体效果可参看[使用示例](#使用示例)。

# 使用方法

1. 打开命令行，切换到当前目录，执行`pip install -r requirements.txt`安装依赖库。
2. 修改`config.json`中的各项配置以符合自己的需求，通常情况下，只需将`private_key_base64`参数修改为你钱包私钥的`base64`形式即可（这么做也仅是为私钥提供了一层微不足道的保护）。这里提供了一种生成方法：在当前目录下执行`python encrypt.py`，之后输入私钥即可。
3. 在当前目录下执行`python swap.py`，之后根据引导进行相应的操作即可。

## 配置参数说明

`bsc_mainnet_rpc`: BSC 链主网的 RPC 地址。修改建议：自行选择合适的 RPC。

`bsc_testnet_rpc`: BSC 链测试网的 RPC 地址。修改建议：维持现状。

`bscscan_api_key`: BscScan 的 API KEY。修改建议：更换为自己的 API KEY。

`network_environment`: 程序工作的网络环境。修改建议：主网-"mainnet"/测试网-"testnet"。

`private_key_base64`: 钱包私钥的 Base64 形式。修改建议：更换为自己钱包的私钥的 Base64 形式。

`buy_slippage_tolerance`: 买入时的滑点容差，单位为%。修改建议：自行选择合适的值。

`sell_slippage_tolerance`: 卖出时的滑点容差，单位为%。修改建议：自行选择合适的值。

`fund_token_use`: 使用的资金币种在`fund_token_list`中的下标，用于指定使用的资金币种。修改建议：自行选择合适的值。

`pancakeswap_router_address`: PancakeswapRouter 的合约地址。修改建议：维持现状。

`fund_token_list`: 资金币种列表。资金币种是指买入时消耗，卖出时得到的币种。修改建议：维持现状/通过工具进行导入。

`valuable_token_list`: 计价币种列表。计价币种是指在进行最佳交易路由选择时，纳入考虑范围的中间币种。修改建议：维持现状/通过工具进行导入。

`optional_token_list`: 自选币种列表。自选币种是指需要进行交易操作的币种。修改建议：通过工具进行导入。

## 其他说明

1. 使用的是`http/https`协议访问，所以`ws`协议特有的如`事件订阅`等功能是无法实现的，节点延迟也各有不同，但仅作为一个辅助交互的工具，它的功能本就无需过于复杂。
2. 没有支持自定义`GasPrice`，是因为在`BSC`链平均出块间隔仅为 3 秒的情况下，过高的`GasPrice`只会让你的交易`Gas`成本更高且没有必要，工具默认的`GasPrice`是`BSC.gas_price+10`wei，也就是`5.00000001`Gwei，这特意增加的 10wei，已经能让你在几乎不增加交易成本的前提下使得你的交易在 80%（甚至更高）的交易之前被确认，它足够让你领先大部分手动访问网页进行操作的人了。
3. 代码是开源的，安不安全这个问题由你自行审查，以此决定要不要使用它，我只是基于**技术交流分享**的目的将其分享出来，仅此而已。

## 使用示例

![1](/screenshot/1.png)

测试网环境：

![2](/screenshot/2.png)

![3](/screenshot/3.png)

![4](/screenshot/4.png)

![5](/screenshot/5.png)

![6](/screenshot/6.png)

![7](/screenshot/7.png)

主网环境：

![8](/screenshot/8.png)

![9](/screenshot/9.png)

# 尽责声明

由于涉及的领域较为敏感，请你事先详尽了解并严格遵守自己所在国家/地区的**相关法律法规**。

本项目仅出于**技术交流分享**的目的进行开源，**不作任何投资建议和引导**，任何人原则上都应只将其用于**技术研究/测试**，而不是用于任何实际的投资交易，由此导致的任何问题、责任、结果、损失都将由你自行承担、负责。

# 开源许可

本项目使用 [GPL-3.0](https://choosealicense.com/licenses/gpl-3.0/) 作为开源许可证。
