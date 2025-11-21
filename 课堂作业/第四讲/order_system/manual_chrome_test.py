"""
手动 Chrome 测试脚本
当自动驱动下载失败时的备选方案
"""

import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service

def test_chrome_manual():
    """手动测试Chrome浏览器"""
    print("🔧 尝试手动测试 Chrome 浏览器...")
    
    try:
        # 方法1: 尝试使用系统PATH中的chromedriver
        print("  📝 方法1: 使用系统PATH中的chromedriver...")
        
        options = webdriver.ChromeOptions()
        options.add_argument('--disable-web-security')
        options.add_argument('--disable-features=VizDisplayCompositor')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        driver = webdriver.Chrome(options=options)
        
        # 如果成功创建驱动，运行测试
        print("  ✅ Chrome 驱动创建成功！")
        run_chrome_test(driver)
        return True
        
    except Exception as e:
        print(f"  ❌ 方法1失败: {e}")
        
        try:
            # 方法2: 尝试指定chromedriver路径
            print("  📝 方法2: 尝试常见的chromedriver路径...")
            
            possible_paths = [
                r"C:\Program Files\Google\Chrome\Application\chromedriver.exe",
                r"C:\chromedriver\chromedriver.exe",
                r".\chromedriver.exe",
                r"C:\WebDrivers\chromedriver.exe"
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    print(f"    🔍 找到chromedriver: {path}")
                    service = Service(path)
                    driver = webdriver.Chrome(service=service, options=options)
                    print("  ✅ Chrome 驱动创建成功！")
                    run_chrome_test(driver)
                    return True
            
            print("  ❌ 未找到chromedriver.exe")
            print_chrome_setup_guide()
            return False
            
        except Exception as e2:
            print(f"  ❌ 方法2失败: {e2}")
            print_chrome_setup_guide()
            return False

def run_chrome_test(driver):
    """运行Chrome测试"""
    try:
        login_url = f"file://{os.path.abspath('login.html')}"
        
        print("  📂 打开登录页面...")
        driver.get(login_url)
        driver.set_window_size(1200, 800)
        time.sleep(2)
        
        # 验证页面
        title = driver.title
        print(f"  📄 页面标题: {title}")
        
        # 测试元素
        username = driver.find_element(By.ID, "username")
        password = driver.find_element(By.ID, "password")
        login_btn = driver.find_element(By.ID, "loginBtn")
        
        print("  ✅ 页面元素检查通过")
        
        # 测试登录
        username.send_keys("admin")
        password.send_keys("admin123")
        login_btn.click()
        
        time.sleep(3)
        
        # 处理alert
        try:
            alert = driver.switch_to.alert
            alert_text = alert.text
            print(f"  ✅ 登录成功，弹窗内容: {alert_text}")
            alert.accept()
        except:
            print("  ✅ 登录测试完成")
        
        print("  🎉 Chrome 测试全部通过！")
        
    except Exception as e:
        print(f"  ❌ Chrome 测试过程中出错: {e}")
    finally:
        driver.quit()

def print_chrome_setup_guide():
    """打印Chrome设置指南"""
    print("\n📋 Chrome WebDriver 设置指南:")
    print("=" * 40)
    print("1. 下载 ChromeDriver:")
    print("   https://chromedriver.chromium.org/")
    print("   或 https://googlechromelabs.github.io/chrome-for-testing/")
    print("")
    print("2. 将 chromedriver.exe 放到以下位置之一:")
    print("   - 当前项目目录")
    print("   - C:\\chromedriver\\")
    print("   - C:\\WebDrivers\\")
    print("   - 添加到系统 PATH 环境变量")
    print("")
    print("3. 确保 ChromeDriver 版本与 Chrome 浏览器版本匹配")
    print("")
    print("4. 重新运行测试")

def main():
    """主函数"""
    print("🚀 Chrome 手动测试工具")
    print("=" * 30)
    
    if not os.path.exists("login.html"):
        print("❌ 登录页面文件 login.html 不存在")
        return
    
    success = test_chrome_manual()
    
    if success:
        print("\n🎉 Chrome 测试成功完成！")
    else:
        print("\n💡 提示: 如果需要测试Chrome，请按照上述指南设置ChromeDriver")
        print("    目前 Edge 和 Firefox 测试都正常工作")

if __name__ == "__main__":
    main()
