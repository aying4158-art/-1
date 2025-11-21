"""
Pytest配置文件
定义全局fixtures和测试配置
"""

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


@pytest.fixture(scope="session")
def browser_setup():
    """浏览器设置fixture"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    
    # 自动管理ChromeDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    yield driver
    
    driver.quit()


@pytest.fixture(scope="function")
def login_page(browser_setup):
    """登录页面fixture"""
    driver = browser_setup
    driver.get("http://localhost:8080/login")
    return driver


def pytest_html_report_title(report):
    """自定义HTML报告标题"""
    report.title = "Web登录功能自动化测试报告"


def pytest_configure(config):
    """Pytest配置"""
    config.addinivalue_line(
        "markers", "smoke: 冒烟测试用例"
    )
    config.addinivalue_line(
        "markers", "regression: 回归测试用例"
    )
    config.addinivalue_line(
        "markers", "security: 安全测试用例"
    )
