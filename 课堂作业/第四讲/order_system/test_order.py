"""
订单模块单元测试
"""

import pytest
from .order import Order, OrderItem, OrderService, OrderStatus
from .inventory import Inventory, InsufficientStockError
from .payment import PaymentProcessor, PaymentMethod, InsufficientFundsError


class TestOrderItem:
    """订单项测试"""
    
    def test_order_item_creation(self):
        """测试创建订单项"""
        item = OrderItem("P001", 2, 50.0)
        
        assert item.product_id == "P001"
        assert item.quantity == 2
        assert item.price == 50.0
        assert item.total_price == 100.0
    
    def test_order_item_invalid_quantity(self):
        """测试无效数量"""
        with pytest.raises(ValueError):
            OrderItem("P001", 0, 50.0)
        
        with pytest.raises(ValueError):
            OrderItem("P001", -1, 50.0)
    
    def test_order_item_invalid_price(self):
        """测试无效价格"""
        with pytest.raises(ValueError):
            OrderItem("P001", 2, -10.0)
    
    def test_order_item_to_dict(self):
        """测试转换为字典"""
        item = OrderItem("P001", 2, 50.0)
        item_dict = item.to_dict()
        
        assert item_dict["product_id"] == "P001"
        assert item_dict["quantity"] == 2
        assert item_dict["price"] == 50.0
        assert item_dict["total_price"] == 100.0


class TestOrder:
    """订单测试"""
    
    def test_order_creation(self):
        """测试创建订单"""
        order = Order("ORD001", "CUST001")
        
        assert order.order_id == "ORD001"
        assert order.customer_id == "CUST001"
        assert order.status == OrderStatus.CREATED
        assert order.item_count == 0
        assert order.total_amount == 0
    
    def test_add_item(self):
        """测试添加订单项"""
        order = Order("ORD001", "CUST001")
        order.add_item("P001", 2, 50.0)
        
        assert order.item_count == 1
        assert order.total_amount == 100.0
    
    def test_add_multiple_items(self):
        """测试添加多个订单项"""
        order = Order("ORD001", "CUST001")
        order.add_item("P001", 2, 50.0)
        order.add_item("P002", 1, 100.0)
        order.add_item("P003", 3, 30.0)
        
        assert order.item_count == 3
        assert order.total_amount == 290.0
    
    def test_confirm_order(self):
        """测试确认订单"""
        order = Order("ORD001", "CUST001")
        order.add_item("P001", 2, 50.0)
        order.confirm()
        
        assert order.status == OrderStatus.CONFIRMED
    
    def test_confirm_empty_order(self):
        """测试确认空订单"""
        order = Order("ORD001", "CUST001")
        
        with pytest.raises(ValueError):
            order.confirm()
    
    def test_mark_paid(self):
        """测试标记为已支付"""
        order = Order("ORD001", "CUST001")
        order.add_item("P001", 2, 50.0)
        order.confirm()
        order.mark_paid("PAY001")
        
        assert order.status == OrderStatus.PAID
        assert order.payment_id == "PAY001"
    
    def test_ship_order(self):
        """测试发货"""
        order = Order("ORD001", "CUST001")
        order.add_item("P001", 2, 50.0)
        order.confirm()
        order.mark_paid("PAY001")
        order.ship()
        
        assert order.status == OrderStatus.SHIPPED
    
    def test_complete_order(self):
        """测试完成订单"""
        order = Order("ORD001", "CUST001")
        order.add_item("P001", 2, 50.0)
        order.confirm()
        order.mark_paid("PAY001")
        order.ship()
        order.complete()
        
        assert order.status == OrderStatus.COMPLETED
    
    def test_cancel_order(self):
        """测试取消订单"""
        order = Order("ORD001", "CUST001")
        order.add_item("P001", 2, 50.0)
        order.cancel()
        
        assert order.status == OrderStatus.CANCELLED
    
    def test_invalid_state_transitions(self):
        """测试无效的状态转换"""
        order = Order("ORD001", "CUST001")
        order.add_item("P001", 2, 50.0)
        
        # 不能直接支付未确认的订单
        with pytest.raises(ValueError):
            order.mark_paid("PAY001")
        
        # 不能发货未支付的订单
        order.confirm()
        with pytest.raises(ValueError):
            order.ship()


class TestOrderService:
    """订单服务测试"""
    
    def test_create_order(self):
        """测试创建订单"""
        inventory = Inventory()
        payment_processor = PaymentProcessor()
        service = OrderService(inventory, payment_processor)
        
        order = service.create_order("ORD001", "CUST001")
        
        assert order.order_id == "ORD001"
        assert order.customer_id == "CUST001"
    
    def test_create_duplicate_order(self):
        """测试创建重复订单"""
        inventory = Inventory()
        payment_processor = PaymentProcessor()
        service = OrderService(inventory, payment_processor)
        
        service.create_order("ORD001", "CUST001")
        
        with pytest.raises(ValueError):
            service.create_order("ORD001", "CUST002")
    
    def test_get_order(self):
        """测试获取订单"""
        inventory = Inventory()
        payment_processor = PaymentProcessor()
        service = OrderService(inventory, payment_processor)
        
        service.create_order("ORD001", "CUST001")
        order = service.get_order("ORD001")
        
        assert order.order_id == "ORD001"
    
    def test_get_nonexistent_order(self):
        """测试获取不存在的订单"""
        inventory = Inventory()
        payment_processor = PaymentProcessor()
        service = OrderService(inventory, payment_processor)
        
        with pytest.raises(ValueError):
            service.get_order("ORD999")
    
    def test_add_item_to_order(self):
        """测试向订单添加商品"""
        inventory = Inventory()
        payment_processor = PaymentProcessor()
        service = OrderService(inventory, payment_processor)
        
        service.create_order("ORD001", "CUST001")
        service.add_item_to_order("ORD001", "P001", 2, 50.0)
        
        order = service.get_order("ORD001")
        assert order.item_count == 1
        assert order.total_amount == 100.0


class TestOrderServiceWithInventory:
    """订单服务与库存集成测试"""
    
    def test_confirm_order_with_sufficient_stock(self):
        """测试库存充足时确认订单"""
        inventory = Inventory()
        inventory.add_product("P001", 100)
        
        payment_processor = PaymentProcessor()
        service = OrderService(inventory, payment_processor)
        
        service.create_order("ORD001", "CUST001")
        service.add_item_to_order("ORD001", "P001", 2, 50.0)
        
        result = service.confirm_order("ORD001")
        
        assert result is True
        assert inventory.get_stock("P001") == 98  # 库存减少
    
    def test_confirm_order_with_insufficient_stock(self):
        """测试库存不足时确认订单"""
        inventory = Inventory()
        inventory.add_product("P001", 1)
        
        payment_processor = PaymentProcessor()
        service = OrderService(inventory, payment_processor)
        
        service.create_order("ORD001", "CUST001")
        service.add_item_to_order("ORD001", "P001", 2, 50.0)
        
        with pytest.raises(InsufficientStockError):
            service.confirm_order("ORD001")
        
        # 库存不应该改变
        assert inventory.get_stock("P001") == 1
    
    def test_confirm_order_with_multiple_items(self):
        """测试确认包含多个商品的订单"""
        inventory = Inventory()
        inventory.add_product("P001", 100)
        inventory.add_product("P002", 50)
        
        payment_processor = PaymentProcessor()
        service = OrderService(inventory, payment_processor)
        
        service.create_order("ORD001", "CUST001")
        service.add_item_to_order("ORD001", "P001", 2, 50.0)
        service.add_item_to_order("ORD001", "P002", 1, 100.0)
        
        service.confirm_order("ORD001")
        
        assert inventory.get_stock("P001") == 98
        assert inventory.get_stock("P002") == 49


class TestOrderServiceWithPayment:
    """订单服务与支付集成测试"""
    
    def test_process_payment_success(self):
        """测试支付成功"""
        inventory = Inventory()
        inventory.add_product("P001", 100)
        
        payment_processor = PaymentProcessor()
        service = OrderService(inventory, payment_processor)
        
        service.create_order("ORD001", "CUST001")
        service.add_item_to_order("ORD001", "P001", 2, 50.0)
        service.confirm_order("ORD001")
        
        payment_id = service.process_payment("ORD001", PaymentMethod.ALIPAY)
        
        order = service.get_order("ORD001")
        assert order.status == OrderStatus.PAID
        assert order.payment_id == payment_id
    
    def test_process_payment_insufficient_funds(self):
        """测试余额不足"""
        inventory = Inventory()
        inventory.add_product("P001", 100)
        
        payment_processor = PaymentProcessor()
        payment_processor.set_balance(PaymentMethod.ALIPAY, 50.0)
        
        service = OrderService(inventory, payment_processor)
        
        service.create_order("ORD001", "CUST001")
        service.add_item_to_order("ORD001", "P001", 2, 50.0)
        service.confirm_order("ORD001")
        
        with pytest.raises(InsufficientFundsError):
            service.process_payment("ORD001", PaymentMethod.ALIPAY)


class TestOrderServiceCompleteWorkflow:
    """订单服务完整流程测试"""
    
    def test_complete_order_workflow(self):
        """测试完整订单流程"""
        # 准备
        inventory = Inventory()
        inventory.add_product("P001", 100)
        inventory.add_product("P002", 50)
        
        payment_processor = PaymentProcessor()
        service = OrderService(inventory, payment_processor)
        
        # 1. 创建订单
        service.create_order("ORD001", "CUST001")
        service.add_item_to_order("ORD001", "P001", 2, 50.0)
        service.add_item_to_order("ORD001", "P002", 1, 100.0)
        
        order = service.get_order("ORD001")
        assert order.status == OrderStatus.CREATED
        assert order.total_amount == 200.0
        
        # 2. 确认订单（预留库存）
        service.confirm_order("ORD001")
        assert order.status == OrderStatus.CONFIRMED
        assert inventory.get_stock("P001") == 98
        assert inventory.get_stock("P002") == 49
        
        # 3. 支付
        service.process_payment("ORD001", PaymentMethod.ALIPAY)
        assert order.status == OrderStatus.PAID
        
        # 4. 发货
        service.ship_order("ORD001")
        assert order.status == OrderStatus.SHIPPED
        
        # 5. 完成
        service.complete_order("ORD001")
        assert order.status == OrderStatus.COMPLETED
    
    def test_cancel_order_after_confirm(self):
        """测试确认后取消订单"""
        inventory = Inventory()
        inventory.add_product("P001", 100)
        
        payment_processor = PaymentProcessor()
        service = OrderService(inventory, payment_processor)
        
        service.create_order("ORD001", "CUST001")
        service.add_item_to_order("ORD001", "P001", 2, 50.0)
        service.confirm_order("ORD001")
        
        # 库存已预留
        assert inventory.get_stock("P001") == 98
        
        # 取消订单
        service.cancel_order("ORD001")
        
        # 库存应该恢复
        assert inventory.get_stock("P001") == 100
        
        order = service.get_order("ORD001")
        assert order.status == OrderStatus.CANCELLED
    
    def test_cancel_order_after_payment(self):
        """测试支付后取消订单"""
        inventory = Inventory()
        inventory.add_product("P001", 100)
        
        payment_processor = PaymentProcessor()
        initial_balance = payment_processor.get_balance(PaymentMethod.ALIPAY)
        
        service = OrderService(inventory, payment_processor)
        
        service.create_order("ORD001", "CUST001")
        service.add_item_to_order("ORD001", "P001", 2, 50.0)
        service.confirm_order("ORD001")
        service.process_payment("ORD001", PaymentMethod.ALIPAY)
        
        # 余额应该减少
        assert payment_processor.get_balance(PaymentMethod.ALIPAY) == initial_balance - 100.0
        
        # 取消订单
        service.cancel_order("ORD001")
        
        # 库存恢复
        assert inventory.get_stock("P001") == 100
        
        # 余额恢复
        assert payment_processor.get_balance(PaymentMethod.ALIPAY) == initial_balance


# Fixtures
@pytest.fixture
def setup_service():
    """创建配置好的订单服务"""
    inventory = Inventory()
    inventory.add_product("P001", 100)
    inventory.add_product("P002", 50)
    inventory.add_product("P003", 200)
    
    payment_processor = PaymentProcessor()
    service = OrderService(inventory, payment_processor)
    
    return service, inventory, payment_processor


class TestOrderServiceWithFixtures:
    """使用fixtures的测试"""
    
    def test_multiple_orders(self, setup_service):
        """测试多个订单"""
        service, inventory, payment_processor = setup_service
        
        # 创建第一个订单
        service.create_order("ORD001", "CUST001")
        service.add_item_to_order("ORD001", "P001", 2, 50.0)
        service.confirm_order("ORD001")
        service.process_payment("ORD001", PaymentMethod.ALIPAY)
        
        # 创建第二个订单
        service.create_order("ORD002", "CUST002")
        service.add_item_to_order("ORD002", "P002", 1, 100.0)
        service.confirm_order("ORD002")
        service.process_payment("ORD002", PaymentMethod.WECHAT)
        
        # 验证
        assert service.get_order("ORD001").status == OrderStatus.PAID
        assert service.get_order("ORD002").status == OrderStatus.PAID
        assert inventory.get_stock("P001") == 98
        assert inventory.get_stock("P002") == 49


# 参数化测试
@pytest.mark.parametrize("product_id,quantity,price,expected_total", [
    ("P001", 2, 50.0, 100.0),
    ("P002", 1, 100.0, 100.0),
    ("P003", 5, 20.0, 100.0),
])
def test_order_total_calculation(product_id, quantity, price, expected_total):
    """参数化测试订单总额计算"""
    order = Order("ORD001", "CUST001")
    order.add_item(product_id, quantity, price)
    
    assert order.total_amount == expected_total
