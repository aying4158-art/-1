"""
Selenium 登录页面自动化测试
支持多种浏览器驱动：Chrome, Edge, Firefox
"""

import os
import time
import json
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.firefox.service import Service as FirefoxService

class LoginPageTest:
    """登录页面测试类"""
    
    def __init__(self):
        self.test_results = []
        self.login_url = f"file://{os.path.abspath('login.html')}"
        self.wait_timeout = 10
        
        # 测试用例数据
        self.test_cases = [
            {
                "name": "有效登录 - admin",
                "username": "admin",
                "password": "admin123",
                "expected_result": "success",
                "description": "使用管理员账号登录"
            },
            {
                "name": "有效登录 - user",
                "username": "user", 
                "password": "user123",
                "expected_result": "success",
                "description": "使用普通用户账号登录"
            },
            {
                "name": "无效登录 - 错误密码",
                "username": "admin",
                "password": "wrongpassword",
                "expected_result": "error",
                "description": "使用错误密码登录"
            },
            {
                "name": "无效登录 - 不存在用户",
                "username": "nonexistent",
                "password": "password",
                "expected_result": "error",
                "description": "使用不存在的用户名登录"
            },
            {
                "name": "空用户名",
                "username": "",
                "password": "password",
                "expected_result": "validation_error",
                "description": "用户名为空的情况"
            },
            {
                "name": "空密码",
                "username": "admin",
                "password": "",
                "expected_result": "validation_error",
                "description": "密码为空的情况"
            }
        ]
    
    def setup_chrome_driver(self):
        """设置 Chrome 浏览器驱动"""
        try:
            print("🔧 设置 Chrome 浏览器驱动...")
            options = webdriver.ChromeOptions()
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            service = ChromeService(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            print("✅ Chrome 驱动设置成功")
            return driver
        except Exception as e:
            print(f"❌ Chrome 驱动设置失败: {e}")
            return None
    
    def setup_edge_driver(self):
        """设置 Edge 浏览器驱动"""
        try:
            print("🔧 设置 Edge 浏览器驱动...")
            options = webdriver.EdgeOptions()
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            service = EdgeService(EdgeChromiumDriverManager().install())
            driver = webdriver.Edge(service=service, options=options)
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            print("✅ Edge 驱动设置成功")
            return driver
        except Exception as e:
            print(f"❌ Edge 驱动设置失败: {e}")
            return None
    
    def setup_firefox_driver(self):
        """设置 Firefox 浏览器驱动"""
        try:
            print("🔧 设置 Firefox 浏览器驱动...")
            options = webdriver.FirefoxOptions()
            options.set_preference("dom.webdriver.enabled", False)
            options.set_preference('useAutomationExtension', False)
            
            service = FirefoxService(GeckoDriverManager().install())
            driver = webdriver.Firefox(service=service, options=options)
            
            print("✅ Firefox 驱动设置成功")
            return driver
        except Exception as e:
            print(f"❌ Firefox 驱动设置失败: {e}")
            return None
    
    def wait_for_element(self, driver, by, value, timeout=None):
        """等待元素出现"""
        if timeout is None:
            timeout = self.wait_timeout
        
        try:
            wait = WebDriverWait(driver, timeout)
            return wait.until(EC.presence_of_element_located((by, value)))
        except TimeoutException:
            return None
    
    def wait_for_clickable(self, driver, by, value, timeout=None):
        """等待元素可点击"""
        if timeout is None:
            timeout = self.wait_timeout
        
        try:
            wait = WebDriverWait(driver, timeout)
            return wait.until(EC.element_to_be_clickable((by, value)))
        except TimeoutException:
            return None
    
    def perform_login_test(self, driver, test_case):
        """执行单个登录测试"""
        test_result = {
            "test_name": test_case["name"],
            "description": test_case["description"],
            "username": test_case["username"],
            "password": test_case["password"],
            "expected_result": test_case["expected_result"],
            "actual_result": None,
            "status": "FAIL",
            "error_message": None,
            "execution_time": 0,
            "browser": driver.capabilities.get('browserName', 'unknown')
        }
        
        start_time = time.time()
        
        try:
            print(f"  📝 执行测试: {test_case['name']}")
            
            # 刷新页面确保干净状态
            driver.refresh()
            time.sleep(1)
            
            # 查找表单元素
            username_input = self.wait_for_element(driver, By.ID, "username")
            password_input = self.wait_for_element(driver, By.ID, "password")
            login_button = self.wait_for_clickable(driver, By.ID, "loginBtn")
            
            if not all([username_input, password_input, login_button]):
                test_result["error_message"] = "无法找到登录表单元素"
                return test_result
            
            # 清空并输入用户名
            username_input.clear()
            if test_case["username"]:
                username_input.send_keys(test_case["username"])
            
            # 清空并输入密码
            password_input.clear()
            if test_case["password"]:
                password_input.send_keys(test_case["password"])
            
            # 点击登录按钮
            login_button.click()
            
            # 等待结果
            time.sleep(2)
            
            # 检查验证错误（空字段）
            if test_case["expected_result"] == "validation_error":
                username_error = driver.find_elements(By.ID, "username-error")
                password_error = driver.find_elements(By.ID, "password-error")
                
                if (username_error and username_error[0].is_displayed()) or \
                   (password_error and password_error[0].is_displayed()):
                    test_result["actual_result"] = "validation_error"
                    test_result["status"] = "PASS"
                else:
                    test_result["actual_result"] = "no_validation_error"
                    test_result["error_message"] = "期望的验证错误未显示"
            
            else:
                # 等待登录结果
                time.sleep(3)  # 等待登录处理完成
                
                # 检查登录结果
                result_element = self.wait_for_element(driver, By.ID, "login-result", timeout=5)
                
                if result_element and result_element.is_displayed():
                    result_text = result_element.text
                    result_class = result_element.get_attribute("class")
                    
                    if "success" in result_class:
                        test_result["actual_result"] = "success"
                    elif "error" in result_class:
                        test_result["actual_result"] = "error"
                    else:
                        test_result["actual_result"] = "unknown"
                    
                    # 检查结果是否符合期望
                    if test_result["actual_result"] == test_case["expected_result"]:
                        test_result["status"] = "PASS"
                    else:
                        test_result["error_message"] = f"期望结果: {test_case['expected_result']}, 实际结果: {test_result['actual_result']}"
                else:
                    test_result["actual_result"] = "no_result"
                    test_result["error_message"] = "未找到登录结果元素"
            
        except Exception as e:
            test_result["error_message"] = f"测试执行异常: {str(e)}"
        
        finally:
            test_result["execution_time"] = round(time.time() - start_time, 2)
        
        return test_result
    
    def test_browser(self, browser_name, setup_function):
        """测试指定浏览器"""
        print(f"\n🌐 开始测试 {browser_name} 浏览器")
        print("=" * 50)
        
        driver = setup_function()
        if not driver:
            print(f"❌ {browser_name} 浏览器驱动初始化失败，跳过测试")
            return []
        
        browser_results = []
        
        try:
            # 设置窗口大小
            driver.set_window_size(1200, 800)
            
            # 打开登录页面
            print(f"📂 打开登录页面: {self.login_url}")
            driver.get(self.login_url)
            
            # 等待页面加载
            time.sleep(2)
            
            # 验证页面标题
            expected_title = "用户登录 - 订单系统"
            actual_title = driver.title
            
            if expected_title == actual_title:
                print(f"✅ 页面标题验证通过: {actual_title}")
            else:
                print(f"⚠️ 页面标题不匹配 - 期望: {expected_title}, 实际: {actual_title}")
            
            # 执行所有测试用例
            for test_case in self.test_cases:
                result = self.perform_login_test(driver, test_case)
                browser_results.append(result)
                
                status_icon = "✅" if result["status"] == "PASS" else "❌"
                print(f"  {status_icon} {result['test_name']}: {result['status']}")
                
                if result["error_message"]:
                    print(f"    💬 {result['error_message']}")
            
            # 测试页面元素
            self.test_page_elements(driver, browser_results)
            
        except Exception as e:
            print(f"❌ {browser_name} 浏览器测试过程中发生错误: {e}")
        
        finally:
            driver.quit()
            print(f"🔚 {browser_name} 浏览器测试完成")
        
        return browser_results
    
    def test_page_elements(self, driver, results):
        """测试页面元素"""
        print("  🔍 测试页面元素...")
        
        elements_to_test = [
            ("username", "用户名输入框"),
            ("password", "密码输入框"),
            ("loginBtn", "登录按钮"),
            ("forgot-link", "忘记密码链接")
        ]
        
        for element_id, element_name in elements_to_test:
            try:
                element = driver.find_element(By.ID, element_id)
                if element.is_displayed():
                    print(f"    ✅ {element_name} 存在且可见")
                else:
                    print(f"    ⚠️ {element_name} 存在但不可见")
            except:
                print(f"    ❌ {element_name} 不存在")
    
    def run_all_tests(self):
        """运行所有浏览器测试"""
        print("🚀 开始 Selenium 跨浏览器登录测试")
        print("=" * 60)
        
        browsers = [
            ("Chrome", self.setup_chrome_driver),
            ("Edge", self.setup_edge_driver),
            ("Firefox", self.setup_firefox_driver)
        ]
        
        all_results = []
        
        for browser_name, setup_function in browsers:
            try:
                browser_results = self.test_browser(browser_name, setup_function)
                all_results.extend(browser_results)
            except Exception as e:
                print(f"❌ {browser_name} 测试失败: {e}")
        
        # 生成测试报告
        self.generate_report(all_results)
        
        return all_results
    
    def generate_report(self, results):
        """生成测试报告"""
        print("\n📊 生成测试报告...")
        
        # 统计结果
        total_tests = len(results)
        passed_tests = len([r for r in results if r["status"] == "PASS"])
        failed_tests = total_tests - passed_tests
        
        # 按浏览器分组
        browser_stats = {}
        for result in results:
            browser = result["browser"]
            if browser not in browser_stats:
                browser_stats[browser] = {"total": 0, "passed": 0, "failed": 0}
            
            browser_stats[browser]["total"] += 1
            if result["status"] == "PASS":
                browser_stats[browser]["passed"] += 1
            else:
                browser_stats[browser]["failed"] += 1
        
        # 生成报告内容
        report = {
            "test_summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "success_rate": round((passed_tests / total_tests * 100), 2) if total_tests > 0 else 0
            },
            "browser_stats": browser_stats,
            "detailed_results": results,
            "generated_at": datetime.now().isoformat()
        }
        
        # 保存 JSON 报告
        with open("selenium_test_report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        # 生成 HTML 报告
        self.generate_html_report(report)
        
        # 打印摘要
        print(f"\n📈 测试摘要:")
        print(f"  总测试数: {total_tests}")
        print(f"  通过: {passed_tests}")
        print(f"  失败: {failed_tests}")
        print(f"  成功率: {report['test_summary']['success_rate']}%")
        
        print(f"\n🌐 各浏览器结果:")
        for browser, stats in browser_stats.items():
            success_rate = round((stats['passed'] / stats['total'] * 100), 2) if stats['total'] > 0 else 0
            print(f"  {browser}: {stats['passed']}/{stats['total']} ({success_rate}%)")
        
        print(f"\n📄 报告文件:")
        print(f"  - JSON报告: selenium_test_report.json")
        print(f"  - HTML报告: selenium_test_report.html")
    
    def generate_html_report(self, report):
        """生成 HTML 测试报告"""
        html_content = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Selenium 登录测试报告</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .header {{ text-align: center; margin-bottom: 30px; }}
        .summary {{ display: flex; justify-content: space-around; margin-bottom: 30px; }}
        .stat-card {{ background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; min-width: 150px; }}
        .stat-number {{ font-size: 2em; font-weight: bold; color: #007bff; }}
        .stat-label {{ color: #666; margin-top: 5px; }}
        .browser-stats {{ margin-bottom: 30px; }}
        .browser-card {{ background: #fff; border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 5px; }}
        .results-table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
        .results-table th, .results-table td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
        .results-table th {{ background-color: #f8f9fa; }}
        .status-pass {{ color: #28a745; font-weight: bold; }}
        .status-fail {{ color: #dc3545; font-weight: bold; }}
        .progress-bar {{ width: 100%; height: 20px; background-color: #e9ecef; border-radius: 10px; overflow: hidden; }}
        .progress-fill {{ height: 100%; background-color: #28a745; transition: width 0.3s ease; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧪 Selenium 登录页面测试报告</h1>
            <p>生成时间: {report['generated_at']}</p>
        </div>
        
        <div class="summary">
            <div class="stat-card">
                <div class="stat-number">{report['test_summary']['total_tests']}</div>
                <div class="stat-label">总测试数</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{report['test_summary']['passed_tests']}</div>
                <div class="stat-label">通过测试</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{report['test_summary']['failed_tests']}</div>
                <div class="stat-label">失败测试</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{report['test_summary']['success_rate']}%</div>
                <div class="stat-label">成功率</div>
            </div>
        </div>
        
        <div class="browser-stats">
            <h2>🌐 各浏览器测试结果</h2>
"""
        
        for browser, stats in report['browser_stats'].items():
            success_rate = round((stats['passed'] / stats['total'] * 100), 2) if stats['total'] > 0 else 0
            html_content += f"""
            <div class="browser-card">
                <h3>{browser}</h3>
                <p>通过: {stats['passed']} / 总计: {stats['total']} (成功率: {success_rate}%)</p>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {success_rate}%"></div>
                </div>
            </div>
"""
        
        html_content += """
        </div>
        
        <h2>📋 详细测试结果</h2>
        <table class="results-table">
            <thead>
                <tr>
                    <th>浏览器</th>
                    <th>测试名称</th>
                    <th>描述</th>
                    <th>用户名</th>
                    <th>期望结果</th>
                    <th>实际结果</th>
                    <th>状态</th>
                    <th>执行时间(s)</th>
                    <th>错误信息</th>
                </tr>
            </thead>
            <tbody>
"""
        
        for result in report['detailed_results']:
            status_class = "status-pass" if result['status'] == 'PASS' else "status-fail"
            error_msg = result.get('error_message', '') or ''
            
            html_content += f"""
                <tr>
                    <td>{result['browser']}</td>
                    <td>{result['test_name']}</td>
                    <td>{result['description']}</td>
                    <td>{result['username']}</td>
                    <td>{result['expected_result']}</td>
                    <td>{result.get('actual_result', 'N/A')}</td>
                    <td class="{status_class}">{result['status']}</td>
                    <td>{result['execution_time']}</td>
                    <td>{error_msg}</td>
                </tr>
"""
        
        html_content += """
            </tbody>
        </table>
    </div>
</body>
</html>
"""
        
        with open("selenium_test_report.html", "w", encoding="utf-8") as f:
            f.write(html_content)


def main():
    """主函数"""
    # 检查登录页面是否存在
    login_file = "login.html"
    if not os.path.exists(login_file):
        print(f"❌ 登录页面文件不存在: {login_file}")
        print("请确保 login.html 文件在当前目录中")
        return
    
    # 创建测试实例并运行
    test_runner = LoginPageTest()
    results = test_runner.run_all_tests()
    
    print(f"\n🎉 所有测试完成！")
    print(f"共执行 {len(results)} 个测试用例")


if __name__ == "__main__":
    main()
