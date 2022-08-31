from Poseidon_BSC_Simplify import *

Config, NetworkEnvironment, ERC20ABI, chain, account, router = None, None, None, None, None, None


def Init():
    from json import load
    try:
        global Config, NetworkEnvironment, ERC20ABI, chain, account, router
        StartTime = time()
        with open("config.json", "r", encoding="utf-8") as f:
            Config = load(f)
        with open("abi\\ERC20\\ERC20_ABI.json", "r", encoding="utf-8") as f:
            ERC20ABI = load(f)
        with open("abi\\PancakeSwap\\PancakeRouter02_ABI.json", "r", encoding="utf-8") as f:
            RouterABI = load(f)
        NetworkEnvironment = Config["basic"]["network_environment"]
        assert(NetworkEnvironment == "mainnet" or NetworkEnvironment == "testnet")
        chain = Chain(Config["basic"][f"bsc_{NetworkEnvironment}_rpc"], Config["basic"]["bscscan_api_key"])
        account = Account(chain, Utils.SimplyDecryptPrivateKey(Config["swap"]["private_key_base64"]))
        router = Router(account, Config["swap"][NetworkEnvironment]["pancakeswap_router_address"], RouterABI)
        FinishTime = time()
        Delay = round(FinishTime - StartTime, 2)
        logger.success(f"\n[初始化][成功]共耗时[{Delay} s]")
        Select()
    except Exception:
        ExceptionInformation = exc_info()
        logger.error(f"\n[初始化][失败]\n[异常信息]{ExceptionInformation}")
        return


def Select():
    try:
        global Config, NetworkEnvironment, ERC20ABI, account
        TokenList = Config["swap"][NetworkEnvironment]["optional_token_list"]
        Temp = ["\n[选择币种]\n自选币种列表如下:"]
        for index, item in enumerate(TokenList):
            Temp.append(f"[{index+1}][{item['symbol']}({item['name']})-{item['address']}]")
        Temp.append("[0]导入币种")
        Temp = "\n".join(Temp)
        logger.success(Temp)
        Index = input("[选择币种]请输入要操作币种的序号:")
        if Index == "":
            logger.warning("\n[选择币种]未作出选择,程序已退出.")
            exit()
        elif Index == "0":
            Import()
        else:
            Index = int(Index) - 1
            assert(0 <= Index < len(TokenList))
            Coin = ERC20(account, TokenList[Index]["address"], ERC20ABI, TokenList[Index])
            Index = Config["swap"]["fund_token_use"]
            KeyCoinInfo = Config["swap"][NetworkEnvironment]["fund_token_list"][Index]
            KeyCoin = ERC20(account, KeyCoinInfo["address"], ERC20ABI, KeyCoinInfo)
            Swap(Coin, KeyCoin)
    except Exception:
        ExceptionInformation = exc_info()
        logger.error(f"\n[选择币种]\n[异常信息]{ExceptionInformation}")
        Select()


def Import():
    try:
        global Config, NetworkEnvironment, ERC20ABI, account
        logger.success(f"\n[导入币种]\n[1]自选币种 [2]计价币种 [3]资金币种 [0]返回")
        Index = input("[导入币种]请输入要导入币种类型的序号:")
        if Index == "":
            logger.warning("\n[导入币种]未作出选择,程序已退出.")
            exit()
        elif Index == "0":
            Select()
        else:
            if Index not in ["1", "2", "3"]:
                logger.warning("\n[导入币种]选项错误,已返回.")
                Select()
            else:
                if Index == "1":
                    ListName = "optional_token_list"
                elif Index == "2":
                    ListName = "valuable_token_list"
                elif Index == "3":
                    ListName = "fund_token_list"
                Address = input("[导入币种]请输入要导入币种的合约地址:")
                if Address == "":
                    logger.warning("\n[导入币种]未输入地址,程序已退出.")
                    exit()
                else:
                    ERC20Temp = ERC20(account, Address, ERC20ABI)
                    Data = {"symbol": ERC20Temp.Symbol, "name": ERC20Temp.Name, "decimals": ERC20Temp.Decimals, "address": ERC20Temp.Address}
                    Config["swap"][NetworkEnvironment][ListName].append(Data)
                    with open(f'config.json', 'w') as f:
                        dump(Config, f, indent=4)
                    logger.success(f"\n[导入币种][成功]\n[简称]{ERC20Temp.Symbol}\n[全称]{ERC20Temp.Name}\n[精度]{ERC20Temp.Decimals}\n[地址]{ERC20Temp.Address}")
                    Select()
    except Exception:
        ExceptionInformation = exc_info()
        logger.error(f"\n[导入币种][失败]\n[异常信息]{ExceptionInformation}")
        Select()


def Swap(Coin: ERC20, KeyCoin: ERC20):
    try:
        global account
        CoinBalanceAmount = round(Coin.GetBalanceOf(account.Address) / pow(10, Coin.Decimals), 4)
        logger.success(f"\n[交易]\n[当前币种]{Coin.Symbol}({Coin.Name})-{Coin.Address}\n[币种余额]{CoinBalanceAmount} {Coin.Symbol}\n[1]买入 [2]卖出 [0]返回")
        Index = input("[交易]请输入要执行的操作:")
        if Index == "":
            logger.warning("\n[交易]未作出选择,程序已退出.")
            exit()
        elif Index == "0":
            Select()
        elif Index == "1":
            Buy(Coin, KeyCoin)
        elif Index == "2":
            Sell(Coin, KeyCoin)
        else:
            logger.warning("\n[交易]选项错误,程序已返回.")
            Select()
    except Exception:
        ExceptionInformation = exc_info()
        logger.error(f"\n[交易]\n[异常信息]{ExceptionInformation}")
        Select()


def Buy(Coin: ERC20, KeyCoin: ERC20):
    try:
        global Config, account
        assert(KeyCoin.Address != Coin.Address)
        KeyCoinBalanceValue = KeyCoin.GetBalanceOf(account.Address)
        logger.success(f"\n[买入]\n[资金币种]{KeyCoin.Symbol}({KeyCoin.Name})-{KeyCoin.Address}\n[资金余额]{round(KeyCoinBalanceValue / pow(10, KeyCoin.Decimals), 4)} {KeyCoin.Symbol}")
        InputValue = input(f"[买入]请输入要买入的金额({KeyCoin.Symbol}):")
        Value = 0
        if InputValue == "":
            logger.warning("\n[买入]未输入金额,程序已退出.")
            exit()
        elif InputValue == "全仓":
            logger.warning("\n[买入]您选择了全仓买入,是否确定?\n[1]确定 [0]取消")
            Index = input("[买入]请输入选择:")
            if Index == "":
                logger.warning("\n[买入]未作出选择,程序已退出.")
                exit()
            elif Index == "1":
                Value = KeyCoinBalanceValue
            elif Index == "0":
                Buy(Coin, KeyCoin)
                return
        if Value == 0:
            Value = int(float(InputValue) * pow(10, KeyCoin.Decimals))
        assert(0 < Value <= KeyCoinBalanceValue)
        SlippageTolerance = Config["swap"]["buy_slippage_tolerance"]
        MinimumValue, PathList, Deadline = GetBuyInformation(Coin, KeyCoin, Value, SlippageTolerance)
        Index = input("[1]确定 [0]取消 [2]修改滑点\n[买入]是否确定发送交易:")
        if Index == "":
            logger.warning("\n[买入]未作出选择,程序已退出.")
            exit()
        elif Index == "1":
            ConfirmBuy(Coin, KeyCoin, Value, MinimumValue, PathList, Deadline)
        elif Index == "0":
            logger.warning("\n[买入]取消发送交易.")
            Swap(Coin, KeyCoin)
        elif Index == "2":
            SlippageTolerance = input("[买入]请输入修改的值:")
            if SlippageTolerance == "":
                logger.warning("\n[买入]未输入任何值,程序已退出.")
                exit()
            else:
                SlippageTolerance = float(SlippageTolerance)
                assert(0 <= SlippageTolerance <= 100)
                MinimumValue, PathList, Deadline = GetBuyInformation(Coin, KeyCoin, Value, SlippageTolerance)
                Index = input("[1]确定 [0]取消\n[买入]是否确定发送交易:")
                if Index == "":
                    logger.warning("\n[买入]未作出选择,程序已退出.")
                    exit()
                elif Index == "1":
                    ConfirmBuy(Coin, KeyCoin, Value, MinimumValue, PathList, Deadline)
                elif Index == "0":
                    logger.warning("\n[买入]取消发送交易.")
                    Swap(Coin, KeyCoin)
                else:
                    logger.warning("\n[买入]选项错误,程序已返回.")
                    Swap(Coin, KeyCoin)
        else:
            logger.warning("\n[买入]选项错误,程序已返回.")
            Swap(Coin, KeyCoin)
    except Exception:
        ExceptionInformation = exc_info()
        logger.error(f"\n[买入]\n[异常信息]{ExceptionInformation}")
        Select()


def Sell(Coin: ERC20, KeyCoin: ERC20):
    try:
        global Config, account
        assert(KeyCoin.Address != Coin.Address)
        CoinBalanceValue = Coin.GetBalanceOf(account.Address)
        logger.success(f"\n[卖出]\n[当前币种]{Coin.Symbol}({Coin.Name})-{Coin.Address}\n[币种余额]{round(CoinBalanceValue / pow(10, Coin.Decimals), 4)} {Coin.Symbol}")
        assert(CoinBalanceValue != 0)
        SlippageTolerance = Config["swap"]["sell_slippage_tolerance"]
        MinimumValue, PathList, Deadline = GetSellInformation(Coin, KeyCoin, CoinBalanceValue, SlippageTolerance)
        Index = input("[1]确定 [0]取消 [2]修改滑点\n[卖出][全仓]是否确定发送交易:")
        if Index == "":
            logger.warning("\n[卖出]未作出选择,程序已退出.")
            exit()
        elif Index == "1":
            ConfirmSell(Coin, KeyCoin, CoinBalanceValue, MinimumValue, PathList, Deadline)
        elif Index == "0":
            logger.warning("\n[卖出]取消发送交易.")
            Swap(Coin, KeyCoin)
        elif Index == "2":
            SlippageTolerance = input("[卖出]请输入修改的值:")
            if SlippageTolerance == "":
                logger.warning("\n[卖出]未输入任何值,程序已退出.")
                exit()
            else:
                SlippageTolerance = float(SlippageTolerance)
                assert(0 <= SlippageTolerance <= 100)
                MinimumValue, PathList, Deadline = GetSellInformation(Coin, KeyCoin, CoinBalanceValue, SlippageTolerance)
                Index = input("[1]确定 [0]取消\n[卖出][全仓]是否确定发送交易:")
                if Index == "":
                    logger.warning("\n[卖出]未作出选择,程序已退出.")
                    exit()
                elif Index == "1":
                    ConfirmSell(Coin, KeyCoin, CoinBalanceValue, MinimumValue, PathList, Deadline)
                elif Index == "0":
                    logger.warning("\n[卖出]取消发送交易.")
                    Swap(Coin, KeyCoin)
                else:
                    logger.warning("\n[卖出]选项错误,程序已返回.")
                    Swap(Coin, KeyCoin)
        else:
            logger.warning("\n[卖出]选项错误,程序已返回.")
            Swap(Coin, KeyCoin)
    except Exception:
        ExceptionInformation = exc_info()
        logger.error(f"\n[卖出]\n[异常信息]{ExceptionInformation}")
        Select()


def GetBuyInformation(Coin: ERC20, KeyCoin: ERC20, KeyCoinValue: int, SlippageTolerance: float) -> tuple:
    try:
        global chain, account, router
        if CheckAndApprove(KeyCoin, KeyCoinValue):
            GasPrice = chain.GasPrice + 10
            RouterInformation = ChooseBuyRouterPath(Coin, KeyCoin, KeyCoinValue)
            PathList = RouterInformation["path_list"]
            PathName = RouterInformation["path_name"]
            EstimatedValue = RouterInformation["value"]
            Price = (KeyCoinValue / pow(10, KeyCoin.Decimals)) / (EstimatedValue / pow(10, Coin.Decimals))
            MinimumValue = int(EstimatedValue * (100 - SlippageTolerance) / 100)
            Fee = round((KeyCoinValue / pow(10, KeyCoin.Decimals)) * (0.25 * (len(PathList) - 1) / 100), 4)
            Deadline = round(time() + 5 * 60)
            EstimatedGasLimit = router.GetEstimateGas("swapExactTokensForTokensSupportingFeeOnTransferTokens", KeyCoinValue, MinimumValue, PathList, account.Address, Deadline)
            assert(EstimatedGasLimit != 0)
            EstimatedGasFee = round(float(Web3.fromWei(EstimatedGasLimit * GasPrice, "ether")) * chain.BNBPrice, 2)
            logger.success(f"\n[买入][模拟交易成功]\n[当前币种]{Coin.Symbol}({Coin.Name})-{Coin.Address}\n[资金币种]{KeyCoin.Symbol}({KeyCoin.Name})-{KeyCoin.Address}\n[币对价格]{Price:.18f} {Coin.Symbol}/{KeyCoin.Symbol}\n[买入金额]{round(KeyCoinValue/pow(10,KeyCoin.Decimals),4)} {KeyCoin.Symbol}\n[预计得到]{round(EstimatedValue/pow(10,Coin.Decimals),4)} {Coin.Symbol}(最少得到 {round(MinimumValue/pow(10,Coin.Decimals),4)} {Coin.Symbol})\n[兑换路由]{PathName}\n[滑点容差]{SlippageTolerance}%\n[手续费]{Fee} {KeyCoin.Symbol}\n[GasPrice]{Web3.fromWei(GasPrice,'gwei')} Gwei\n[预估Gas消耗]{EstimatedGasLimit}(${EstimatedGasFee})\n[时间容限]5分钟")
            return (MinimumValue, PathList, Deadline)
        else:
            Select()
    except:
        ExceptionInformation = exc_info()
        logger.error(f"\n[买入][模拟交易失败]\n[异常信息]{ExceptionInformation}")
        Select()


def GetSellInformation(Coin: ERC20, KeyCoin: ERC20, CoinValue: int, SlippageTolerance: float) -> tuple:
    try:
        global chain, account, router
        if CheckAndApprove(Coin, CoinValue):
            GasPrice = chain.GasPrice + 10
            RouterInformation = ChooseSellRouterPath(Coin, KeyCoin, CoinValue)
            PathList = RouterInformation["path_list"]
            PathName = RouterInformation["path_name"]
            EstimatedValue = RouterInformation["value"]
            Price = (EstimatedValue / pow(10, KeyCoin.Decimals)) / (CoinValue / pow(10, Coin.Decimals))
            MinimumValue = int(EstimatedValue * (100 - SlippageTolerance) / 100)
            Fee = round((CoinValue / pow(10, Coin.Decimals)) * (0.25 * (len(PathList) - 1) / 100), 4)
            Deadline = round(time() + 5 * 60)
            EstimatedGasLimit = router.GetEstimateGas("swapExactTokensForTokensSupportingFeeOnTransferTokens", CoinValue, MinimumValue, PathList, account.Address, Deadline)
            assert(EstimatedGasLimit != 0)
            EstimatedGasFee = round(float(Web3.fromWei(EstimatedGasLimit * GasPrice, "ether")) * chain.BNBPrice, 2)
            logger.success(f"\n[卖出][模拟交易成功]\n[当前币种]{Coin.Symbol}({Coin.Name})-{Coin.Address}\n[资金币种]{KeyCoin.Symbol}({KeyCoin.Name})-{KeyCoin.Address}\n[币对价格]{Price:.18f} {Coin.Symbol}/{KeyCoin.Symbol}\n[卖出数量]{round(CoinValue/pow(10,Coin.Decimals),4)} {Coin.Symbol}\n[预计得到]{round(EstimatedValue/pow(10,KeyCoin.Decimals),4)} {KeyCoin.Symbol}(最少得到 {round(MinimumValue/pow(10,KeyCoin.Decimals),4)} {KeyCoin.Symbol})\n[兑换路由]{PathName}\n[滑点容差]{SlippageTolerance}%\n[手续费]{Fee} {Coin.Symbol}\n[GasPrice]{Web3.fromWei(GasPrice,'gwei')} Gwei\n[预估Gas消耗]{EstimatedGasLimit}(${EstimatedGasFee})\n[时间容限]5分钟")
            return (MinimumValue, PathList, Deadline)
        else:
            Select()
    except:
        ExceptionInformation = exc_info()
        logger.error(f"\n[卖出][模拟交易失败]\n[异常信息]{ExceptionInformation}")
        Select()


def ChooseBuyRouterPath(Coin: ERC20, KeyCoin: ERC20, KeyCoinValue: int) -> dict:
    try:
        global Config, NetworkEnvironment, router
        ValuableTokenList = Config["swap"][NetworkEnvironment]["valuable_token_list"]
        RouterInformation = []
        try:
            ValueTemp = router.GetAmountsOut(KeyCoinValue, [KeyCoin.Address, Coin.Address])
        except:
            ValueTemp = [0]
        RouterInformation.append({"path_list": [KeyCoin.Address, Coin.Address], "path_name": f"{KeyCoin.Symbol}->{Coin.Symbol}", "value": ValueTemp[-1]})
        for item in ValuableTokenList:
            if item["address"] != KeyCoin.Address and item["address"] != Coin.Address:
                try:
                    ValueTemp = router.GetAmountsOut(KeyCoinValue, [KeyCoin.Address, item["address"], Coin.Address])
                except:
                    ValueTemp = [0]
                RouterInformation.append({"path_list": [KeyCoin.Address, item["address"], Coin.Address], "path_name": f"{KeyCoin.Symbol}->{item['symbol']}->{Coin.Symbol}", "value": ValueTemp[-1]})
        RouterInformation.sort(key=lambda x: x["value"], reverse=True)
        assert(RouterInformation[0]["value"] > 0)
        return RouterInformation[0]
    except:
        ExceptionInformation = exc_info()
        logger.error(f"\n[买入][获取路由失败]\n[异常信息]{ExceptionInformation}")
        Select()


def ChooseSellRouterPath(Coin: ERC20, KeyCoin: ERC20, CoinValue: int) -> dict:
    try:
        global Config, NetworkEnvironment, router
        ValuableTokenList = Config["swap"][NetworkEnvironment]["valuable_token_list"]
        RouterInformation = []
        try:
            ValueTemp = router.GetAmountsOut(CoinValue, [Coin.Address, KeyCoin.Address])
        except:
            ValueTemp = [0]
        RouterInformation.append({"path_list": [Coin.Address, KeyCoin.Address], "path_name": f"{Coin.Symbol}->{KeyCoin.Symbol}", "value": ValueTemp[-1]})
        for item in ValuableTokenList:
            if item["address"] != KeyCoin.Address and item["address"] != Coin.Address:
                try:
                    ValueTemp = router.GetAmountsOut(CoinValue, [Coin.Address, item["address"], KeyCoin.Address])
                except:
                    ValueTemp = [0]
                RouterInformation.append({"path_list": [Coin.Address, item["address"], KeyCoin.Address], "path_name": f"{Coin.Symbol}->{item['symbol']}->{KeyCoin.Symbol}", "value": ValueTemp[-1]})
        RouterInformation.sort(key=lambda x: x["value"], reverse=True)
        assert(RouterInformation[0]["value"] > 0)
        return RouterInformation[0]
    except:
        ExceptionInformation = exc_info()
        logger.error(f"\n[卖出][获取路由失败]\n[异常信息]{ExceptionInformation}")
        Select()


def ConfirmBuy(Coin: ERC20, KeyCoin: ERC20, KeyCoinValue: int, MinimumValue: int, PathList: list, Deadline: int):
    try:
        global account, router
        BalanceBefore = Coin.GetBalanceOf(account.Address)
        TransactionReceipt = router.SwapExactTokensForTokensSupportingFeeOnTransferTokens(KeyCoinValue, MinimumValue, PathList, account.Address, Deadline)
        if TransactionReceipt[1]:
            BalanceAfter = Coin.GetBalanceOf(account.Address)
            RealIncome = BalanceAfter - BalanceBefore
            RealPrice = (KeyCoinValue / pow(10, KeyCoin.Decimals)) / (RealIncome / pow(10, Coin.Decimals))
            RealGasUsed = TransactionReceipt[-7]
            RealGasFee = TransactionReceipt[-4]
            logger.success(
                f"\n[买入][成功]\n[当前币种]{Coin.Symbol}({Coin.Name})-{Coin.Address}\n[资金币种]{KeyCoin.Symbol}({KeyCoin.Name})-{KeyCoin.Address}\n[实际买入价格]{RealPrice:.18f} {Coin.Symbol}/{KeyCoin.Symbol}\n[实际买入数量]{round(RealIncome/ pow(10, Coin.Decimals),4)} {Coin.Symbol}\n[实际Gas消耗]{RealGasUsed}(${RealGasFee})")
            Swap(Coin, KeyCoin)
        else:
            logger.error(f"\n[买入][失败]交易失败,请检查情况!")
            Swap(Coin, KeyCoin)
    except:
        ExceptionInformation = exc_info()
        logger.error(f"\n[买入]\n[异常信息]{ExceptionInformation}")
        Select()


def ConfirmSell(Coin: ERC20, KeyCoin: ERC20, CoinValue: int, MinimumValue: int, PathList: list, Deadline: int):
    try:
        global account, router
        BalanceBefore = KeyCoin.GetBalanceOf(account.Address)
        TransactionReceipt = router.SwapExactTokensForTokensSupportingFeeOnTransferTokens(CoinValue, MinimumValue, PathList, account.Address, Deadline)
        if TransactionReceipt[1]:
            BalanceAfter = KeyCoin.GetBalanceOf(account.Address)
            RealIncome = BalanceAfter - BalanceBefore
            RealPrice = (RealIncome / pow(10, KeyCoin.Decimals)) / (CoinValue / pow(10, Coin.Decimals))
            RealGasUsed = TransactionReceipt[-7]
            RealGasFee = TransactionReceipt[-4]
            logger.success(
                f"\n[卖出][成功]\n[当前币种]{Coin.Symbol}({Coin.Name})-{Coin.Address}\n[资金币种]{KeyCoin.Symbol}({KeyCoin.Name})-{KeyCoin.Address}\n[实际卖出价格]{RealPrice:.18f} {Coin.Symbol}/{KeyCoin.Symbol}\n[实际卖出金额]{round(RealIncome/ pow(10, KeyCoin.Decimals),4)} {KeyCoin.Symbol}\n[实际Gas消耗]{RealGasUsed}(${RealGasFee})")
            Swap(Coin, KeyCoin)
        else:
            logger.error(f"\n[卖出][失败]交易失败,请检查情况!")
            Swap(Coin, KeyCoin)
    except:
        ExceptionInformation = exc_info()
        logger.error(f"\n[卖出]\n[异常信息]{ExceptionInformation}")
        Select()


def CheckAndApprove(Coin: ERC20, CoinValue: int) -> bool:
    try:
        global account, router
        Allowance = Coin.GetAllowance(account.Address, router.Address)
        if Allowance == 0 or Allowance < CoinValue:
            logger.warning(f"\n[授权检测]您还未授权路由转移您的{Coin.Symbol},是否确定授权?\n[1]确定 [0]取消")
            Index = input("[授权检测]请输入选择:")
            if Index == "":
                logger.warning("\n[授权检测]未作出选择,程序已退出.")
                exit()
            elif Index == "1":
                import web3.constants
                TransactionReceipt = Coin.SendApprove(router.Address, int(web3.constants.MAX_INT, 16))
                if TransactionReceipt[1]:
                    logger.success(f"\n[授权检测]授权转移{Coin.Symbol}成功")
                    return True
                else:
                    logger.error(f"\n[授权检测]授权转移{Coin.Symbol}失败")
                    return False
            elif Index == "0":
                logger.warning(f"\n[授权检测]取消授权.")
                return False
            else:
                logger.warning("\n[授权检测]选项错误,程序已返回.")
                Select()
        else:
            logger.success(f"\n[授权检测]先前已授权.")
            return True
    except:
        ExceptionInformation = exc_info()
        logger.error(f"\n[授权检测]\n[异常信息]{ExceptionInformation}")
        Select()


if __name__ == "__main__":
    Init()
