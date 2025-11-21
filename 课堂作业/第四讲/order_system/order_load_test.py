"""
专门针对 /api/orders 接口的 Locust 负载测试
模拟 100 用户同时请求订单接口
"""

from locust import HttpUser, task, between
import random
import time
import json

class OrderAPIUser(HttpUser):
    """专门测试订单 API 的用户"""
    
    # 设置较短的等待时间以增加并发压力
    wait_time = between(0.1, 0.5)
    
    def on_start(self):
        """用户开始时的初始化"""
        self.user_id = random.randint(100000, 999999)
        self.order_counter = 0
        print(f"用户 {self.user_id} 开始测试")
    
    @task(10)
    def create_order(self):
        """创建订单 - 主要测试任务"""
        self.order_counter += 1
        
        # 生成唯一的订单ID
        timestamp = int(time.time() * 1000)  # 毫秒级时间戳
        order_id = f"LOAD_TEST_{self.user_id}_{self.order_counter}_{timestamp}"
        
        order_data = {
            "order_id": order_id,
            "customer_id": f"CUSTOMER_{self.user_id}"
        }
        
        # 记录请求开始时间
        start_time = time.time()
        
        with self.client.post(
            "/api/orders", 
            json=order_data, 
            catch_response=True,
            name="POST /api/orders"
        ) as response:
            
            # 计算响应时间
            response_time = (time.time() - start_time) * 1000  # 转换为毫秒
            
            if response.status_code == 201:
                response.success()
                # 可选：打印成功信息
                if self.order_counter % 10 == 0:  # 每10个请求打印一次
                    print(f"用户 {self.user_id}: 成功创建第 {self.order_counter} 个订单，响应时间: {response_time:.2f}ms")
            else:
                response.failure(f"创建订单失败 - 状态码: {response.status_code}, 响应: {response.text}")
                print(f"用户 {self.user_id}: 订单创建失败 - {response.text}")
    
    @task(3)
    def get_orders(self):
        """查询所有订单"""
        with self.client.get(
            "/api/orders", 
            catch_response=True,
            name="GET /api/orders"
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"查询订单失败: {response.text}")
    
    @task(2)
    def get_specific_order(self):
        """查询特定订单"""
        if self.order_counter > 0:
            # 查询最近创建的订单
            timestamp = int(time.time() * 1000)
            order_id = f"LOAD_TEST_{self.user_id}_{self.order_counter}_{timestamp}"
            
            with self.client.get(
                f"/api/orders/{order_id}", 
                catch_response=True,
                name="GET /api/orders/{id}"
            ) as response:
                if response.status_code in [200, 404]:  # 404也是正常的
                    response.success()
                else:
                    response.failure(f"查询特定订单失败: {response.text}")
    
    @task(1)
    def health_check(self):
        """健康检查"""
        with self.client.get(
            "/health", 
            catch_response=True,
            name="GET /health"
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"健康检查失败: {response.text}")


class HighFrequencyOrderUser(HttpUser):
    """高频订单创建用户 - 专门用于压力测试"""
    
    wait_time = between(0.05, 0.2)  # 更短的等待时间
    
    def on_start(self):
        self.user_id = random.randint(1000000, 9999999)
        self.order_counter = 0
    
    @task
    def rapid_order_creation(self):
        """快速创建订单"""
        self.order_counter += 1
        
        # 使用更精确的时间戳避免冲突
        timestamp = time.time_ns()  # 纳秒级时间戳
        order_id = f"RAPID_{self.user_id}_{timestamp}"
        
        order_data = {
            "order_id": order_id,
            "customer_id": f"RAPID_CUSTOMER_{self.user_id}"
        }
        
        with self.client.post(
            "/api/orders", 
            json=order_data, 
            catch_response=True,
            name="POST /api/orders (Rapid)"
        ) as response:
            if response.status_code == 201:
                response.success()
            else:
                response.failure(f"快速创建订单失败: {response.text}")


# 如果直接运行此文件，提供命令行启动选项
if __name__ == "__main__":
    import os
    import sys
    
    print("🚀 订单系统负载测试")
    print("=" * 50)
    print("测试目标: /api/orders 接口")
    print("建议配置: 100 用户, 10 spawn rate")
    print("=" * 50)
    
    # 检查服务器是否运行
    import requests
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ 服务器运行正常")
        else:
            print("⚠️  服务器响应异常")
    except:
        print("❌ 无法连接到服务器，请确保服务器在 http://localhost:8000 运行")
        sys.exit(1)
    
    print("\n启动 Locust Web UI...")
    print("访问 http://localhost:8089 开始测试")
    
    # 启动 Locust
    os.system("locust -f order_load_test.py --host=http://localhost:8000")
