"""
库存模块单元测试
"""

import pytest
from .inventory import Inventory, InsufficientStockError, ProductNotFoundError


class TestInventoryBasic:
    """库存基本功能测试"""
    
    def test_add_product(self):
        """测试添加商品"""
        inventory = Inventory()
        inventory.add_product("P001", 100)
        assert inventory.get_stock("P001") == 100
    
    def test_add_product_multiple_times(self):
        """测试多次添加同一商品"""
        inventory = Inventory()
        inventory.add_product("P001", 100)
        inventory.add_product("P001", 50)
        assert inventory.get_stock("P001") == 150
    
    def test_add_product_negative_quantity(self):
        """测试添加负数数量"""
        inventory = Inventory()
        with pytest.raises(ValueError):
            inventory.add_product("P001", -10)
    
    def test_add_product_zero_quantity(self):
        """测试添加零数量"""
        inventory = Inventory()
        inventory.add_product("P001", 0)
        assert inventory.get_stock("P001") == 0
    
    def test_remove_product(self):
        """测试移除商品"""
        inventory = Inventory()
        inventory.add_product("P001", 100)
        inventory.remove_product("P001")
        
        with pytest.raises(ProductNotFoundError):
            inventory.get_stock("P001")
    
    def test_remove_nonexistent_product(self):
        """测试移除不存在的商品"""
        inventory = Inventory()
        with pytest.raises(ProductNotFoundError):
            inventory.remove_product("P999")
    
    def test_get_stock(self):
        """测试查询库存"""
        inventory = Inventory()
        inventory.add_product("P001", 100)
        assert inventory.get_stock("P001") == 100
    
    def test_get_stock_nonexistent(self):
        """测试查询不存在的商品"""
        inventory = Inventory()
        with pytest.raises(ProductNotFoundError):
            inventory.get_stock("P999")


class TestInventoryAvailability:
    """库存可用性检查测试"""
    
    def test_check_availability_sufficient(self):
        """测试库存充足"""
        inventory = Inventory()
        inventory.add_product("P001", 100)
        assert inventory.check_availability("P001", 50) is True
    
    def test_check_availability_exact(self):
        """测试库存刚好够"""
        inventory = Inventory()
        inventory.add_product("P001", 100)
        assert inventory.check_availability("P001", 100) is True
    
    def test_check_availability_insufficient(self):
        """测试库存不足"""
        inventory = Inventory()
        inventory.add_product("P001", 100)
        assert inventory.check_availability("P001", 150) is False
    
    def test_check_availability_nonexistent(self):
        """测试不存在的商品"""
        inventory = Inventory()
        assert inventory.check_availability("P999", 10) is False


class TestInventoryReserve:
    """库存预留测试"""
    
    def test_reserve_stock_success(self):
        """测试预留库存成功"""
        inventory = Inventory()
        inventory.add_product("P001", 100)
        inventory.reserve_stock("P001", 30)
        assert inventory.get_stock("P001") == 70
    
    def test_reserve_stock_exact_amount(self):
        """测试预留全部库存"""
        inventory = Inventory()
        inventory.add_product("P001", 100)
        inventory.reserve_stock("P001", 100)
        assert inventory.get_stock("P001") == 0
    
    def test_reserve_stock_insufficient(self):
        """测试库存不足"""
        inventory = Inventory()
        inventory.add_product("P001", 100)
        
        with pytest.raises(InsufficientStockError) as exc_info:
            inventory.reserve_stock("P001", 150)
        
        assert "库存不足" in str(exc_info.value)
        assert inventory.get_stock("P001") == 100  # 库存未改变
    
    def test_reserve_stock_nonexistent(self):
        """测试预留不存在的商品"""
        inventory = Inventory()
        with pytest.raises(ProductNotFoundError):
            inventory.reserve_stock("P999", 10)
    
    def test_reserve_stock_zero_quantity(self):
        """测试预留零数量"""
        inventory = Inventory()
        inventory.add_product("P001", 100)
        
        with pytest.raises(ValueError):
            inventory.reserve_stock("P001", 0)
    
    def test_reserve_stock_negative_quantity(self):
        """测试预留负数数量"""
        inventory = Inventory()
        inventory.add_product("P001", 100)
        
        with pytest.raises(ValueError):
            inventory.reserve_stock("P001", -10)


class TestInventoryRelease:
    """库存释放测试"""
    
    def test_release_stock_success(self):
        """测试释放库存成功"""
        inventory = Inventory()
        inventory.add_product("P001", 100)
        inventory.reserve_stock("P001", 30)
        inventory.release_stock("P001", 30)
        assert inventory.get_stock("P001") == 100
    
    def test_release_stock_nonexistent(self):
        """测试释放不存在的商品"""
        inventory = Inventory()
        with pytest.raises(ProductNotFoundError):
            inventory.release_stock("P999", 10)
    
    def test_release_stock_zero_quantity(self):
        """测试释放零数量"""
        inventory = Inventory()
        inventory.add_product("P001", 100)
        
        with pytest.raises(ValueError):
            inventory.release_stock("P001", 0)
    
    def test_release_stock_negative_quantity(self):
        """测试释放负数数量"""
        inventory = Inventory()
        inventory.add_product("P001", 100)
        
        with pytest.raises(ValueError):
            inventory.release_stock("P001", -10)


class TestInventoryMultipleProducts:
    """多商品测试"""
    
    def test_multiple_products(self):
        """测试多个商品"""
        inventory = Inventory()
        inventory.add_product("P001", 100)
        inventory.add_product("P002", 200)
        inventory.add_product("P003", 300)
        
        assert inventory.get_stock("P001") == 100
        assert inventory.get_stock("P002") == 200
        assert inventory.get_stock("P003") == 300
    
    def test_get_all_stock(self):
        """测试获取所有库存"""
        inventory = Inventory()
        inventory.add_product("P001", 100)
        inventory.add_product("P002", 200)
        
        all_stock = inventory.get_all_stock()
        assert all_stock == {"P001": 100, "P002": 200}
    
    def test_get_all_stock_returns_copy(self):
        """测试获取所有库存返回副本"""
        inventory = Inventory()
        inventory.add_product("P001", 100)
        
        all_stock = inventory.get_all_stock()
        all_stock["P001"] = 999
        
        # 原始库存不应该被修改
        assert inventory.get_stock("P001") == 100
    
    def test_clear(self):
        """测试清空库存"""
        inventory = Inventory()
        inventory.add_product("P001", 100)
        inventory.add_product("P002", 200)
        
        inventory.clear()
        
        assert inventory.get_all_stock() == {}


# Fixtures
@pytest.fixture
def inventory_with_products():
    """创建包含商品的库存"""
    inv = Inventory()
    inv.add_product("P001", 100)
    inv.add_product("P002", 200)
    inv.add_product("P003", 50)
    return inv


class TestInventoryWithFixtures:
    """使用fixtures的测试"""
    
    def test_reserve_multiple_products(self, inventory_with_products):
        """测试预留多个商品"""
        inventory_with_products.reserve_stock("P001", 20)
        inventory_with_products.reserve_stock("P002", 50)
        
        assert inventory_with_products.get_stock("P001") == 80
        assert inventory_with_products.get_stock("P002") == 150
    
    def test_complex_operations(self, inventory_with_products):
        """测试复杂操作"""
        # 预留
        inventory_with_products.reserve_stock("P001", 30)
        assert inventory_with_products.get_stock("P001") == 70
        
        # 释放
        inventory_with_products.release_stock("P001", 10)
        assert inventory_with_products.get_stock("P001") == 80
        
        # 再次预留
        inventory_with_products.reserve_stock("P001", 50)
        assert inventory_with_products.get_stock("P001") == 30


# 参数化测试
@pytest.mark.parametrize("initial_stock,reserve_amount,expected_stock", [
    (100, 20, 80),
    (100, 100, 0),
    (200, 50, 150),
    (50, 1, 49),
])
def test_reserve_stock_parametrized(initial_stock, reserve_amount, expected_stock):
    """参数化测试库存预留"""
    inventory = Inventory()
    inventory.add_product("P001", initial_stock)
    inventory.reserve_stock("P001", reserve_amount)
    assert inventory.get_stock("P001") == expected_stock
