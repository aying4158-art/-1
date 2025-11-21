"""
库存管理模块
负责商品库存的增减和查询
"""

from typing import Dict, Optional


class InsufficientStockError(Exception):
    """库存不足异常"""
    pass


class ProductNotFoundError(Exception):
    """商品不存在异常"""
    pass


class Inventory:
    """库存管理类"""
    
    def __init__(self):
        """初始化库存"""
        self._stock: Dict[str, int] = {}
    
    def add_product(self, product_id: str, quantity: int) -> None:
        """
        添加商品库存
        
        Args:
            product_id: 商品ID
            quantity: 数量
        
        Raises:
            ValueError: 数量为负数
        """
        if quantity < 0:
            raise ValueError(f"数量不能为负数: {quantity}")
        
        if product_id in self._stock:
            self._stock[product_id] += quantity
        else:
            self._stock[product_id] = quantity
    
    def remove_product(self, product_id: str) -> None:
        """
        移除商品
        
        Args:
            product_id: 商品ID
        
        Raises:
            ProductNotFoundError: 商品不存在
        """
        if product_id not in self._stock:
            raise ProductNotFoundError(f"商品不存在: {product_id}")
        
        del self._stock[product_id]
    
    def get_stock(self, product_id: str) -> int:
        """
        查询商品库存
        
        Args:
            product_id: 商品ID
        
        Returns:
            库存数量
        
        Raises:
            ProductNotFoundError: 商品不存在
        """
        if product_id not in self._stock:
            raise ProductNotFoundError(f"商品不存在: {product_id}")
        
        return self._stock[product_id]
    
    def check_availability(self, product_id: str, quantity: int) -> bool:
        """
        检查库存是否充足
        
        Args:
            product_id: 商品ID
            quantity: 需要的数量
        
        Returns:
            是否有足够库存
        """
        try:
            current_stock = self.get_stock(product_id)
            return current_stock >= quantity
        except ProductNotFoundError:
            return False
    
    def reserve_stock(self, product_id: str, quantity: int) -> None:
        """
        预留库存（减少库存）
        
        Args:
            product_id: 商品ID
            quantity: 数量
        
        Raises:
            ProductNotFoundError: 商品不存在
            InsufficientStockError: 库存不足
            ValueError: 数量无效
        """
        if quantity <= 0:
            raise ValueError(f"数量必须大于0: {quantity}")
        
        if product_id not in self._stock:
            raise ProductNotFoundError(f"商品不存在: {product_id}")
        
        if self._stock[product_id] < quantity:
            raise InsufficientStockError(
                f"库存不足。商品: {product_id}, "
                f"当前库存: {self._stock[product_id]}, "
                f"需要: {quantity}"
            )
        
        self._stock[product_id] -= quantity
    
    def release_stock(self, product_id: str, quantity: int) -> None:
        """
        释放库存（增加库存，用于取消订单）
        
        Args:
            product_id: 商品ID
            quantity: 数量
        
        Raises:
            ProductNotFoundError: 商品不存在
            ValueError: 数量无效
        """
        if quantity <= 0:
            raise ValueError(f"数量必须大于0: {quantity}")
        
        if product_id not in self._stock:
            raise ProductNotFoundError(f"商品不存在: {product_id}")
        
        self._stock[product_id] += quantity
    
    def get_all_stock(self) -> Dict[str, int]:
        """
        获取所有库存信息
        
        Returns:
            库存字典
        """
        return self._stock.copy()
    
    def clear(self) -> None:
        """清空所有库存"""
        self._stock.clear()
