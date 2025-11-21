"""
Locust 性能测试脚本
模拟多用户并发访问订单系统 API
"""

from locust import HttpUser, task, between
import random
import json
import time

class OrderSystemUser(HttpUser):
    """订单系统用户行为模拟"""
    
    # 用户请求间隔时间（秒）
    wait_time = between(1, 3)
    
    def on_start(self):
        """用户开始时的初始化操作"""
        self.user_id = random.randint(1000, 9999)
        self.order_counter = 0
        
        # 初始化一些测试数据
        self.setup_test_data()
    
    def setup_test_data(self):
        """设置测试数据"""
        # 添加一些商品库存
        products = [
            {"product_id": f"P{i:03d}", "quantity": 1000} 
            for i in range(1, 11)
        ]
        
        for product in products:
            try:
                self.client.post("/api/inventory/products", json=product)
            except:
                pass  # 忽略重复添加的错误
    
    @task(5)
    def create_order(self):
        """创建订单 - 高频任务"""
        self.order_counter += 1
        order_id = f"ORD_{self.user_id}_{self.order_counter}_{int(time.time())}"
        
        order_data = {
            "order_id": order_id,
            "customer_id": f"CUST_{self.user_id}"
        }
        
        with self.client.post("/api/orders", json=order_data, catch_response=True) as response:
            if response.status_code == 201:
                response.success()
                # 保存订单ID用于后续操作
                self.current_order_id = order_id
            else:
                response.failure(f"创建订单失败: {response.text}")
    
    @task(4)
    def add_order_item(self):
        """添加订单项"""
        if not hasattr(self, 'current_order_id'):
            return
        
        product_id = f"P{random.randint(1, 10):03d}"
        item_data = {
            "product_id": product_id,
            "quantity": random.randint(1, 5),
            "price": round(random.uniform(10.0, 100.0), 2)
        }
        
        with self.client.post(
            f"/api/orders/{self.current_order_id}/items", 
            json=item_data, 
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"添加订单项失败: {response.text}")
    
    @task(3)
    def confirm_order(self):
        """确认订单"""
        if not hasattr(self, 'current_order_id'):
            return
        
        with self.client.post(
            f"/api/orders/{self.current_order_id}/confirm", 
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 400:
                # 库存不足等业务错误也算正常响应
                response.success()
            else:
                response.failure(f"确认订单失败: {response.text}")
    
    @task(2)
    def process_payment(self):
        """处理支付"""
        if not hasattr(self, 'current_order_id'):
            return
        
        payment_methods = ["credit_card", "debit_card", "alipay", "wechat", "paypal"]
        payment_data = {
            "payment_method": random.choice(payment_methods)
        }
        
        with self.client.post(
            f"/api/orders/{self.current_order_id}/payment", 
            json=payment_data, 
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 400:
                # 订单状态不正确等业务错误
                response.success()
            else:
                response.failure(f"支付失败: {response.text}")
    
    @task(2)
    def get_order_details(self):
        """查询订单详情"""
        if not hasattr(self, 'current_order_id'):
            return
        
        with self.client.get(
            f"/api/orders/{self.current_order_id}", 
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 404:
                response.success()  # 订单不存在也是正常情况
            else:
                response.failure(f"查询订单失败: {response.text}")
    
    @task(1)
    def get_all_orders(self):
        """查询所有订单"""
        with self.client.get("/api/orders", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"查询所有订单失败: {response.text}")
    
    @task(1)
    def get_inventory(self):
        """查询库存"""
        with self.client.get("/api/inventory/products", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"查询库存失败: {response.text}")
    
    @task(1)
    def health_check(self):
        """健康检查"""
        with self.client.get("/health", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"健康检查失败: {response.text}")


class OrderCreationUser(HttpUser):
    """专门测试订单创建的用户类"""
    
    wait_time = between(0.5, 2)
    
    def on_start(self):
        """初始化"""
        self.user_id = random.randint(10000, 99999)
        self.order_counter = 0
    
    @task
    def create_order_only(self):
        """只创建订单"""
        self.order_counter += 1
        order_id = f"LOAD_ORD_{self.user_id}_{self.order_counter}_{int(time.time() * 1000)}"
        
        order_data = {
            "order_id": order_id,
            "customer_id": f"LOAD_CUST_{self.user_id}"
        }
        
        with self.client.post("/api/orders", json=order_data, catch_response=True) as response:
            if response.status_code == 201:
                response.success()
            else:
                response.failure(f"创建订单失败: {response.text}")


class InventoryUser(HttpUser):
    """专门测试库存查询的用户类"""
    
    wait_time = between(0.1, 1)
    
    @task
    def get_inventory_frequently(self):
        """频繁查询库存"""
        with self.client.get("/api/inventory/products", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"查询库存失败: {response.text}")
