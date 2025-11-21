"""
登录功能自动化测试脚本
使用Selenium WebDriver + Pytest框架
"""

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time


class TestLoginFunctional:
    """登录功能测试类"""
    
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        """测试前置和后置操作"""
        # 设置Chrome选项
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # 无头模式运行
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        # 初始化WebDriver
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.implicitly_wait(10)
        self.wait = WebDriverWait(self.driver, 10)
        
        # 测试执行
        yield
        
        # 清理资源
        self.driver.quit()
    
    def navigate_to_login_page(self):
        """导航到登录页面"""
        self.driver.get("http://localhost:8080/login")
        
    def enter_username(self, username):
        """输入用户名"""
        username_field = self.wait.until(
            EC.presence_of_element_located((By.ID, "username"))
        )
        username_field.clear()
        username_field.send_keys(username)
        
    def enter_password(self, password):
        """输入密码"""
        password_field = self.driver.find_element(By.ID, "password")
        password_field.clear()
        password_field.send_keys(password)
        
    def click_login_button(self):
        """点击登录按钮"""
        login_button = self.driver.find_element(By.ID, "login-btn")
        login_button.click()
        
    def get_error_message(self):
        """获取错误消息"""
        try:
            error_element = self.wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "error-message"))
            )
            return error_element.text
        except:
            return None
            
    def is_logged_in_successfully(self):
        """检查是否登录成功"""
        try:
            self.wait.until(EC.url_contains("dashboard"))
            return True
        except:
            return False

    def test_tc001_successful_login(self):
        """TC001 - 正常登录测试"""
        self.navigate_to_login_page()
        self.enter_username("admin")
        self.enter_password("password123")
        self.click_login_button()
        
        assert self.is_logged_in_successfully(), "登录失败，未跳转到主页面"
        
    def test_tc002_empty_username(self):
        """TC002 - 用户名为空测试"""
        self.navigate_to_login_page()
        self.enter_username("")
        self.enter_password("password123")
        self.click_login_button()
        
        error_msg = self.get_error_message()
        assert error_msg is not None, "未显示错误消息"
        assert "用户名" in error_msg, f"错误消息不正确: {error_msg}"
        
    def test_tc003_empty_password(self):
        """TC003 - 密码为空测试"""
        self.navigate_to_login_page()
        self.enter_username("admin")
        self.enter_password("")
        self.click_login_button()
        
        error_msg = self.get_error_message()
        assert error_msg is not None, "未显示错误消息"
        assert "密码" in error_msg, f"错误消息不正确: {error_msg}"
        
    def test_tc004_both_empty(self):
        """TC004 - 用户名和密码都为空测试"""
        self.navigate_to_login_page()
        self.enter_username("")
        self.enter_password("")
        self.click_login_button()
        
        error_msg = self.get_error_message()
        assert error_msg is not None, "未显示错误消息"
        assert "用户名" in error_msg and "密码" in error_msg, f"错误消息不完整: {error_msg}"
        
    def test_tc005_wrong_username(self):
        """TC005 - 错误用户名测试"""
        self.navigate_to_login_page()
        self.enter_username("wronguser")
        self.enter_password("password123")
        self.click_login_button()
        
        error_msg = self.get_error_message()
        assert error_msg is not None, "未显示错误消息"
        assert "用户名或密码错误" in error_msg, f"错误消息不正确: {error_msg}"
        
    def test_tc006_wrong_password(self):
        """TC006 - 错误密码测试"""
        self.navigate_to_login_page()
        self.enter_username("admin")
        self.enter_password("wrongpassword")
        self.click_login_button()
        
        error_msg = self.get_error_message()
        assert error_msg is not None, "未显示错误消息"
        assert "用户名或密码错误" in error_msg, f"错误消息不正确: {error_msg}"
        
    def test_tc007_sql_injection(self):
        """TC007 - SQL注入测试"""
        self.navigate_to_login_page()
        self.enter_username("admin' OR '1'='1")
        self.enter_password("anything")
        self.click_login_button()
        
        # 应该登录失败，不能绕过认证
        assert not self.is_logged_in_successfully(), "SQL注入攻击成功，存在安全漏洞"
        
    def test_tc008_password_masking(self):
        """TC008 - 密码显示隐藏测试"""
        self.navigate_to_login_page()
        password_field = self.driver.find_element(By.ID, "password")
        
        # 检查密码框类型是否为password
        input_type = password_field.get_attribute("type")
        assert input_type == "password", f"密码框类型不正确: {input_type}"
        
    def test_tc009_login_button_state(self):
        """TC009 - 登录按钮状态测试"""
        self.navigate_to_login_page()
        login_button = self.driver.find_element(By.ID, "login-btn")
        
        # 检查按钮是否可点击
        assert login_button.is_enabled(), "登录按钮不可点击"
        assert login_button.is_displayed(), "登录按钮不可见"
        
    def test_tc010_page_elements_existence(self):
        """TC010 - 页面元素存在性测试"""
        self.navigate_to_login_page()
        
        # 检查必要元素是否存在
        username_field = self.driver.find_element(By.ID, "username")
        password_field = self.driver.find_element(By.ID, "password")
        login_button = self.driver.find_element(By.ID, "login-btn")
        page_title = self.driver.find_element(By.TAG_NAME, "title")
        
        assert username_field.is_displayed(), "用户名输入框不存在"
        assert password_field.is_displayed(), "密码输入框不存在"
        assert login_button.is_displayed(), "登录按钮不存在"
        assert page_title is not None, "页面标题不存在"


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "--tb=short"])
