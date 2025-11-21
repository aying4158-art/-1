"""
支付管理模块
负责处理支付请求和支付状态管理
"""

from typing import Dict, Optional
from enum import Enum
from datetime import datetime


class PaymentStatus(Enum):
    """支付状态枚举"""
    PENDING = "pending"      # 待支付
    PROCESSING = "processing"  # 处理中
    SUCCESS = "success"      # 支付成功
    FAILED = "failed"        # 支付失败
    REFUNDED = "refunded"    # 已退款


class PaymentMethod(Enum):
    """支付方式枚举"""
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    ALIPAY = "alipay"
    WECHAT = "wechat"
    PAYPAL = "paypal"


class InsufficientFundsError(Exception):
    """余额不足异常"""
    pass


class PaymentNotFoundError(Exception):
    """支付记录不存在异常"""
    pass


class InvalidPaymentStateError(Exception):
    """无效的支付状态异常"""
    pass


class Payment:
    """支付记录类"""
    
    def __init__(self, payment_id: str, order_id: str, amount: float, 
                 method: PaymentMethod):
        """
        初始化支付记录
        
        Args:
            payment_id: 支付ID
            order_id: 订单ID
            amount: 支付金额
            method: 支付方式
        """
        if amount <= 0:
            raise ValueError(f"支付金额必须大于0: {amount}")
        
        self.payment_id = payment_id
        self.order_id = order_id
        self.amount = amount
        self.method = method
        self.status = PaymentStatus.PENDING
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    def process(self) -> None:
        """将支付状态设置为处理中"""
        if self.status != PaymentStatus.PENDING:
            raise InvalidPaymentStateError(
                f"只能处理待支付的订单。当前状态: {self.status.value}"
            )
        self.status = PaymentStatus.PROCESSING
        self.updated_at = datetime.now()
    
    def complete(self) -> None:
        """完成支付"""
        if self.status != PaymentStatus.PROCESSING:
            raise InvalidPaymentStateError(
                f"只能完成处理中的支付。当前状态: {self.status.value}"
            )
        self.status = PaymentStatus.SUCCESS
        self.updated_at = datetime.now()
    
    def fail(self) -> None:
        """支付失败"""
        if self.status not in [PaymentStatus.PENDING, PaymentStatus.PROCESSING]:
            raise InvalidPaymentStateError(
                f"无法将当前状态设置为失败。当前状态: {self.status.value}"
            )
        self.status = PaymentStatus.FAILED
        self.updated_at = datetime.now()
    
    def refund(self) -> None:
        """退款"""
        if self.status != PaymentStatus.SUCCESS:
            raise InvalidPaymentStateError(
                f"只能退款成功的支付。当前状态: {self.status.value}"
            )
        self.status = PaymentStatus.REFUNDED
        self.updated_at = datetime.now()
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "payment_id": self.payment_id,
            "order_id": self.order_id,
            "amount": self.amount,
            "method": self.method.value,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }


class PaymentProcessor:
    """支付处理器"""
    
    def __init__(self):
        """初始化支付处理器"""
        self._payments: Dict[str, Payment] = {}
        # 模拟账户余额
        self._account_balances: Dict[PaymentMethod, float] = {
            PaymentMethod.CREDIT_CARD: 10000.0,
            PaymentMethod.DEBIT_CARD: 5000.0,
            PaymentMethod.ALIPAY: 8000.0,
            PaymentMethod.WECHAT: 6000.0,
            PaymentMethod.PAYPAL: 15000.0,
        }
    
    def create_payment(self, payment_id: str, order_id: str, 
                      amount: float, method: PaymentMethod) -> Payment:
        """
        创建支付记录
        
        Args:
            payment_id: 支付ID
            order_id: 订单ID
            amount: 支付金额
            method: 支付方式
        
        Returns:
            支付记录
        
        Raises:
            ValueError: 支付ID已存在或金额无效
        """
        if payment_id in self._payments:
            raise ValueError(f"支付ID已存在: {payment_id}")
        
        payment = Payment(payment_id, order_id, amount, method)
        self._payments[payment_id] = payment
        return payment
    
    def get_payment(self, payment_id: str) -> Payment:
        """
        获取支付记录
        
        Args:
            payment_id: 支付ID
        
        Returns:
            支付记录
        
        Raises:
            PaymentNotFoundError: 支付记录不存在
        """
        if payment_id not in self._payments:
            raise PaymentNotFoundError(f"支付记录不存在: {payment_id}")
        
        return self._payments[payment_id]
    
    def process_payment(self, payment_id: str) -> bool:
        """
        处理支付
        
        Args:
            payment_id: 支付ID
        
        Returns:
            是否成功
        
        Raises:
            PaymentNotFoundError: 支付记录不存在
            InsufficientFundsError: 余额不足
        """
        payment = self.get_payment(payment_id)
        payment.process()
        
        # 检查余额
        if self._account_balances[payment.method] < payment.amount:
            payment.fail()
            raise InsufficientFundsError(
                f"余额不足。支付方式: {payment.method.value}, "
                f"需要: {payment.amount}, "
                f"可用: {self._account_balances[payment.method]}"
            )
        
        # 扣款
        self._account_balances[payment.method] -= payment.amount
        payment.complete()
        return True
    
    def refund_payment(self, payment_id: str) -> bool:
        """
        退款
        
        Args:
            payment_id: 支付ID
        
        Returns:
            是否成功
        
        Raises:
            PaymentNotFoundError: 支付记录不存在
        """
        payment = self.get_payment(payment_id)
        
        # 退款
        self._account_balances[payment.method] += payment.amount
        payment.refund()
        return True
    
    def get_balance(self, method: PaymentMethod) -> float:
        """
        获取账户余额
        
        Args:
            method: 支付方式
        
        Returns:
            余额
        """
        return self._account_balances[method]
    
    def set_balance(self, method: PaymentMethod, balance: float) -> None:
        """
        设置账户余额（用于测试）
        
        Args:
            method: 支付方式
            balance: 余额
        """
        if balance < 0:
            raise ValueError(f"余额不能为负数: {balance}")
        self._account_balances[method] = balance
    
    def get_all_payments(self) -> Dict[str, Payment]:
        """
        获取所有支付记录
        
        Returns:
            支付记录字典
        """
        return self._payments.copy()
    
    def clear(self) -> None:
        """清空所有支付记录"""
        self._payments.clear()
