"""
订单管理模块
整合库存和支付模块，处理订单流程
"""

from typing import Dict, List, Optional
from enum import Enum
from datetime import datetime
from inventory import Inventory, InsufficientStockError, ProductNotFoundError
from payment import PaymentProcessor, PaymentMethod, PaymentStatus


class OrderStatus(Enum):
    """订单状态枚举"""
    CREATED = "created"          # 已创建
    CONFIRMED = "confirmed"      # 已确认
    PAID = "paid"               # 已支付
    SHIPPED = "shipped"         # 已发货
    COMPLETED = "completed"     # 已完成
    CANCELLED = "cancelled"     # 已取消


class OrderItem:
    """订单项"""
    
    def __init__(self, product_id: str, quantity: int, price: float):
        """
        初始化订单项
        
        Args:
            product_id: 商品ID
            quantity: 数量
            price: 单价
        """
        if quantity <= 0:
            raise ValueError(f"数量必须大于0: {quantity}")
        if price < 0:
            raise ValueError(f"价格不能为负数: {price}")
        
        self.product_id = product_id
        self.quantity = quantity
        self.price = price
    
    @property
    def total_price(self) -> float:
        """计算总价"""
        return self.quantity * self.price
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "product_id": self.product_id,
            "quantity": self.quantity,
            "price": self.price,
            "total_price": self.total_price
        }


class Order:
    """订单类"""
    
    def __init__(self, order_id: str, customer_id: str):
        """
        初始化订单
        
        Args:
            order_id: 订单ID
            customer_id: 客户ID
        """
        self.order_id = order_id
        self.customer_id = customer_id
        self.items: List[OrderItem] = []
        self.status = OrderStatus.CREATED
        self.payment_id: Optional[str] = None
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    def add_item(self, product_id: str, quantity: int, price: float) -> None:
        """
        添加订单项
        
        Args:
            product_id: 商品ID
            quantity: 数量
            price: 单价
        """
        item = OrderItem(product_id, quantity, price)
        self.items.append(item)
        self.updated_at = datetime.now()
    
    @property
    def total_amount(self) -> float:
        """计算订单总金额"""
        return sum(item.total_price for item in self.items)
    
    @property
    def item_count(self) -> int:
        """获取订单项数量"""
        return len(self.items)
    
    def confirm(self) -> None:
        """确认订单"""
        if self.status != OrderStatus.CREATED:
            raise ValueError(f"只能确认已创建的订单。当前状态: {self.status.value}")
        if not self.items:
            raise ValueError("订单没有商品")
        
        self.status = OrderStatus.CONFIRMED
        self.updated_at = datetime.now()
    
    def mark_paid(self, payment_id: str) -> None:
        """标记为已支付"""
        if self.status != OrderStatus.CONFIRMED:
            raise ValueError(f"只能支付已确认的订单。当前状态: {self.status.value}")
        
        self.payment_id = payment_id
        self.status = OrderStatus.PAID
        self.updated_at = datetime.now()
    
    def ship(self) -> None:
        """发货"""
        if self.status != OrderStatus.PAID:
            raise ValueError(f"只能发货已支付的订单。当前状态: {self.status.value}")
        
        self.status = OrderStatus.SHIPPED
        self.updated_at = datetime.now()
    
    def complete(self) -> None:
        """完成订单"""
        if self.status != OrderStatus.SHIPPED:
            raise ValueError(f"只能完成已发货的订单。当前状态: {self.status.value}")
        
        self.status = OrderStatus.COMPLETED
        self.updated_at = datetime.now()
    
    def cancel(self) -> None:
        """取消订单"""
        if self.status in [OrderStatus.SHIPPED, OrderStatus.COMPLETED]:
            raise ValueError(f"无法取消该状态的订单。当前状态: {self.status.value}")
        
        self.status = OrderStatus.CANCELLED
        self.updated_at = datetime.now()
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "order_id": self.order_id,
            "customer_id": self.customer_id,
            "items": [item.to_dict() for item in self.items],
            "total_amount": self.total_amount,
            "status": self.status.value,
            "payment_id": self.payment_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }


class OrderService:
    """订单服务"""
    
    def __init__(self, inventory: Inventory, payment_processor: PaymentProcessor):
        """
        初始化订单服务
        
        Args:
            inventory: 库存管理器
            payment_processor: 支付处理器
        """
        self.inventory = inventory
        self.payment_processor = payment_processor
        self._orders: Dict[str, Order] = {}
    
    def create_order(self, order_id: str, customer_id: str) -> Order:
        """
        创建订单
        
        Args:
            order_id: 订单ID
            customer_id: 客户ID
        
        Returns:
            订单对象
        
        Raises:
            ValueError: 订单ID已存在
        """
        if order_id in self._orders:
            raise ValueError(f"订单ID已存在: {order_id}")
        
        order = Order(order_id, customer_id)
        self._orders[order_id] = order
        return order
    
    def get_order(self, order_id: str) -> Order:
        """
        获取订单
        
        Args:
            order_id: 订单ID
        
        Returns:
            订单对象
        
        Raises:
            ValueError: 订单不存在
        """
        if order_id not in self._orders:
            raise ValueError(f"订单不存在: {order_id}")
        
        return self._orders[order_id]
    
    def add_item_to_order(self, order_id: str, product_id: str, 
                         quantity: int, price: float) -> None:
        """
        向订单添加商品
        
        Args:
            order_id: 订单ID
            product_id: 商品ID
            quantity: 数量
            price: 单价
        """
        order = self.get_order(order_id)
        order.add_item(product_id, quantity, price)
    
    def confirm_order(self, order_id: str) -> bool:
        """
        确认订单（检查库存并预留）
        
        Args:
            order_id: 订单ID
        
        Returns:
            是否成功
        
        Raises:
            InsufficientStockError: 库存不足
            ProductNotFoundError: 商品不存在
        """
        order = self.get_order(order_id)
        
        # 检查所有商品库存
        for item in order.items:
            if not self.inventory.check_availability(item.product_id, item.quantity):
                raise InsufficientStockError(
                    f"商品 {item.product_id} 库存不足。需要: {item.quantity}"
                )
        
        # 预留库存
        for item in order.items:
            self.inventory.reserve_stock(item.product_id, item.quantity)
        
        order.confirm()
        return True
    
    def process_payment(self, order_id: str, payment_method: PaymentMethod) -> str:
        """
        处理订单支付
        
        Args:
            order_id: 订单ID
            payment_method: 支付方式
        
        Returns:
            支付ID
        
        Raises:
            ValueError: 订单状态错误
        """
        order = self.get_order(order_id)
        
        # 创建支付
        payment_id = f"PAY_{order_id}"
        payment = self.payment_processor.create_payment(
            payment_id, order_id, order.total_amount, payment_method
        )
        
        # 处理支付
        self.payment_processor.process_payment(payment_id)
        
        # 标记订单为已支付
        order.mark_paid(payment_id)
        
        return payment_id
    
    def ship_order(self, order_id: str) -> bool:
        """
        发货
        
        Args:
            order_id: 订单ID
        
        Returns:
            是否成功
        """
        order = self.get_order(order_id)
        order.ship()
        return True
    
    def complete_order(self, order_id: str) -> bool:
        """
        完成订单
        
        Args:
            order_id: 订单ID
        
        Returns:
            是否成功
        """
        order = self.get_order(order_id)
        order.complete()
        return True
    
    def cancel_order(self, order_id: str) -> bool:
        """
        取消订单（释放库存，退款）
        
        Args:
            order_id: 订单ID
        
        Returns:
            是否成功
        """
        order = self.get_order(order_id)
        
        # 如果已确认，释放库存
        if order.status in [OrderStatus.CONFIRMED, OrderStatus.PAID]:
            for item in order.items:
                self.inventory.release_stock(item.product_id, item.quantity)
        
        # 如果已支付，退款
        if order.payment_id and order.status == OrderStatus.PAID:
            self.payment_processor.refund_payment(order.payment_id)
        
        order.cancel()
        return True
    
    def get_all_orders(self) -> Dict[str, Order]:
        """获取所有订单"""
        return self._orders.copy()
    
    def clear(self) -> None:
        """清空所有订单"""
        self._orders.clear()
