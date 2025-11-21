import pytest
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options

class TestLoginEdge:
    """Web登录功能自动化测试类（Edge浏览器版本）"""
    
    @pytest.fixture(scope="class")
    def driver(self):
        """设置Edge WebDriver"""
        options = Options()
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        try:
            # 尝试使用系统PATH中的msedgedriver
            driver = webdriver.Edge(options=options)
            print("✅ 成功启动Edge浏览器")
        except Exception as e:
            print(f"❌ 无法启动Edge浏览器: {e}")
            print("请确保已安装Edge浏览器和EdgeDriver")
            print("EdgeDriver下载地址: https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/")
            pytest.skip("Edge浏览器或EdgeDriver不可用")
        
        driver.maximize_window()
        
        # 获取登录页面的绝对路径
        current_dir = os.path.dirname(os.path.abspath(__file__))
        login_page = os.path.join(current_dir, "login.html")
        driver.get(f"file:///{login_page}")
        
        yield driver
        driver.quit()
    
    @pytest.fixture(autouse=True)
    def setup_method(self, driver):
        """每个测试方法执行前的设置"""
        driver.refresh()
        time.sleep(1)
    
    def test_tc001_successful_login(self, driver):
        """TC001 - 正常登录测试"""
        # 输入正确的用户名和密码
        username_field = driver.find_element(By.ID, "username")
        password_field = driver.find_element(By.ID, "password")
        login_button = driver.find_element(By.ID, "loginBtn")
        
        username_field.send_keys("admin")
        password_field.send_keys("password123")
        login_button.click()
        
        # 验证成功消息
        success_message = WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located((By.ID, "successMessage"))
        )
        assert "登录成功" in success_message.text
        print("✅ TC001 - 正常登录测试通过")
        
    def test_tc002_empty_username(self, driver):
        """TC002 - 用户名为空测试"""
        password_field = driver.find_element(By.ID, "password")
        login_button = driver.find_element(By.ID, "loginBtn")
        
        password_field.send_keys("password123")
        login_button.click()
        
        # 验证错误消息
        error_message = WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located((By.ID, "errorMessage"))
        )
        assert "请输入用户名" in error_message.text
        print("✅ TC002 - 用户名为空测试通过")
        
    def test_tc003_empty_password(self, driver):
        """TC003 - 密码为空测试"""
        username_field = driver.find_element(By.ID, "username")
        login_button = driver.find_element(By.ID, "loginBtn")
        
        username_field.send_keys("admin")
        login_button.click()
        
        # 验证错误消息
        error_message = WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located((By.ID, "errorMessage"))
        )
        assert "请输入密码" in error_message.text
        print("✅ TC003 - 密码为空测试通过")
        
    def test_tc004_empty_username_and_password(self, driver):
        """TC004 - 用户名和密码都为空测试"""
        login_button = driver.find_element(By.ID, "loginBtn")
        login_button.click()
        
        # 验证错误消息
        error_message = WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located((By.ID, "errorMessage"))
        )
        assert "请输入用户名和密码" in error_message.text
        print("✅ TC004 - 用户名和密码都为空测试通过")
        
    def test_tc005_wrong_username(self, driver):
        """TC005 - 错误用户名测试"""
        username_field = driver.find_element(By.ID, "username")
        password_field = driver.find_element(By.ID, "password")
        login_button = driver.find_element(By.ID, "loginBtn")
        
        username_field.send_keys("wronguser")
        password_field.send_keys("password123")
        login_button.click()
        
        # 验证错误消息
        error_message = WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located((By.ID, "errorMessage"))
        )
        assert "用户名或密码错误" in error_message.text
        print("✅ TC005 - 错误用户名测试通过")
        
    def test_tc006_wrong_password(self, driver):
        """TC006 - 错误密码测试"""
        username_field = driver.find_element(By.ID, "username")
        password_field = driver.find_element(By.ID, "password")
        login_button = driver.find_element(By.ID, "loginBtn")
        
        username_field.send_keys("admin")
        password_field.send_keys("wrongpassword")
        login_button.click()
        
        # 验证错误消息
        error_message = WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located((By.ID, "errorMessage"))
        )
        assert "用户名或密码错误" in error_message.text
        print("✅ TC006 - 错误密码测试通过")
        
    def test_tc007_sql_injection(self, driver):
        """TC007 - SQL注入测试"""
        username_field = driver.find_element(By.ID, "username")
        password_field = driver.find_element(By.ID, "password")
        login_button = driver.find_element(By.ID, "loginBtn")
        
        username_field.send_keys("admin' OR '1'='1")
        password_field.send_keys("anything")
        login_button.click()
        
        # 验证错误消息（应该登录失败）
        error_message = WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located((By.ID, "errorMessage"))
        )
        assert "用户名或密码错误" in error_message.text
        print("✅ TC007 - SQL注入测试通过")
        
    def test_tc008_password_hidden(self, driver):
        """TC008 - 密码显示隐藏测试"""
        password_field = driver.find_element(By.ID, "password")
        
        # 验证密码输入框类型为password
        assert password_field.get_attribute("type") == "password"
        print("✅ TC008 - 密码显示隐藏测试通过")
        
    def test_tc009_login_button_clickable(self, driver):
        """TC009 - 登录按钮状态测试"""
        login_button = driver.find_element(By.ID, "loginBtn")
        
        # 验证按钮可点击
        assert login_button.is_enabled()
        assert login_button.is_displayed()
        print("✅ TC009 - 登录按钮状态测试通过")
        
    def test_tc010_page_elements_exist(self, driver):
        """TC010 - 页面元素存在性测试"""
        # 验证页面标题
        assert "用户登录" in driver.title
        
        # 验证必要元素存在
        username_field = driver.find_element(By.ID, "username")
        password_field = driver.find_element(By.ID, "password")
        login_button = driver.find_element(By.ID, "loginBtn")
        
        assert username_field.is_displayed()
        assert password_field.is_displayed()
        assert login_button.is_displayed()
        
        # 验证占位符文本
        assert username_field.get_attribute("placeholder") == "请输入用户名"
        assert password_field.get_attribute("placeholder") == "请输入密码"
        print("✅ TC010 - 页面元素存在性测试通过")
