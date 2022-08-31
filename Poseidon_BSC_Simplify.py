from web3 import Web3
from loguru import logger
from sys import exit, exc_info
from json import dumps, dump
from time import time


class Chain():
    def __init__(self, RPCUrl: str, BscScanAPIKey: str):
        from web3 import HTTPProvider
        from web3.middleware import geth_poa_middleware
        from requests import Session
        from bscscan.core.sync_client import SyncClient as BscScan

        StartTime = time()
        self.Provider = Web3(HTTPProvider(RPCUrl))
        if self.Provider.isConnected():
            FinishTime = time()
            Delay = round((FinishTime - StartTime) * 1000)
            logger.success(f"\n[连接成功]成功连接至节点[{RPCUrl}] 延迟[{Delay} ms]")
            self.Provider.middleware_onion.inject(geth_poa_middleware, layer=0)
            self.BSC = self.Provider.eth
            self.BscScan = BscScan.from_session(api_key=BscScanAPIKey, session=Session())
            self.GetBasicInformation()
        else:
            logger.error(f"\n[连接失败]无法连接至节点[{RPCUrl}]")
            exit()

    def GetBasicInformation(self) -> tuple:
        try:
            self.ChainID = self.BSC.chainId
            assert(self.ChainID == 56 or self.ChainID == 97)
            self.GasPrice = self.BSC.gas_price
            BlockNumber = self.BSC.block_number
            self.BNBPrice = round(float(self.BscScan.get_bnb_last_price()["ethusd"]), 2)
            logger.success(f"\n[读取BSC链信息成功]\n[链ID]{self.ChainID}\n[当前块高度]{BlockNumber}\n[BNB价格]${self.BNBPrice}\n[GasPrice]{Web3.fromWei(self.GasPrice, 'gwei')} Gwei")
            return (self.ChainID, BlockNumber, self.BNBPrice, self.GasPrice)
        except Exception:
            ExceptionInformation = exc_info()
            logger.error(f"\n[读取BSC链信息失败]\n[异常信息]{ExceptionInformation}")
            exit()

    def GetTransactionByHash(self, TransactionHash: str) -> tuple:
        try:
            Info = self.BSC.wait_for_transaction_receipt(TransactionHash, timeout=60)
            Status = Info.status
            GasUsed = Info.gasUsed
            ContractAddress = Info.contractAddress
            Logs = Info.logs
            BlockNumber = Info.blockNumber
            Info = self.BSC.get_transaction(TransactionHash)
            From = Info["from"]
            To = Info.to
            InputData = Info.input
            Nonce = Info.nonce
            Value = Info.value
            ValueToBNB = Web3.fromWei(Value, 'ether')
            GasLimit = Info.gas
            GasPrice = Web3.fromWei(Info.gasPrice, "gwei")
            FeeToBNB = Web3.fromWei(Info.gasPrice * GasUsed, 'ether')
            FeeToUSD = round(self.BNBPrice * float(FeeToBNB), 2)
            if ContractAddress != None:
                TransactionType = "创建合约"
            elif Value != 0 and GasUsed <= 50000:
                TransactionType = "BNB转账"
            else:
                TransactionType = "调用合约(或其他类型的失败交易)"
            if TransactionType == "创建合约":
                logger.success(f"\n[查询交易信息成功]\n[交易哈希]{TransactionHash}\n[交易类型]{TransactionType}\n[交易状态]成功 [所在区块]{BlockNumber}\n[创建者]{From}\n[所建合约地址]{ContractAddress}\n[Nonce]{Nonce} [Value]{Value}({ValueToBNB} BNB ≈ ${round(self.BNBPrice*float(ValueToBNB),2)})\n[GasLimit]{GasLimit} [GasUsed]{GasUsed} [GasPrice]{GasPrice} Gwei\n[Fee]{FeeToBNB} BNB ≈ ${FeeToUSD}\n[InputData]{InputData}\n[Logs]{Logs}")
            elif Status == 1:
                logger.success(f"\n[查询交易信息成功]\n[交易哈希]{TransactionHash}\n[交易类型]{TransactionType}\n[交易状态]成功 [所在区块]{BlockNumber}\n[发送者]{From}\n[接收者]{To}\n[Nonce]{Nonce} [Value]{Value}({ValueToBNB} BNB ≈ ${round(self.BNBPrice*float(ValueToBNB),2)})\n[GasLimit]{GasLimit} [GasUsed]{GasUsed} [GasPrice]{GasPrice} Gwei\n[Fee]{FeeToBNB} BNB ≈ ${FeeToUSD}\n[InputData]{InputData}\n[Logs]{Logs}")
            else:
                logger.error(f"\n[查询交易信息成功]\n[交易哈希]{TransactionHash}\n[交易类型]{TransactionType}\n[交易状态]失败 [所在区块]{BlockNumber}\n[发送者]{From}\n[接收者]{To}\n[Nonce]{Nonce} [Value]{Value}({ValueToBNB} BNB ≈ ${round(self.BNBPrice*float(ValueToBNB),2)})\n[GasLimit]{GasLimit} [GasUsed]{GasUsed} [GasPrice]{GasPrice} Gwei\n[Fee]{FeeToBNB} BNB ≈ ${FeeToUSD}\n[InputData]{InputData}\n[Logs]{Logs}")
            return (TransactionHash, Status, BlockNumber, From, To, Nonce, Value, GasLimit, GasUsed, GasPrice, FeeToBNB, FeeToUSD, InputData, Logs, ContractAddress)
        except Exception:
            ExceptionInformation = exc_info()
            logger.error(f"\n[查询交易信息失败]\n[交易哈希]{TransactionHash}\n[异常信息]{ExceptionInformation}")
            return None

    def GetBalance(self, Address: str) -> int:
        try:
            Balance = self.BSC.get_balance(Address)
            logger.success(f"\n[查询BNB余额成功]\n[地址]{Address}\n[余额][{Balance} Wei]<=>[{Web3.fromWei(Balance,'ether')} BNB]")
            return Balance
        except Exception:
            ExceptionInformation = exc_info()
            logger.error(f"\n[查询BNB余额失败]\n[地址]{Address}\n[异常信息]{ExceptionInformation}")
            return None


class Account():
    def __init__(self, Chain: Chain, PrivateKey: str):
        try:
            self.Chain = Chain
            self.BSC = Chain.BSC
            AccountTemp = self.BSC.account.from_key(PrivateKey)
            self.Address = Web3.toChecksumAddress(AccountTemp.address)
            self.PrivateKey = AccountTemp.privateKey
            self.BSC.default_account = self.Address
            logger.success(f"\n[导入账户成功]成功导入[{self.Address}]")
            self.GetSelfBalance()
        except Exception:
            ExceptionInformation = exc_info()
            logger.error(f"\n[导入账户失败]\n[异常信息]{ExceptionInformation}")
            exit()

    def GetSelfBalance(self) -> int:
        Balance = self.Chain.GetBalance(self.Address)
        if Balance == 0:
            logger.warning(f"\n[余额不足警告]账户余额为0 无法发送交易")
        return Balance

    def SendTransaction(self, To: str, Data: str, GasLimit: int = 1000000, GasPrice: int = None, Value: int = 0) -> tuple:
        try:
            Txn = {
                "chainId": self.Chain.ChainID,
                "from": self.Address,
                "to": Web3.toChecksumAddress(To),
                "nonce": self.BSC.get_transaction_count(self.Address),
                "gas": GasLimit,
                "gasPrice": GasPrice if GasPrice else self.Chain.GasPrice + 10,
                "value": Value,
                "data": Data
            }
            SignedTxn = self.BSC.account.sign_transaction(Txn, self.PrivateKey)
            TransactionHash = self.BSC.send_raw_transaction(SignedTxn.rawTransaction).hex()
            Txn["gasPrice"] = f'{Web3.fromWei(Txn["gasPrice"],"gwei")} Gwei'
            logger.success(f"\n[发送交易成功]\n[交易哈希]{TransactionHash}\n[Txn]\n{dumps(Txn, indent=2)}")
            TransactionReceipt = self.Chain.GetTransactionByHash(TransactionHash)
            return TransactionReceipt
        except Exception:
            ExceptionInformation = exc_info()
            logger.error(f"\n[发送交易失败]\n[异常信息]{ExceptionInformation}")
            return None


class Contract():
    def __init__(self, Account: Account, Address: str, ABI: dict):
        try:
            self.Chain = Account.Chain
            self.Account = Account
            self.BSC = Account.BSC
            self.Address = Web3.toChecksumAddress(Address)
            self.Instance = self.BSC.contract(address=self.Address, abi=ABI)
            logger.success(f"\n[实例化合约成功]合约地址为[{self.Address}]")
        except Exception:
            ExceptionInformation = exc_info()
            logger.error(f"\n[实例化合约失败]\n[地址传参]{Address}\n[ABI传参]{ABI}\n[异常信息]{ExceptionInformation}")
            exit()

    def CallFunction(self, FunctionName: str, *FunctionArguments) -> tuple:
        try:
            TransactionData = self.Instance.functions[FunctionName](*FunctionArguments).buildTransaction({"value": 0, "gasPrice": self.Chain.GasPrice + 10})
            logger.success(
                f"\n[发起函数调用成功]\n[合约地址]{self.Address}\n[调用]{FunctionName}{FunctionArguments}\n[Value]{TransactionData['value']} [GasLimit]{TransactionData['gas']} [GasPrice]{Web3.fromWei(TransactionData['gasPrice'],'gwei')} Gwei")
            TransactionResult = self.Account.SendTransaction(self.Address, TransactionData["data"], TransactionData["gas"], TransactionData["value"])
            return TransactionResult
        except Exception:
            ExceptionInformation = exc_info()
            logger.error(f"\n[发起函数调用失败]\n[合约地址]{self.Address}\n[调用]{FunctionName}{FunctionArguments}\n[异常信息]{ExceptionInformation}")
            return None

    def ReadOnlyCallFunction(self, FunctionName: str, *FunctionArguments):
        try:
            Result = self.Instance.functions[FunctionName](*FunctionArguments).call()
            # logger.success(f"\n[只读函数调用成功]\n[合约地址]{self.Address}\n[调用]{FunctionName}{FunctionArguments}\n[结果]{Result}")
            return Result
        except Exception:
            ExceptionInformation = exc_info()
            logger.error(f"\n[只读函数调用失败]\n[合约地址]{self.Address}\n[调用]{FunctionName}{FunctionArguments}\n[异常信息]{ExceptionInformation}")
            return None

    def GetEstimateGas(self, FunctionName: str, *FunctionArguments) -> int:
        try:
            TransactionData = self.Instance.functions[FunctionName](*FunctionArguments).buildTransaction({"value": 0, "gasPrice": self.Chain.GasPrice + 10})
            return TransactionData["gas"]
        except Exception:
            ExceptionInformation = exc_info()
            logger.error(f"\n[获取预估Gas失败]\n[合约地址]{self.Address}\n[调用]{FunctionName}{FunctionArguments}\n[异常信息]{ExceptionInformation}")
            return 0


class ERC20(Contract):
    def __init__(self, Account: Account, Address: str, ABI: dict, Data: dict = {}):
        try:
            self.Chain = Account.Chain
            self.Account = Account
            self.BSC = Account.BSC
            self.Address = Web3.toChecksumAddress(Address)
            self.Instance = self.BSC.contract(address=self.Address, abi=ABI)
            self.Symbol = Data.get("symbol", None)
            self.Name = Data.get("name", None)
            self.Decimals = Data.get("decimals", None)
            if self.Symbol == None or self.Name == None or self.Decimals == None:
                self.InitInfo()
            logger.success(f"\n[实例化ERC20成功]\n[合约地址]{self.Address}\n[简称]{self.Symbol}\n[全称]{self.Name}\n[精度]{self.Decimals}")
        except Exception:
            ExceptionInformation = exc_info()
            logger.error(f"\n[实例化ERC20失败]\n[地址传参]{Address}\n[ABI传参]{ABI}\n[异常信息]{ExceptionInformation}")
            exit()

    def InitInfo(self):
        self.Symbol = self.GetSymbol()
        self.Name = self.GetName()
        self.Decimals = self.GetDecimals()

    def GetSymbol(self) -> str:
        return self.ReadOnlyCallFunction("symbol")

    def GetName(self) -> str:
        return self.ReadOnlyCallFunction("name")

    def GetDecimals(self) -> str:
        return self.ReadOnlyCallFunction("decimals")

    def GetTotalSupply(self) -> str:
        return self.ReadOnlyCallFunction("totalSupply")

    def GetBalanceOf(self, Owner: str) -> int:
        return self.ReadOnlyCallFunction("balanceOf", Web3.toChecksumAddress(Owner))

    def GetAllowance(self, Owner: str, Spender: str) -> int:
        return self.ReadOnlyCallFunction("allowance", Web3.toChecksumAddress(Owner), Web3.toChecksumAddress(Spender))

    def SendTransfer(self, To: str, Amount: int) -> tuple:
        return self.CallFunction("transfer", Web3.toChecksumAddress(To), Amount)

    def SendApprove(self, Spender: str, Amount: int) -> tuple:
        return self.CallFunction("approve", Web3.toChecksumAddress(Spender), Amount)

    def SendTransferFrom(self, From: str, To: str, Amount: int) -> tuple:
        return self.CallFunction("transferFrom", Web3.toChecksumAddress(From), Web3.toChecksumAddress(To), Amount)


class Router(Contract):
    def ReadOnlyCallFunction(self, FunctionName: str, *FunctionArguments):
        Result = self.Instance.functions[FunctionName](*FunctionArguments).call()
        return Result

    def GetAmountsOut(self, AmountIn: int, Path: list) -> list:
        return self.ReadOnlyCallFunction("getAmountsOut", AmountIn, Path)

    def SwapExactTokensForTokensSupportingFeeOnTransferTokens(self, AmountIn: int, AmountOutMin: int, Path: list, To: str, Deadline: int):
        return self.CallFunction("swapExactTokensForTokensSupportingFeeOnTransferTokens", AmountIn, AmountOutMin, Path, To, Deadline)


class Utils():
    @staticmethod
    def SimplyEncryptPrivateKey(PrivateKey):
        from base64 import b64encode
        PrivateKeyBase64 = b64encode(PrivateKey.encode()).decode()
        return PrivateKeyBase64

    @staticmethod
    def SimplyDecryptPrivateKey(PrivateKeyBase64):
        from base64 import b64decode
        PrivateKey = b64decode(PrivateKeyBase64.encode()).decode()
        return PrivateKey
