"""
账户转账功能测试套件
使用 pytest 和 unittest.mock 进行测试
"""

import pytest
from unittest.mock import Mock, patch, call
from account import Account, transfer, InsufficientBalanceError, InvalidAmountError


class TestAccount:
    """账户类测试"""
    
    def test_account_initialization(self):
        """测试账户初始化"""
        account = Account("A001", 1000)
        assert account.account_id == "A001"
        assert account.balance == 1000
    
    def test_account_default_balance(self):
        """测试账户默认余额为0"""
        account = Account("A002")
        assert account.balance == 0
    
    def test_deposit_success(self):
        """测试存款成功"""
        account = Account("A001", 100)
        account.deposit(50)
        assert account.balance == 150
    
    def test_deposit_invalid_amount(self):
        """测试存款金额无效"""
        account = Account("A001", 100)
        with pytest.raises(InvalidAmountError):
            account.deposit(-50)
        with pytest.raises(InvalidAmountError):
            account.deposit(0)
    
    def test_withdraw_success(self):
        """测试取款成功"""
        account = Account("A001", 100)
        account.withdraw(50)
        assert account.balance == 50
    
    def test_withdraw_insufficient_balance(self):
        """测试取款余额不足"""
        account = Account("A001", 100)
        with pytest.raises(InsufficientBalanceError):
            account.withdraw(150)


class TestTransferNormalCases:
    """转账正常场景测试"""
    
    def test_transfer_success(self):
        """测试正常转账成功"""
        account_a = Account("A001", 1000)
        account_b = Account("B001", 500)
        
        transfer(account_a, account_b, 200)
        
        assert account_a.balance == 800
        assert account_b.balance == 700
    
    def test_transfer_exact_balance(self):
        """测试转账金额等于余额"""
        account_a = Account("A001", 500)
        account_b = Account("B001", 0)
        
        transfer(account_a, account_b, 500)
        
        assert account_a.balance == 0
        assert account_b.balance == 500
    
    def test_transfer_small_amount(self):
        """测试转账小额金额"""
        account_a = Account("A001", 100)
        account_b = Account("B001", 50)
        
        transfer(account_a, account_b, 0.01)
        
        assert account_a.balance == pytest.approx(99.99)
        assert account_b.balance == pytest.approx(50.01)
    
    def test_transfer_large_amount(self):
        """测试转账大额金额"""
        account_a = Account("A001", 1000000)
        account_b = Account("B001", 0)
        
        transfer(account_a, account_b, 999999)
        
        assert account_a.balance == 1
        assert account_b.balance == 999999


class TestTransferInsufficientBalance:
    """转账余额不足测试"""
    
    def test_transfer_insufficient_balance(self):
        """测试余额不足时抛出异常"""
        account_a = Account("A001", 100)
        account_b = Account("B001", 500)
        
        with pytest.raises(InsufficientBalanceError) as exc_info:
            transfer(account_a, account_b, 200)
        
        # 验证异常信息
        assert "余额不足" in str(exc_info.value)
        assert "A001" in str(exc_info.value)
        
        # 验证余额未改变
        assert account_a.balance == 100
        assert account_b.balance == 500
    
    def test_transfer_zero_balance(self):
        """测试零余额转账"""
        account_a = Account("A001", 0)
        account_b = Account("B001", 100)
        
        with pytest.raises(InsufficientBalanceError):
            transfer(account_a, account_b, 50)
        
        assert account_a.balance == 0
        assert account_b.balance == 100
    
    def test_transfer_slightly_insufficient(self):
        """测试余额略微不足"""
        account_a = Account("A001", 99.99)
        account_b = Account("B001", 0)
        
        with pytest.raises(InsufficientBalanceError):
            transfer(account_a, account_b, 100)
        
        assert account_a.balance == 99.99
        assert account_b.balance == 0


class TestTransferNegativeAmount:
    """转账负数金额测试"""
    
    def test_transfer_negative_amount(self):
        """测试负数金额转账"""
        account_a = Account("A001", 1000)
        account_b = Account("B001", 500)
        
        with pytest.raises(InvalidAmountError) as exc_info:
            transfer(account_a, account_b, -100)
        
        # 验证异常信息
        assert "必须大于0" in str(exc_info.value)
        
        # 验证余额未改变
        assert account_a.balance == 1000
        assert account_b.balance == 500
    
    def test_transfer_zero_amount(self):
        """测试零金额转账"""
        account_a = Account("A001", 1000)
        account_b = Account("B001", 500)
        
        with pytest.raises(InvalidAmountError):
            transfer(account_a, account_b, 0)
        
        assert account_a.balance == 1000
        assert account_b.balance == 500
    
    def test_transfer_very_small_negative(self):
        """测试极小负数金额"""
        account_a = Account("A001", 1000)
        account_b = Account("B001", 500)
        
        with pytest.raises(InvalidAmountError):
            transfer(account_a, account_b, -0.01)
        
        assert account_a.balance == 1000
        assert account_b.balance == 500


class TestTransferWithMock:
    """使用 Mock 测试转账功能"""
    
    def test_transfer_calls_withdraw_and_deposit(self):
        """测试转账调用了 withdraw 和 deposit 方法"""
        account_a = Mock(spec=Account)
        account_a.balance = 1000
        account_a.account_id = "A001"
        
        account_b = Mock(spec=Account)
        account_b.balance = 500
        account_b.account_id = "B001"
        
        transfer(account_a, account_b, 200)
        
        # 验证方法调用
        account_a.withdraw.assert_called_once_with(200)
        account_b.deposit.assert_called_once_with(200)
    
    def test_transfer_withdraw_before_deposit(self):
        """测试转账先取款后存款的顺序"""
        account_a = Mock(spec=Account)
        account_a.balance = 1000
        account_a.account_id = "A001"
        
        account_b = Mock(spec=Account)
        account_b.balance = 500
        account_b.account_id = "B001"
        
        # 创建一个管理器来跟踪调用顺序
        manager = Mock()
        manager.attach_mock(account_a, 'account_a')
        manager.attach_mock(account_b, 'account_b')
        
        transfer(account_a, account_b, 200)
        
        # 验证调用顺序：先 withdraw 后 deposit
        expected_calls = [
            call.account_a.withdraw(200),
            call.account_b.deposit(200)
        ]
        assert manager.mock_calls == expected_calls
    
    def test_transfer_with_mock_spec(self):
        """测试使用 Mock spec 验证类型检查"""
        # 创建带有 spec 的模拟账户实例
        mock_a = Mock(spec=Account)
        mock_a.balance = 1000
        mock_a.account_id = "A001"
        
        mock_b = Mock(spec=Account)
        mock_b.balance = 500
        mock_b.account_id = "B001"
        
        transfer(mock_a, mock_b, 150)
        
        mock_a.withdraw.assert_called_once_with(150)
        mock_b.deposit.assert_called_once_with(150)


class TestTransferEdgeCases:
    """转账边界条件测试"""
    
    def test_transfer_invalid_account_type(self):
        """测试无效的账户类型"""
        account_a = Account("A001", 1000)
        invalid_account = "not_an_account"
        
        with pytest.raises(ValueError):
            transfer(account_a, invalid_account, 100)
    
    def test_transfer_none_accounts(self):
        """测试 None 账户"""
        account_a = Account("A001", 1000)
        
        with pytest.raises(ValueError):
            transfer(account_a, None, 100)
        
        with pytest.raises(ValueError):
            transfer(None, account_a, 100)
    
    def test_transfer_same_account(self):
        """测试同一账户转账（允许）"""
        account = Account("A001", 1000)
        
        # 同一账户转账应该成功（先减后加）
        transfer(account, account, 100)
        
        # 余额应该不变
        assert account.balance == 1000
    
    def test_transfer_floating_point_precision(self):
        """测试浮点数精度问题"""
        account_a = Account("A001", 0.1 + 0.2)  # 可能是 0.30000000000000004
        account_b = Account("B001", 0)
        
        transfer(account_a, account_b, 0.3)
        
        assert account_a.balance == pytest.approx(0)
        assert account_b.balance == pytest.approx(0.3)


class TestTransferMultipleOperations:
    """多次转账操作测试"""
    
    def test_multiple_transfers(self):
        """测试多次转账"""
        account_a = Account("A001", 1000)
        account_b = Account("B001", 500)
        account_c = Account("C001", 200)
        
        transfer(account_a, account_b, 100)
        transfer(account_b, account_c, 150)
        transfer(account_c, account_a, 50)
        
        assert account_a.balance == 950
        assert account_b.balance == 450
        assert account_c.balance == 300
    
    def test_transfer_chain_with_failure(self):
        """测试转账链中出现失败"""
        account_a = Account("A001", 1000)
        account_b = Account("B001", 100)
        account_c = Account("C001", 0)
        
        transfer(account_a, account_b, 200)
        
        # 第二次转账应该失败
        with pytest.raises(InsufficientBalanceError):
            transfer(account_b, account_c, 500)
        
        # 验证状态
        assert account_a.balance == 800
        assert account_b.balance == 300
        assert account_c.balance == 0


# Pytest fixtures
@pytest.fixture
def account_with_balance():
    """创建有余额的账户 fixture"""
    return Account("TEST001", 1000)


@pytest.fixture
def empty_account():
    """创建空账户 fixture"""
    return Account("TEST002", 0)


class TestTransferWithFixtures:
    """使用 fixtures 的转账测试"""
    
    def test_transfer_with_fixtures(self, account_with_balance, empty_account):
        """使用 fixtures 测试转账"""
        transfer(account_with_balance, empty_account, 300)
        
        assert account_with_balance.balance == 700
        assert empty_account.balance == 300


# 参数化测试
@pytest.mark.parametrize("initial_balance,transfer_amount,expected_balance", [
    (1000, 100, 900),
    (500, 250, 250),
    (1000, 1000, 0),
    (100.5, 50.25, 50.25),
])
def test_transfer_parametrized(initial_balance, transfer_amount, expected_balance):
    """参数化测试不同金额的转账"""
    account_a = Account("A001", initial_balance)
    account_b = Account("B001", 0)
    
    transfer(account_a, account_b, transfer_amount)
    
    assert account_a.balance == pytest.approx(expected_balance)
    assert account_b.balance == pytest.approx(transfer_amount)


@pytest.mark.parametrize("amount", [-100, -0.01, 0, -1000])
def test_invalid_amounts_parametrized(amount):
    """参数化测试无效金额"""
    account_a = Account("A001", 1000)
    account_b = Account("B001", 500)
    
    with pytest.raises(InvalidAmountError):
        transfer(account_a, account_b, amount)
