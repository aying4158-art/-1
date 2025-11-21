import pytest
import requests
import multiprocessing
import time
from checkout_service import app

class TestCheckoutService:
    """Checkout服务测试类"""
    
    def run_server(self):
        """启动服务器"""
        app.run(port=5000, debug=False, use_reloader=False)
    
    def start_server_process(self):
        """启动服务器进程"""
        p = multiprocessing.Process(target=self.run_server)
        p.start()
        time.sleep(2)
        
        # 验证服务器启动
        try:
            response = requests.get("http://127.0.0.1:5000/health", timeout=5)
            if response.status_code != 200:
                p.terminate()
                raise Exception("Server startup failed")
        except requests.exceptions.RequestException:
            p.terminate()
            raise Exception("Cannot connect to server")
        
        return p
    
    def test_checkout_basic_calculation(self):
        """测试基础结账计算 - 作业要求的测试用例"""
        p = self.start_server_process()
        
        try:
            # 作业要求: price=20, quantity=3, expected total=60
            data = {"items": [{"price": 20, "quantity": 3}]}
            
            response = requests.post("http://127.0.0.1:5000/checkout", json=data)
            
            assert response.status_code == 200
            result = response.json()
            assert result["total"] == 60
            assert result["status"] == "ok"
            
        finally:
            p.terminate()
            p.join()
    
    def test_multiple_items_checkout(self):
        """测试多个商品结账"""
        p = self.start_server_process()
        
        try:
            data = {
                "items": [
                    {"price": 10.5, "quantity": 2},
                    {"price": 5.0, "quantity": 3},
                    {"price": 2.5, "quantity": 4}
                ]
            }
            
            response = requests.post("http://127.0.0.1:5000/checkout", json=data)
            
            assert response.status_code == 200
            result = response.json()
            assert result["total"] == 46.0
            assert result["status"] == "ok"
            
        finally:
            p.terminate()
            p.join()
    
    def test_empty_cart_validation(self):
        """测试空购物车验证"""
        p = self.start_server_process()
        
        try:
            data = {"items": []}
            
            response = requests.post("http://127.0.0.1:5000/checkout", json=data)
            
            assert response.status_code == 400
            result = response.json()
            assert "error" in result
            assert result["error"] == "empty cart"
            
        finally:
            p.terminate()
            p.join()
    
    def test_invalid_item_format_validation(self):
        """测试无效商品格式验证"""
        p = self.start_server_process()
        
        try:
            data = {"items": ["invalid_item"]}
            
            response = requests.post("http://127.0.0.1:5000/checkout", json=data)
            
            assert response.status_code == 400
            result = response.json()
            assert result["error"] == "invalid item format"
            
        finally:
            p.terminate()
            p.join()
    
    def test_missing_fields_validation(self):
        """测试缺少字段验证"""
        p = self.start_server_process()
        
        try:
            data = {"items": [{"price": 10.0}]}  # 缺少quantity
            
            response = requests.post("http://127.0.0.1:5000/checkout", json=data)
            
            assert response.status_code == 400
            result = response.json()
            assert result["error"] == "missing price or quantity"
            
        finally:
            p.terminate()
            p.join()
    
    def test_negative_values_validation(self):
        """测试负数验证"""
        p = self.start_server_process()
        
        try:
            data = {"items": [{"price": -10.0, "quantity": 2}]}
            
            response = requests.post("http://127.0.0.1:5000/checkout", json=data)
            
            assert response.status_code == 400
            result = response.json()
            assert result["error"] == "negative price or quantity"
            
        finally:
            p.terminate()
            p.join()
    
    def test_health_check_endpoint(self):
        """测试健康检查端点"""
        p = self.start_server_process()
        
        try:
            response = requests.get("http://127.0.0.1:5000/health")
            
            assert response.status_code == 200
            result = response.json()
            assert result["status"] == "healthy"
            
        finally:
            p.terminate()
            p.join()
    
    def test_zero_price_calculation(self):
        """测试零价格计算"""
        p = self.start_server_process()
        
        try:
            data = {"items": [{"price": 0, "quantity": 5}]}
            
            response = requests.post("http://127.0.0.1:5000/checkout", json=data)
            
            assert response.status_code == 200
            result = response.json()
            assert result["total"] == 0
            assert result["status"] == "ok"
            
        finally:
            p.terminate()
            p.join()
    
    def test_decimal_precision_calculation(self):
        """测试小数精度计算"""
        p = self.start_server_process()
        
        try:
            data = {"items": [{"price": 0.1, "quantity": 3}]}
            
            response = requests.post("http://127.0.0.1:5000/checkout", json=data)
            
            assert response.status_code == 200
            result = response.json()
            assert abs(result["total"] - 0.3) < 0.0001
            assert result["status"] == "ok"
            
        finally:
            p.terminate()
            p.join()

if __name__ == "__main__":
    pytest.main([
        __file__,
        "-v",
        "--html=homework_report.html",
        "--self-contained-html"
    ])
