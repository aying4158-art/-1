"""
账户转账模块
提供账户类和转账功能
"""


class InsufficientBalanceError(Exception):
    """余额不足异常"""
    pass


class InvalidAmountError(Exception):
    """无效金额异常"""
    pass


class Account:
    """账户类"""
    
    def __init__(self, account_id: str, balance: float = 0.0):
        """
        初始化账户
        
        Args:
            account_id: 账户ID
            balance: 初始余额，默认为0
        """
        self.account_id = account_id
        self.balance = balance
    
    def deposit(self, amount: float) -> None:
        """
        存款
        
        Args:
            amount: 存款金额
        
        Raises:
            InvalidAmountError: 金额为负数或零
        """
        if amount <= 0:
            raise InvalidAmountError(f"存款金额必须大于0，当前金额: {amount}")
        self.balance += amount
    
    def withdraw(self, amount: float) -> None:
        """
        取款
        
        Args:
            amount: 取款金额
        
        Raises:
            InvalidAmountError: 金额为负数或零
            InsufficientBalanceError: 余额不足
        """
        if amount <= 0:
            raise InvalidAmountError(f"取款金额必须大于0，当前金额: {amount}")
        if self.balance < amount:
            raise InsufficientBalanceError(
                f"余额不足。当前余额: {self.balance}, 尝试取款: {amount}"
            )
        self.balance -= amount
    
    def __repr__(self):
        return f"Account(id={self.account_id}, balance={self.balance})"


def transfer(account_a: Account, account_b: Account, amount: float) -> None:
    """
    从账户A转账到账户B
    
    Args:
        account_a: 转出账户
        account_b: 转入账户
        amount: 转账金额
    
    Raises:
        InvalidAmountError: 转账金额为负数或零
        InsufficientBalanceError: 账户A余额不足
        ValueError: 账户参数无效
    
    Examples:
        >>> acc_a = Account("A001", 1000)
        >>> acc_b = Account("B001", 500)
        >>> transfer(acc_a, acc_b, 200)
        >>> print(acc_a.balance)  # 800
        >>> print(acc_b.balance)  # 700
    """
    # 参数验证
    if not isinstance(account_a, Account) or not isinstance(account_b, Account):
        raise ValueError("账户参数必须是Account类型")
    
    # 金额验证
    if amount <= 0:
        raise InvalidAmountError(f"转账金额必须大于0，当前金额: {amount}")
    
    # 余额验证
    if account_a.balance < amount:
        raise InsufficientBalanceError(
            f"账户 {account_a.account_id} 余额不足。"
            f"当前余额: {account_a.balance}, 尝试转账: {amount}"
        )
    
    # 执行转账
    account_a.withdraw(amount)
    account_b.deposit(amount)
