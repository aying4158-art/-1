"""
演示版本的测试脚本 - 不需要真实Web服务器
展示测试框架的基本功能
"""

import pytest
import time
from unittest.mock import Mock, patch


class MockWebElement:
    """模拟Web元素"""
    def __init__(self, tag_name="input", element_type="text", text=""):
        self.tag_name = tag_name
        self.element_type = element_type
        self.text = text
        self.value = ""
        
    def send_keys(self, keys):
        self.value += keys
        print(f"输入: {keys}")
        
    def clear(self):
        self.value = ""
        print("清空输入框")
        
    def click(self):
        print("点击元素")
        
    def get_attribute(self, name):
        if name == "type":
            return self.element_type
        return None
        
    def is_enabled(self):
        return True
        
    def is_displayed(self):
        return True


class MockWebDriver:
    """模拟WebDriver"""
    def __init__(self):
        self.current_url = "http://localhost:8080/login"
        self.title = "登录页面"
        
    def get(self, url):
        self.current_url = url
        print(f"导航到: {url}")
        
    def find_element(self, by, value):
        if value == "username":
            return MockWebElement("input", "text")
        elif value == "password":
            return MockWebElement("input", "password")
        elif value == "login-btn":
            return MockWebElement("button", "submit")
        elif value == "title":
            return MockWebElement("title", "text", "登录页面")
        elif value == "error-message":
            return MockWebElement("div", "text", "用户名或密码错误")
        return MockWebElement()
        
    def quit(self):
        print("关闭浏览器")


class TestLoginDemo:
    """登录功能演示测试类"""
    
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        """测试前置和后置操作"""
        print("\n=== 测试开始 ===")
        self.driver = MockWebDriver()
        yield
        self.driver.quit()
        print("=== 测试结束 ===")
    
    def navigate_to_login_page(self):
        """导航到登录页面"""
        self.driver.get("http://localhost:8080/login")
        
    def enter_credentials(self, username, password):
        """输入用户名和密码"""
        username_field = self.driver.find_element("id", "username")
        password_field = self.driver.find_element("id", "password")
        
        username_field.clear()
        username_field.send_keys(username)
        
        password_field.clear()
        password_field.send_keys(password)
        
    def click_login_button(self):
        """点击登录按钮"""
        login_button = self.driver.find_element("id", "login-btn")
        login_button.click()
        
    def simulate_login_result(self, username, password):
        """模拟登录结果"""
        if username == "admin" and password == "password123":
            self.driver.current_url = "http://localhost:8080/dashboard"
            return True, None
        elif not username:
            return False, "请输入用户名"
        elif not password:
            return False, "请输入密码"
        elif not username and not password:
            return False, "请输入用户名和密码"
        else:
            return False, "用户名或密码错误"

    def test_demo_successful_login(self):
        """演示 - 正常登录测试"""
        print("\n测试用例: 正常登录")
        self.navigate_to_login_page()
        self.enter_credentials("admin", "password123")
        self.click_login_button()
        
        success, error = self.simulate_login_result("admin", "password123")
        assert success, f"登录失败: {error}"
        assert "dashboard" in self.driver.current_url, "未跳转到主页面"
        print("✅ 登录成功，跳转到主页面")
        
    def test_demo_empty_username(self):
        """演示 - 用户名为空测试"""
        print("\n测试用例: 用户名为空")
        self.navigate_to_login_page()
        self.enter_credentials("", "password123")
        self.click_login_button()
        
        success, error = self.simulate_login_result("", "password123")
        assert not success, "应该登录失败"
        assert "用户名" in error, f"错误消息不正确: {error}"
        print(f"✅ 正确显示错误消息: {error}")
        
    def test_demo_empty_password(self):
        """演示 - 密码为空测试"""
        print("\n测试用例: 密码为空")
        self.navigate_to_login_page()
        self.enter_credentials("admin", "")
        self.click_login_button()
        
        success, error = self.simulate_login_result("admin", "")
        assert not success, "应该登录失败"
        assert "密码" in error, f"错误消息不正确: {error}"
        print(f"✅ 正确显示错误消息: {error}")
        
    def test_demo_wrong_credentials(self):
        """演示 - 错误凭据测试"""
        print("\n测试用例: 错误的用户名和密码")
        self.navigate_to_login_page()
        self.enter_credentials("wronguser", "wrongpass")
        self.click_login_button()
        
        success, error = self.simulate_login_result("wronguser", "wrongpass")
        assert not success, "应该登录失败"
        assert "用户名或密码错误" in error, f"错误消息不正确: {error}"
        print(f"✅ 正确显示错误消息: {error}")
        
    def test_demo_sql_injection(self):
        """演示 - SQL注入防护测试"""
        print("\n测试用例: SQL注入攻击")
        self.navigate_to_login_page()
        malicious_input = "admin' OR '1'='1"
        self.enter_credentials(malicious_input, "anything")
        self.click_login_button()
        
        # 模拟安全的系统应该拒绝SQL注入
        success, error = self.simulate_login_result(malicious_input, "anything")
        assert not success, "SQL注入攻击不应该成功"
        print("✅ 系统正确防护了SQL注入攻击")
        
    def test_demo_password_field_type(self):
        """演示 - 密码框类型测试"""
        print("\n测试用例: 密码框安全性")
        self.navigate_to_login_page()
        password_field = self.driver.find_element("id", "password")
        
        field_type = password_field.get_attribute("type")
        assert field_type == "password", f"密码框类型不正确: {field_type}"
        print("✅ 密码框正确设置为password类型")
        
    def test_demo_page_elements(self):
        """演示 - 页面元素存在性测试"""
        print("\n测试用例: 页面元素检查")
        self.navigate_to_login_page()
        
        # 检查必要元素
        username_field = self.driver.find_element("id", "username")
        password_field = self.driver.find_element("id", "password")
        login_button = self.driver.find_element("id", "login-btn")
        
        assert username_field.is_displayed(), "用户名输入框不存在"
        assert password_field.is_displayed(), "密码输入框不存在"
        assert login_button.is_displayed(), "登录按钮不存在"
        print("✅ 所有必要的页面元素都存在")


if __name__ == "__main__":
    # 运行演示测试
    pytest.main([__file__, "-v", "-s"])
