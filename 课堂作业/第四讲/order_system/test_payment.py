"""
支付模块单元测试
"""

import pytest
from datetime import datetime
from .payment import (
    Payment, PaymentProcessor, PaymentStatus, PaymentMethod,
    InsufficientFundsError, PaymentNotFoundError, InvalidPaymentStateError
)


class TestPayment:
    """支付记录测试"""
    
    def test_payment_creation(self):
        """测试创建支付记录"""
        payment = Payment("PAY001", "ORD001", 100.0, PaymentMethod.ALIPAY)
        
        assert payment.payment_id == "PAY001"
        assert payment.order_id == "ORD001"
        assert payment.amount == 100.0
        assert payment.method == PaymentMethod.ALIPAY
        assert payment.status == PaymentStatus.PENDING
    
    def test_payment_invalid_amount(self):
        """测试无效金额"""
        with pytest.raises(ValueError):
            Payment("PAY001", "ORD001", 0, PaymentMethod.ALIPAY)
        
        with pytest.raises(ValueError):
            Payment("PAY001", "ORD001", -100, PaymentMethod.ALIPAY)
    
    def test_payment_process(self):
        """测试处理支付"""
        payment = Payment("PAY001", "ORD001", 100.0, PaymentMethod.ALIPAY)
        payment.process()
        
        assert payment.status == PaymentStatus.PROCESSING
    
    def test_payment_complete(self):
        """测试完成支付"""
        payment = Payment("PAY001", "ORD001", 100.0, PaymentMethod.ALIPAY)
        payment.process()
        payment.complete()
        
        assert payment.status == PaymentStatus.SUCCESS
    
    def test_payment_fail(self):
        """测试支付失败"""
        payment = Payment("PAY001", "ORD001", 100.0, PaymentMethod.ALIPAY)
        payment.process()
        payment.fail()
        
        assert payment.status == PaymentStatus.FAILED
    
    def test_payment_refund(self):
        """测试退款"""
        payment = Payment("PAY001", "ORD001", 100.0, PaymentMethod.ALIPAY)
        payment.process()
        payment.complete()
        payment.refund()
        
        assert payment.status == PaymentStatus.REFUNDED
    
    def test_payment_invalid_state_transitions(self):
        """测试无效的状态转换"""
        payment = Payment("PAY001", "ORD001", 100.0, PaymentMethod.ALIPAY)
        
        # 不能直接完成待支付的订单
        with pytest.raises(InvalidPaymentStateError):
            payment.complete()
        
        # 不能退款未成功的支付
        with pytest.raises(InvalidPaymentStateError):
            payment.refund()
    
    def test_payment_to_dict(self):
        """测试转换为字典"""
        payment = Payment("PAY001", "ORD001", 100.0, PaymentMethod.ALIPAY)
        payment_dict = payment.to_dict()
        
        assert payment_dict["payment_id"] == "PAY001"
        assert payment_dict["order_id"] == "ORD001"
        assert payment_dict["amount"] == 100.0
        assert payment_dict["method"] == "alipay"
        assert payment_dict["status"] == "pending"


class TestPaymentProcessor:
    """支付处理器测试"""
    
    def test_create_payment(self):
        """测试创建支付"""
        processor = PaymentProcessor()
        payment = processor.create_payment(
            "PAY001", "ORD001", 100.0, PaymentMethod.ALIPAY
        )
        
        assert payment.payment_id == "PAY001"
        assert payment.status == PaymentStatus.PENDING
    
    def test_create_duplicate_payment(self):
        """测试创建重复支付"""
        processor = PaymentProcessor()
        processor.create_payment("PAY001", "ORD001", 100.0, PaymentMethod.ALIPAY)
        
        with pytest.raises(ValueError):
            processor.create_payment("PAY001", "ORD002", 200.0, PaymentMethod.ALIPAY)
    
    def test_get_payment(self):
        """测试获取支付记录"""
        processor = PaymentProcessor()
        processor.create_payment("PAY001", "ORD001", 100.0, PaymentMethod.ALIPAY)
        
        payment = processor.get_payment("PAY001")
        assert payment.payment_id == "PAY001"
    
    def test_get_nonexistent_payment(self):
        """测试获取不存在的支付"""
        processor = PaymentProcessor()
        
        with pytest.raises(PaymentNotFoundError):
            processor.get_payment("PAY999")
    
    def test_process_payment_success(self):
        """测试处理支付成功"""
        processor = PaymentProcessor()
        processor.create_payment("PAY001", "ORD001", 100.0, PaymentMethod.ALIPAY)
        
        result = processor.process_payment("PAY001")
        
        assert result is True
        payment = processor.get_payment("PAY001")
        assert payment.status == PaymentStatus.SUCCESS
    
    def test_process_payment_insufficient_funds(self):
        """测试余额不足"""
        processor = PaymentProcessor()
        processor.set_balance(PaymentMethod.ALIPAY, 50.0)
        processor.create_payment("PAY001", "ORD001", 100.0, PaymentMethod.ALIPAY)
        
        with pytest.raises(InsufficientFundsError):
            processor.process_payment("PAY001")
        
        payment = processor.get_payment("PAY001")
        assert payment.status == PaymentStatus.FAILED
    
    def test_refund_payment(self):
        """测试退款"""
        processor = PaymentProcessor()
        initial_balance = processor.get_balance(PaymentMethod.ALIPAY)
        
        processor.create_payment("PAY001", "ORD001", 100.0, PaymentMethod.ALIPAY)
        processor.process_payment("PAY001")
        
        # 余额应该减少
        assert processor.get_balance(PaymentMethod.ALIPAY) == initial_balance - 100.0
        
        # 退款
        processor.refund_payment("PAY001")
        
        # 余额应该恢复
        assert processor.get_balance(PaymentMethod.ALIPAY) == initial_balance
        
        payment = processor.get_payment("PAY001")
        assert payment.status == PaymentStatus.REFUNDED
    
    def test_get_balance(self):
        """测试获取余额"""
        processor = PaymentProcessor()
        balance = processor.get_balance(PaymentMethod.ALIPAY)
        
        assert balance > 0
    
    def test_set_balance(self):
        """测试设置余额"""
        processor = PaymentProcessor()
        processor.set_balance(PaymentMethod.ALIPAY, 5000.0)
        
        assert processor.get_balance(PaymentMethod.ALIPAY) == 5000.0
    
    def test_set_negative_balance(self):
        """测试设置负数余额"""
        processor = PaymentProcessor()
        
        with pytest.raises(ValueError):
            processor.set_balance(PaymentMethod.ALIPAY, -100.0)


class TestPaymentMethods:
    """支付方式测试"""
    
    @pytest.mark.parametrize("method", [
        PaymentMethod.CREDIT_CARD,
        PaymentMethod.DEBIT_CARD,
        PaymentMethod.ALIPAY,
        PaymentMethod.WECHAT,
        PaymentMethod.PAYPAL,
    ])
    def test_different_payment_methods(self, method):
        """测试不同支付方式"""
        processor = PaymentProcessor()
        payment = processor.create_payment("PAY001", "ORD001", 100.0, method)
        
        result = processor.process_payment("PAY001")
        
        assert result is True
        assert payment.status == PaymentStatus.SUCCESS


class TestPaymentWorkflow:
    """支付流程测试"""
    
    def test_complete_payment_workflow(self):
        """测试完整支付流程"""
        processor = PaymentProcessor()
        
        # 1. 创建支付
        payment = processor.create_payment(
            "PAY001", "ORD001", 100.0, PaymentMethod.ALIPAY
        )
        assert payment.status == PaymentStatus.PENDING
        
        # 2. 处理支付
        processor.process_payment("PAY001")
        assert payment.status == PaymentStatus.SUCCESS
        
        # 3. 退款
        processor.refund_payment("PAY001")
        assert payment.status == PaymentStatus.REFUNDED
    
    def test_failed_payment_workflow(self):
        """测试失败的支付流程"""
        processor = PaymentProcessor()
        processor.set_balance(PaymentMethod.ALIPAY, 50.0)
        
        # 1. 创建支付
        payment = processor.create_payment(
            "PAY001", "ORD001", 100.0, PaymentMethod.ALIPAY
        )
        
        # 2. 尝试处理支付（应该失败）
        with pytest.raises(InsufficientFundsError):
            processor.process_payment("PAY001")
        
        assert payment.status == PaymentStatus.FAILED
    
    def test_multiple_payments(self):
        """测试多个支付"""
        processor = PaymentProcessor()
        
        # 创建多个支付
        processor.create_payment("PAY001", "ORD001", 100.0, PaymentMethod.ALIPAY)
        processor.create_payment("PAY002", "ORD002", 200.0, PaymentMethod.WECHAT)
        processor.create_payment("PAY003", "ORD003", 150.0, PaymentMethod.PAYPAL)
        
        # 处理所有支付
        processor.process_payment("PAY001")
        processor.process_payment("PAY002")
        processor.process_payment("PAY003")
        
        # 验证状态
        assert processor.get_payment("PAY001").status == PaymentStatus.SUCCESS
        assert processor.get_payment("PAY002").status == PaymentStatus.SUCCESS
        assert processor.get_payment("PAY003").status == PaymentStatus.SUCCESS


# Fixtures
@pytest.fixture
def processor_with_payments():
    """创建包含支付记录的处理器"""
    processor = PaymentProcessor()
    processor.create_payment("PAY001", "ORD001", 100.0, PaymentMethod.ALIPAY)
    processor.create_payment("PAY002", "ORD002", 200.0, PaymentMethod.WECHAT)
    return processor


class TestPaymentWithFixtures:
    """使用fixtures的测试"""
    
    def test_get_all_payments(self, processor_with_payments):
        """测试获取所有支付"""
        all_payments = processor_with_payments.get_all_payments()
        
        assert len(all_payments) == 2
        assert "PAY001" in all_payments
        assert "PAY002" in all_payments
    
    def test_clear_payments(self, processor_with_payments):
        """测试清空支付记录"""
        processor_with_payments.clear()
        
        assert len(processor_with_payments.get_all_payments()) == 0


# 参数化测试
@pytest.mark.parametrize("amount,expected_success", [
    (100.0, True),
    (5000.0, True),
    (10000.0, False),  # 超过余额
])
def test_payment_with_different_amounts(amount, expected_success):
    """参数化测试不同金额"""
    processor = PaymentProcessor()
    processor.set_balance(PaymentMethod.ALIPAY, 8000.0)
    processor.create_payment("PAY001", "ORD001", amount, PaymentMethod.ALIPAY)
    
    if expected_success:
        result = processor.process_payment("PAY001")
        assert result is True
    else:
        with pytest.raises(InsufficientFundsError):
            processor.process_payment("PAY001")
