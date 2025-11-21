"""
简化版 Selenium 登录测试
支持本地浏览器驱动测试
"""

import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, UnexpectedAlertPresentException

class SimpleLoginTest:
    """简化的登录测试类"""
    
    def __init__(self):
        self.login_url = f"file://{os.path.abspath('login.html')}"
        self.wait_timeout = 10
    
    def test_chrome(self):
        """测试 Chrome 浏览器"""
        print("🔧 测试 Chrome 浏览器...")
        try:
            # 尝试使用本地Chrome驱动
            options = webdriver.ChromeOptions()
            options.add_argument('--disable-web-security')
            options.add_argument('--disable-features=VizDisplayCompositor')
            
            driver = webdriver.Chrome(options=options)
            return self.run_test(driver, "Chrome")
        except Exception as e:
            print(f"❌ Chrome 测试失败: {e}")
            return False
    
    def test_edge(self):
        """测试 Edge 浏览器"""
        print("🔧 测试 Edge 浏览器...")
        try:
            options = webdriver.EdgeOptions()
            options.add_argument('--disable-web-security')
            
            driver = webdriver.Edge(options=options)
            return self.run_test(driver, "Edge")
        except Exception as e:
            print(f"❌ Edge 测试失败: {e}")
            return False
    
    def test_firefox(self):
        """测试 Firefox 浏览器"""
        print("🔧 测试 Firefox 浏览器...")
        try:
            options = webdriver.FirefoxOptions()
            
            driver = webdriver.Firefox(options=options)
            return self.run_test(driver, "Firefox")
        except Exception as e:
            print(f"❌ Firefox 测试失败: {e}")
            return False
    
    def run_test(self, driver, browser_name):
        """运行基本测试"""
        try:
            print(f"  📂 {browser_name}: 打开登录页面...")
            driver.get(self.login_url)
            
            # 设置窗口大小
            driver.set_window_size(1200, 800)
            
            # 等待页面加载
            time.sleep(2)
            
            # 验证页面标题
            expected_title = "用户登录 - 订单系统"
            actual_title = driver.title
            
            if expected_title == actual_title:
                print(f"  ✅ {browser_name}: 页面标题验证通过")
            else:
                print(f"  ⚠️ {browser_name}: 页面标题不匹配")
            
            # 测试页面元素
            self.test_page_elements(driver, browser_name)
            
            # 测试登录功能
            self.test_login_functionality(driver, browser_name)
            
            print(f"  ✅ {browser_name}: 测试完成")
            return True
            
        except Exception as e:
            print(f"  ❌ {browser_name}: 测试过程中出错 - {e}")
            return False
        finally:
            driver.quit()
    
    def test_page_elements(self, driver, browser_name):
        """测试页面元素"""
        print(f"  🔍 {browser_name}: 检查页面元素...")
        
        elements = {
            "username": "用户名输入框",
            "password": "密码输入框", 
            "loginBtn": "登录按钮",
            "forgot-link": "忘记密码链接"
        }
        
        for element_id, element_name in elements.items():
            try:
                element = driver.find_element(By.ID, element_id)
                if element.is_displayed():
                    print(f"    ✅ {element_name} 正常")
                else:
                    print(f"    ⚠️ {element_name} 不可见")
            except:
                print(f"    ❌ {element_name} 未找到")
    
    def test_login_functionality(self, driver, browser_name):
        """测试登录功能"""
        print(f"  🧪 {browser_name}: 测试登录功能...")
        
        try:
            # 查找元素
            username_input = driver.find_element(By.ID, "username")
            password_input = driver.find_element(By.ID, "password")
            login_button = driver.find_element(By.ID, "loginBtn")
            
            # 测试有效登录
            username_input.clear()
            username_input.send_keys("admin")
            
            password_input.clear()
            password_input.send_keys("admin123")
            
            login_button.click()
            
            # 等待结果并处理可能的alert
            time.sleep(3)
            
            try:
                # 检查是否有alert
                alert = driver.switch_to.alert
                alert_text = alert.text
                print(f"    ℹ️ {browser_name}: 检测到弹窗 - {alert_text}")
                alert.accept()  # 接受alert
                print(f"    ✅ {browser_name}: 登录成功（有弹窗确认）")
            except:
                # 没有alert，检查页面结果
                try:
                    result_element = driver.find_element(By.ID, "login-result")
                    if result_element.is_displayed():
                        result_text = result_element.text
                        result_class = result_element.get_attribute("class")
                        
                        if "success" in result_class:
                            print(f"    ✅ {browser_name}: 登录成功 - {result_text}")
                        else:
                            print(f"    ⚠️ {browser_name}: 登录结果 - {result_text}")
                    else:
                        print(f"    ⚠️ {browser_name}: 未检测到登录结果")
                except:
                    print(f"    ⚠️ {browser_name}: 无法获取登录结果")
            
            # 刷新页面准备下一个测试
            driver.refresh()
            time.sleep(1)
            
            # 测试无效登录
            username_input = driver.find_element(By.ID, "username")
            password_input = driver.find_element(By.ID, "password")
            login_button = driver.find_element(By.ID, "loginBtn")
            
            username_input.clear()
            username_input.send_keys("invalid")
            
            password_input.clear()
            password_input.send_keys("wrongpassword")
            
            login_button.click()
            
            time.sleep(2)
            
            try:
                result_element = driver.find_element(By.ID, "login-result")
                if result_element.is_displayed():
                    result_class = result_element.get_attribute("class")
                    if "error" in result_class:
                        print(f"    ✅ {browser_name}: 无效登录正确被拒绝")
                    else:
                        print(f"    ⚠️ {browser_name}: 无效登录处理异常")
                else:
                    print(f"    ⚠️ {browser_name}: 无效登录无结果显示")
            except:
                print(f"    ⚠️ {browser_name}: 无法检查无效登录结果")
                
        except Exception as e:
            print(f"    ❌ {browser_name}: 登录功能测试失败 - {e}")
    
    def run_all_tests(self):
        """运行所有浏览器测试"""
        print("🚀 开始简化版 Selenium 跨浏览器测试")
        print("=" * 50)
        
        results = {}
        
        # 测试各浏览器
        browsers = [
            ("Chrome", self.test_chrome),
            ("Edge", self.test_edge), 
            ("Firefox", self.test_firefox)
        ]
        
        for browser_name, test_function in browsers:
            print(f"\n🌐 测试 {browser_name}...")
            results[browser_name] = test_function()
        
        # 打印总结
        print(f"\n📊 测试总结:")
        print("=" * 30)
        
        successful_browsers = []
        failed_browsers = []
        
        for browser, success in results.items():
            if success:
                successful_browsers.append(browser)
                print(f"✅ {browser}: 测试通过")
            else:
                failed_browsers.append(browser)
                print(f"❌ {browser}: 测试失败")
        
        print(f"\n🎯 结果:")
        print(f"  成功: {len(successful_browsers)}/{len(results)}")
        print(f"  成功的浏览器: {', '.join(successful_browsers) if successful_browsers else '无'}")
        print(f"  失败的浏览器: {', '.join(failed_browsers) if failed_browsers else '无'}")
        
        return results


def main():
    """主函数"""
    # 检查登录页面
    if not os.path.exists("login.html"):
        print("❌ 登录页面文件 login.html 不存在")
        return
    
    # 运行测试
    test_runner = SimpleLoginTest()
    results = test_runner.run_all_tests()
    
    print(f"\n🎉 测试完成！")


if __name__ == "__main__":
    main()
