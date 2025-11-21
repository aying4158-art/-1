"""
集成测试
使用 requests 库模拟 API 调用
"""

import pytest
import requests
import time
from multiprocessing import Process
import uvicorn


# API 基础 URL
BASE_URL = "http://localhost:8000"


def start_server():
    """启动 FastAPI 服务器"""
    from .api import app
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="error")


@pytest.fixture(scope="module", autouse=True)
def setup_server():
    """启动测试服务器"""
    # 启动服务器进程
    server_process = Process(target=start_server)
    server_process.start()
    
    # 等待服务器启动
    time.sleep(2)
    
    # 初始化测试数据
    try:
        requests.post(f"{BASE_URL}/api/test/init-data")
    except:
        pass
    
    yield
    
    # 清理
    server_process.terminate()
    server_process.join()


@pytest.fixture(autouse=True)
def reset_data():
    """每个测试前重置数据"""
    try:
        requests.post(f"{BASE_URL}/api/test/init-data")
    except:
        pass
    yield


class TestHealthCheck:
    """健康检查测试"""
    
    def test_root_endpoint(self):
        """测试根路径"""
        response = requests.get(f"{BASE_URL}/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
    
    def test_health_check(self):
        """测试健康检查"""
        response = requests.get(f"{BASE_URL}/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


class TestInventoryAPI:
    """库存 API 测试"""
    
    def test_add_product(self):
        """测试添加商品"""
        response = requests.post(
            f"{BASE_URL}/api/inventory/products",
            json={"product_id": "P999", "quantity": 50}
        )
        assert response.status_code == 201
        data = response.json()
        assert data["product_id"] == "P999"
        assert data["quantity"] == 50
    
    def test_get_product_stock(self):
        """测试查询商品库存"""
        response = requests.get(f"{BASE_URL}/api/inventory/products/P001")
        assert response.status_code == 200
        data = response.json()
        assert data["product_id"] == "P001"
        assert data["stock"] == 100
    
    def test_get_nonexistent_product(self):
        """测试查询不存在的商品"""
        response = requests.get(f"{BASE_URL}/api/inventory/products/P999")
        assert response.status_code == 404
    
    def test_get_all_stock(self):
        """测试获取所有库存"""
        response = requests.get(f"{BASE_URL}/api/inventory/products")
        assert response.status_code == 200
        data = response.json()
        assert "products" in data
        assert "P001" in data["products"]
    
    def test_remove_product(self):
        """测试移除商品"""
        # 先添加
        requests.post(
            f"{BASE_URL}/api/inventory/products",
            json={"product_id": "P888", "quantity": 10}
        )
        
        # 再移除
        response = requests.delete(f"{BASE_URL}/api/inventory/products/P888")
        assert response.status_code == 200
        
        # 验证已删除
        response = requests.get(f"{BASE_URL}/api/inventory/products/P888")
        assert response.status_code == 404


class TestOrderAPI:
    """订单 API 测试"""
    
    def test_create_order(self):
        """测试创建订单"""
        response = requests.post(
            f"{BASE_URL}/api/orders",
            json={"order_id": "ORD001", "customer_id": "CUST001"}
        )
        assert response.status_code == 201
        data = response.json()
        assert data["order_id"] == "ORD001"
        assert data["status"] == "created"
    
    def test_add_order_item(self):
        """测试添加订单项"""
        # 创建订单
        requests.post(
            f"{BASE_URL}/api/orders",
            json={"order_id": "ORD002", "customer_id": "CUST001"}
        )
        
        # 添加商品
        response = requests.post(
            f"{BASE_URL}/api/orders/ORD002/items",
            json={"product_id": "P001", "quantity": 2, "price": 50.0}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["item_count"] == 1
        assert data["total_amount"] == 100.0
    
    def test_get_order(self):
        """测试获取订单"""
        # 创建订单
        requests.post(
            f"{BASE_URL}/api/orders",
            json={"order_id": "ORD003", "customer_id": "CUST001"}
        )
        
        # 获取订单
        response = requests.get(f"{BASE_URL}/api/orders/ORD003")
        assert response.status_code == 200
        data = response.json()
        assert data["order_id"] == "ORD003"
        assert data["customer_id"] == "CUST001"
    
    def test_get_all_orders(self):
        """测试获取所有订单"""
        response = requests.get(f"{BASE_URL}/api/orders")
        assert response.status_code == 200
        data = response.json()
        assert "orders" in data
    
    def test_confirm_order(self):
        """测试确认订单"""
        # 创建订单并添加商品
        requests.post(
            f"{BASE_URL}/api/orders",
            json={"order_id": "ORD004", "customer_id": "CUST001"}
        )
        requests.post(
            f"{BASE_URL}/api/orders/ORD004/items",
            json={"product_id": "P001", "quantity": 2, "price": 50.0}
        )
        
        # 确认订单
        response = requests.post(f"{BASE_URL}/api/orders/ORD004/confirm")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "confirmed"
        
        # 验证库存减少
        stock_response = requests.get(f"{BASE_URL}/api/inventory/products/P001")
        stock_data = stock_response.json()
        assert stock_data["stock"] == 98


class TestCompleteOrderWorkflow:
    """完整订单流程测试"""
    
    def test_complete_order_flow(self):
        """测试完整订单流程"""
        order_id = "ORD_FLOW_001"
        
        # 1. 创建订单
        response = requests.post(
            f"{BASE_URL}/api/orders",
            json={"order_id": order_id, "customer_id": "CUST001"}
        )
        assert response.status_code == 201
        
        # 2. 添加商品
        response = requests.post(
            f"{BASE_URL}/api/orders/{order_id}/items",
            json={"product_id": "P001", "quantity": 2, "price": 50.0}
        )
        assert response.status_code == 200
        
        response = requests.post(
            f"{BASE_URL}/api/orders/{order_id}/items",
            json={"product_id": "P002", "quantity": 1, "price": 100.0}
        )
        assert response.status_code == 200
        
        # 3. 确认订单
        response = requests.post(f"{BASE_URL}/api/orders/{order_id}/confirm")
        assert response.status_code == 200
        assert response.json()["status"] == "confirmed"
        
        # 4. 支付
        response = requests.post(
            f"{BASE_URL}/api/orders/{order_id}/payment",
            json={"payment_method": "alipay"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "paid"
        assert "payment_id" in data
        assert data["amount"] == 200.0
        
        # 5. 发货
        response = requests.post(f"{BASE_URL}/api/orders/{order_id}/ship")
        assert response.status_code == 200
        assert response.json()["status"] == "shipped"
        
        # 6. 完成
        response = requests.post(f"{BASE_URL}/api/orders/{order_id}/complete")
        assert response.status_code == 200
        assert response.json()["status"] == "completed"
        
        # 7. 验证最终状态
        response = requests.get(f"{BASE_URL}/api/orders/{order_id}")
        assert response.status_code == 200
        order_data = response.json()
        assert order_data["status"] == "completed"
        assert order_data["total_amount"] == 200.0
    
    def test_order_cancellation_flow(self):
        """测试订单取消流程"""
        order_id = "ORD_CANCEL_001"
        
        # 创建并确认订单
        requests.post(
            f"{BASE_URL}/api/orders",
            json={"order_id": order_id, "customer_id": "CUST001"}
        )
        requests.post(
            f"{BASE_URL}/api/orders/{order_id}/items",
            json={"product_id": "P001", "quantity": 5, "price": 50.0}
        )
        requests.post(f"{BASE_URL}/api/orders/{order_id}/confirm")
        
        # 检查库存减少
        stock_response = requests.get(f"{BASE_URL}/api/inventory/products/P001")
        stock_before = stock_response.json()["stock"]
        
        # 取消订单
        response = requests.post(f"{BASE_URL}/api/orders/{order_id}/cancel")
        assert response.status_code == 200
        assert response.json()["status"] == "cancelled"
        
        # 验证库存恢复
        stock_response = requests.get(f"{BASE_URL}/api/inventory/products/P001")
        stock_after = stock_response.json()["stock"]
        assert stock_after == stock_before + 5
    
    def test_insufficient_stock_flow(self):
        """测试库存不足流程"""
        order_id = "ORD_NO_STOCK"
        
        # 创建订单
        requests.post(
            f"{BASE_URL}/api/orders",
            json={"order_id": order_id, "customer_id": "CUST001"}
        )
        
        # 添加超过库存的商品
        requests.post(
            f"{BASE_URL}/api/orders/{order_id}/items",
            json={"product_id": "P001", "quantity": 1000, "price": 50.0}
        )
        
        # 尝试确认订单（应该失败）
        response = requests.post(f"{BASE_URL}/api/orders/{order_id}/confirm")
        assert response.status_code == 400
        assert "库存不足" in response.json()["detail"]
    
    def test_payment_with_different_methods(self):
        """测试不同支付方式"""
        payment_methods = ["alipay", "wechat", "credit_card"]
        
        for i, method in enumerate(payment_methods):
            order_id = f"ORD_PAY_{i}"
            
            # 创建订单
            requests.post(
                f"{BASE_URL}/api/orders",
                json={"order_id": order_id, "customer_id": "CUST001"}
            )
            requests.post(
                f"{BASE_URL}/api/orders/{order_id}/items",
                json={"product_id": "P001", "quantity": 1, "price": 50.0}
            )
            requests.post(f"{BASE_URL}/api/orders/{order_id}/confirm")
            
            # 使用不同支付方式
            response = requests.post(
                f"{BASE_URL}/api/orders/{order_id}/payment",
                json={"payment_method": method}
            )
            assert response.status_code == 200
            assert response.json()["status"] == "paid"


class TestPaymentAPI:
    """支付 API 测试"""
    
    def test_get_payment_balance(self):
        """测试获取支付余额"""
        response = requests.get(f"{BASE_URL}/api/payments/balance/alipay")
        assert response.status_code == 200
        data = response.json()
        assert "balance" in data
        assert data["payment_method"] == "alipay"


class TestErrorHandling:
    """错误处理测试"""
    
    def test_duplicate_order_id(self):
        """测试重复订单ID"""
        requests.post(
            f"{BASE_URL}/api/orders",
            json={"order_id": "ORD_DUP", "customer_id": "CUST001"}
        )
        
        response = requests.post(
            f"{BASE_URL}/api/orders",
            json={"order_id": "ORD_DUP", "customer_id": "CUST002"}
        )
        assert response.status_code == 400
    
    def test_invalid_payment_method(self):
        """测试无效支付方式"""
        order_id = "ORD_INVALID_PAY"
        
        requests.post(
            f"{BASE_URL}/api/orders",
            json={"order_id": order_id, "customer_id": "CUST001"}
        )
        requests.post(
            f"{BASE_URL}/api/orders/{order_id}/items",
            json={"product_id": "P001", "quantity": 1, "price": 50.0}
        )
        requests.post(f"{BASE_URL}/api/orders/{order_id}/confirm")
        
        response = requests.post(
            f"{BASE_URL}/api/orders/{order_id}/payment",
            json={"payment_method": "invalid_method"}
        )
        assert response.status_code == 400


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
