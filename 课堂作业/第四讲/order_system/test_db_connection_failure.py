"""
数据库连接中断测试脚本
测试Flask服务在支付请求过程中数据库连接中断的处理能力
"""

import requests
import time
import json
import threading
from datetime import datetime


class DatabaseConnectionTest:
    """数据库连接测试类"""
    
    def __init__(self, base_url="http://localhost:5000"):
        """
        初始化测试类
        
        Args:
            base_url: Flask服务的基础URL
        """
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
    
    def log_result(self, test_name: str, success: bool, message: str, details: dict = None):
        """记录测试结果"""
        result = {
            "test_name": test_name,
            "success": success,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "details": details or {}
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        if details:
            print(f"   详情: {json.dumps(details, indent=2, ensure_ascii=False)}")
    
    def check_service_health(self) -> bool:
        """检查服务健康状态"""
        try:
            response = self.session.get(f"{self.base_url}/")
            if response.status_code == 200:
                self.log_result("服务健康检查", True, "服务正常运行")
                return True
            else:
                self.log_result("服务健康检查", False, f"服务返回状态码: {response.status_code}")
                return False
        except Exception as e:
            self.log_result("服务健康检查", False, f"无法连接到服务: {str(e)}")
            return False
    
    def init_test_data(self) -> bool:
        """初始化测试数据"""
        try:
            response = self.session.post(f"{self.base_url}/api/test/init-data")
            if response.status_code == 200:
                data = response.json()
                self.log_result("初始化测试数据", True, "测试数据初始化成功", data)
                return True
            else:
                self.log_result("初始化测试数据", False, f"初始化失败: {response.status_code}")
                return False
        except Exception as e:
            self.log_result("初始化测试数据", False, f"初始化异常: {str(e)}")
            return False
    
    def create_test_order(self, order_id: str = "TEST_ORDER_001") -> bool:
        """创建测试订单"""
        try:
            # 创建订单
            order_data = {
                "order_id": order_id,
                "customer_id": "CUSTOMER_001"
            }
            response = self.session.post(f"{self.base_url}/api/orders", json=order_data)
            
            if response.status_code != 201:
                self.log_result("创建订单", False, f"创建订单失败: {response.status_code}")
                return False
            
            # 添加商品
            item_data = {
                "product_id": "P001",
                "quantity": 2,
                "price": 100.0
            }
            response = self.session.post(f"{self.base_url}/api/orders/{order_id}/items", json=item_data)
            
            if response.status_code != 200:
                self.log_result("添加商品", False, f"添加商品失败: {response.status_code}")
                return False
            
            # 确认订单
            response = self.session.post(f"{self.base_url}/api/orders/{order_id}/confirm")
            
            if response.status_code == 200:
                self.log_result("创建测试订单", True, f"订单 {order_id} 创建成功")
                return True
            else:
                self.log_result("确认订单", False, f"确认订单失败: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("创建测试订单", False, f"创建订单异常: {str(e)}")
            return False
    
    def test_normal_payment(self, order_id: str = "TEST_ORDER_001") -> bool:
        """测试正常支付流程"""
        try:
            payment_data = {
                "payment_method": "credit_card"
            }
            
            response = self.session.post(f"{self.base_url}/api/orders/{order_id}/payment", json=payment_data)
            
            if response.status_code == 200:
                data = response.json()
                self.log_result("正常支付测试", True, "支付成功", data)
                return True
            else:
                error_data = response.json() if response.content else {}
                self.log_result("正常支付测试", False, f"支付失败: {response.status_code}", error_data)
                return False
                
        except Exception as e:
            self.log_result("正常支付测试", False, f"支付异常: {str(e)}")
            return False
    
    def test_payment_with_db_disconnection(self, order_id: str = "TEST_ORDER_002") -> bool:
        """测试支付过程中数据库连接中断"""
        try:
            print("\n=== 开始测试支付过程中数据库连接中断 ===")
            
            # 创建新订单
            if not self.create_test_order(order_id):
                return False
            
            # 手动断开数据库连接
            print("断开数据库连接...")
            response = self.session.post(f"{self.base_url}/api/database/disconnect")
            if response.status_code != 200:
                self.log_result("断开数据库", False, "无法断开数据库连接")
                return False
            
            # 尝试支付（应该失败）
            print("尝试在数据库断开状态下进行支付...")
            payment_data = {
                "payment_method": "credit_card"
            }
            
            response = self.session.post(f"{self.base_url}/api/orders/{order_id}/payment", json=payment_data)
            
            if response.status_code == 503:  # 服务不可用
                error_data = response.json()
                self.log_result("数据库断开时支付", True, "正确返回数据库连接错误", error_data)
                
                # 检查错误信息
                if "数据库连接错误" in error_data.get("error", ""):
                    self.log_result("错误信息检查", True, "错误信息正确")
                else:
                    self.log_result("错误信息检查", False, "错误信息不正确")
                
                return True
            else:
                self.log_result("数据库断开时支付", False, f"未正确处理数据库断开: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("数据库断开测试", False, f"测试异常: {str(e)}")
            return False
    
    def test_database_recovery(self, order_id: str = "TEST_ORDER_003") -> bool:
        """测试数据库恢复后的支付"""
        try:
            print("\n=== 测试数据库恢复后的支付 ===")
            
            # 创建新订单
            if not self.create_test_order(order_id):
                return False
            
            # 重新连接数据库
            print("重新连接数据库...")
            response = self.session.post(f"{self.base_url}/api/database/connect")
            if response.status_code != 200:
                self.log_result("重连数据库", False, "无法重连数据库")
                return False
            
            # 等待一下确保连接稳定
            time.sleep(1)
            
            # 尝试支付（应该成功）
            print("在数据库恢复后尝试支付...")
            payment_data = {
                "payment_method": "credit_card"
            }
            
            response = self.session.post(f"{self.base_url}/api/orders/{order_id}/payment", json=payment_data)
            
            if response.status_code == 200:
                data = response.json()
                self.log_result("数据库恢复后支付", True, "支付成功", data)
                return True
            else:
                error_data = response.json() if response.content else {}
                self.log_result("数据库恢复后支付", False, f"支付失败: {response.status_code}", error_data)
                return False
                
        except Exception as e:
            self.log_result("数据库恢复测试", False, f"测试异常: {str(e)}")
            return False
    
    def test_automatic_retry_mechanism(self, order_id: str = "TEST_ORDER_004") -> bool:
        """测试自动重试机制"""
        try:
            print("\n=== 测试自动重试机制 ===")
            
            # 创建新订单
            if not self.create_test_order(order_id):
                return False
            
            def simulate_temporary_failure():
                """模拟临时数据库故障"""
                time.sleep(1)  # 等待支付开始
                print("模拟数据库临时故障...")
                self.session.post(f"{self.base_url}/api/database/simulate-failure")
                
                time.sleep(3)  # 等待重试
                print("恢复数据库连接...")
                self.session.post(f"{self.base_url}/api/database/connect")
            
            # 启动后台线程模拟故障
            failure_thread = threading.Thread(target=simulate_temporary_failure)
            failure_thread.start()
            
            # 尝试支付
            payment_data = {
                "payment_method": "credit_card"
            }
            
            start_time = time.time()
            response = self.session.post(f"{self.base_url}/api/orders/{order_id}/payment", json=payment_data)
            end_time = time.time()
            
            failure_thread.join()  # 等待后台线程完成
            
            # 检查结果
            if response.status_code == 200:
                data = response.json()
                duration = end_time - start_time
                self.log_result("自动重试机制", True, f"支付成功，耗时 {duration:.2f} 秒", data)
                return True
            else:
                error_data = response.json() if response.content else {}
                self.log_result("自动重试机制", False, f"重试失败: {response.status_code}", error_data)
                return False
                
        except Exception as e:
            self.log_result("自动重试测试", False, f"测试异常: {str(e)}")
            return False
    
    def test_payment_status_tracking(self, order_id: str = "TEST_ORDER_005") -> bool:
        """测试支付状态跟踪"""
        try:
            print("\n=== 测试支付状态跟踪 ===")
            
            # 创建新订单
            if not self.create_test_order(order_id):
                return False
            
            # 进行支付
            payment_data = {
                "payment_method": "credit_card"
            }
            
            response = self.session.post(f"{self.base_url}/api/orders/{order_id}/payment", json=payment_data)
            
            if response.status_code == 200:
                # 检查支付状态
                payment_id = f"PAY_{order_id}"
                response = self.session.get(f"{self.base_url}/api/payments/{payment_id}/status")
                
                if response.status_code == 200:
                    status_data = response.json()
                    self.log_result("支付状态跟踪", True, "成功获取支付状态", status_data)
                    
                    # 检查状态详情
                    if "steps" in status_data and len(status_data["steps"]) > 0:
                        self.log_result("支付步骤跟踪", True, f"记录了 {len(status_data['steps'])} 个处理步骤")
                    else:
                        self.log_result("支付步骤跟踪", False, "未记录处理步骤")
                    
                    return True
                else:
                    self.log_result("支付状态跟踪", False, "无法获取支付状态")
                    return False
            else:
                self.log_result("支付状态跟踪", False, "支付失败，无法测试状态跟踪")
                return False
                
        except Exception as e:
            self.log_result("支付状态跟踪测试", False, f"测试异常: {str(e)}")
            return False
    
    def get_system_stats(self) -> dict:
        """获取系统统计信息"""
        try:
            response = self.session.get(f"{self.base_url}/api/stats")
            if response.status_code == 200:
                return response.json()
            else:
                return {}
        except:
            return {}
    
    def run_all_tests(self):
        """运行所有测试"""
        print("=" * 60)
        print("开始数据库连接中断测试")
        print("=" * 60)
        
        # 检查服务健康状态
        if not self.check_service_health():
            print("❌ 服务不可用，测试终止")
            return
        
        # 初始化测试数据
        if not self.init_test_data():
            print("❌ 测试数据初始化失败，测试终止")
            return
        
        # 测试1: 正常支付流程
        print("\n--- 测试1: 正常支付流程 ---")
        self.test_normal_payment("NORMAL_ORDER_001")
        
        # 测试2: 数据库连接中断时的支付
        print("\n--- 测试2: 数据库连接中断时的支付 ---")
        self.test_payment_with_db_disconnection("DB_DISCONNECT_ORDER")
        
        # 测试3: 数据库恢复后的支付
        print("\n--- 测试3: 数据库恢复后的支付 ---")
        self.test_database_recovery("DB_RECOVERY_ORDER")
        
        # 测试4: 自动重试机制
        print("\n--- 测试4: 自动重试机制 ---")
        self.test_automatic_retry_mechanism("RETRY_ORDER")
        
        # 测试5: 支付状态跟踪
        print("\n--- 测试5: 支付状态跟踪 ---")
        self.test_payment_status_tracking("STATUS_ORDER")
        
        # 输出测试总结
        self.print_test_summary()
    
    def print_test_summary(self):
        """打印测试总结"""
        print("\n" + "=" * 60)
        print("测试总结")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["success"]])
        failed_tests = total_tests - passed_tests
        
        print(f"总测试数: {total_tests}")
        print(f"通过: {passed_tests}")
        print(f"失败: {failed_tests}")
        print(f"成功率: {(passed_tests/total_tests*100):.1f}%")
        
        # 显示失败的测试
        if failed_tests > 0:
            print("\n失败的测试:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  ❌ {result['test_name']}: {result['message']}")
        
        # 显示系统统计
        stats = self.get_system_stats()
        if stats:
            print(f"\n系统统计:")
            print(f"  数据库连接次数: {stats.get('database', {}).get('connection_count', 0)}")
            print(f"  数据库操作次数: {stats.get('database', {}).get('operation_count', 0)}")
            print(f"  数据库错误次数: {stats.get('database', {}).get('error_count', 0)}")
            print(f"  支付处理中: {stats.get('payments', {}).get('processing', 0)}")
            print(f"  支付成功: {stats.get('payments', {}).get('completed', 0)}")
            print(f"  支付失败: {stats.get('payments', {}).get('failed', 0)}")


def main():
    """主函数"""
    print("数据库连接中断测试工具")
    print("确保Flask服务正在运行在 http://localhost:5000")
    
    # 等待用户确认
    input("按回车键开始测试...")
    
    # 创建测试实例并运行
    tester = DatabaseConnectionTest()
    tester.run_all_tests()
    
    # 保存测试结果
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"db_connection_test_results_{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(tester.test_results, f, indent=2, ensure_ascii=False)
    
    print(f"\n测试结果已保存到: {filename}")


if __name__ == "__main__":
    main()
