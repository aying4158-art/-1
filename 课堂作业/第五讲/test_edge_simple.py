#!/usr/bin/env python3
"""
简单的Edge浏览器测试脚本
"""

import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.edge.options import Options

def test_login_with_edge():
    """使用Edge浏览器测试登录功能"""
    print("🚀 开始Edge浏览器测试...")
    
    # 配置Edge选项
    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    driver = None
    test_results = []
    
    try:
        # 启动Edge浏览器
        print("启动Edge浏览器...")
        driver = webdriver.Edge(options=options)
        driver.maximize_window()
        print("✅ Edge浏览器启动成功！")
        
        # 打开登录页面
        current_dir = os.path.dirname(os.path.abspath(__file__))
        login_page = os.path.join(current_dir, "login.html")
        driver.get(f"file:///{login_page}")
        print(f"📄 已打开登录页面: {login_page}")
        
        # 等待页面加载
        time.sleep(2)
        
        # 测试1: 正常登录
        print("\n🧪 测试1: 正常登录")
        driver.refresh()
        time.sleep(1)
        
        username_field = driver.find_element(By.ID, "username")
        password_field = driver.find_element(By.ID, "password")
        login_button = driver.find_element(By.ID, "loginBtn")
        
        username_field.clear()
        password_field.clear()
        username_field.send_keys("admin")
        password_field.send_keys("password123")
        login_button.click()
        
        try:
            success_message = WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located((By.ID, "successMessage"))
            )
            if "登录成功" in success_message.text:
                print("✅ 正常登录测试 - 通过")
                test_results.append("TC001 正常登录: 通过")
            else:
                print("❌ 正常登录测试 - 失败")
                test_results.append("TC001 正常登录: 失败")
        except Exception as e:
            print(f"❌ 正常登录测试 - 异常: {e}")
            test_results.append("TC001 正常登录: 异常")
        
        # 测试2: 用户名为空
        print("\n🧪 测试2: 用户名为空")
        driver.refresh()
        time.sleep(1)
        
        password_field = driver.find_element(By.ID, "password")
        login_button = driver.find_element(By.ID, "loginBtn")
        
        password_field.clear()
        password_field.send_keys("password123")
        login_button.click()
        
        try:
            error_message = WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located((By.ID, "errorMessage"))
            )
            if "请输入用户名" in error_message.text:
                print("✅ 用户名为空测试 - 通过")
                test_results.append("TC002 用户名为空: 通过")
            else:
                print("❌ 用户名为空测试 - 失败")
                test_results.append("TC002 用户名为空: 失败")
        except Exception as e:
            print(f"❌ 用户名为空测试 - 异常: {e}")
            test_results.append("TC002 用户名为空: 异常")
        
        # 测试3: 密码为空
        print("\n🧪 测试3: 密码为空")
        driver.refresh()
        time.sleep(1)
        
        username_field = driver.find_element(By.ID, "username")
        login_button = driver.find_element(By.ID, "loginBtn")
        
        username_field.clear()
        username_field.send_keys("admin")
        login_button.click()
        
        try:
            error_message = WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located((By.ID, "errorMessage"))
            )
            if "请输入密码" in error_message.text:
                print("✅ 密码为空测试 - 通过")
                test_results.append("TC003 密码为空: 通过")
            else:
                print("❌ 密码为空测试 - 失败")
                test_results.append("TC003 密码为空: 失败")
        except Exception as e:
            print(f"❌ 密码为空测试 - 异常: {e}")
            test_results.append("TC003 密码为空: 异常")
        
        # 测试4: 错误凭据
        print("\n🧪 测试4: 错误凭据")
        driver.refresh()
        time.sleep(1)
        
        username_field = driver.find_element(By.ID, "username")
        password_field = driver.find_element(By.ID, "password")
        login_button = driver.find_element(By.ID, "loginBtn")
        
        username_field.clear()
        password_field.clear()
        username_field.send_keys("wronguser")
        password_field.send_keys("wrongpass")
        login_button.click()
        
        try:
            error_message = WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located((By.ID, "errorMessage"))
            )
            if "用户名或密码错误" in error_message.text:
                print("✅ 错误凭据测试 - 通过")
                test_results.append("TC004 错误凭据: 通过")
            else:
                print("❌ 错误凭据测试 - 失败")
                test_results.append("TC004 错误凭据: 失败")
        except Exception as e:
            print(f"❌ 错误凭据测试 - 异常: {e}")
            test_results.append("TC004 错误凭据: 异常")
        
        # 测试5: 页面元素检查
        print("\n🧪 测试5: 页面元素检查")
        driver.refresh()
        time.sleep(1)
        
        try:
            username_field = driver.find_element(By.ID, "username")
            password_field = driver.find_element(By.ID, "password")
            login_button = driver.find_element(By.ID, "loginBtn")
            
            # 检查元素是否可见
            if (username_field.is_displayed() and 
                password_field.is_displayed() and 
                login_button.is_displayed()):
                print("✅ 页面元素检查 - 通过")
                test_results.append("TC005 页面元素: 通过")
            else:
                print("❌ 页面元素检查 - 失败")
                test_results.append("TC005 页面元素: 失败")
        except Exception as e:
            print(f"❌ 页面元素检查 - 异常: {e}")
            test_results.append("TC005 页面元素: 异常")
        
        print("\n" + "="*50)
        print("🎉 Edge浏览器测试完成！")
        print("="*50)
        
        # 显示测试结果汇总
        print("\n📊 测试结果汇总:")
        passed = 0
        for result in test_results:
            print(f"  {result}")
            if "通过" in result:
                passed += 1
        
        print(f"\n✅ 通过: {passed}/{len(test_results)} 个测试用例")
        
        # 保持浏览器打开几秒钟以便查看
        print("\n浏览器将在5秒后关闭...")
        time.sleep(5)
        
    except Exception as e:
        print(f"❌ Edge浏览器测试失败: {e}")
        print("💡 可能的原因:")
        print("  1. Edge浏览器未安装")
        print("  2. EdgeDriver未安装或版本不匹配")
        print("  3. 系统权限问题")
        
    finally:
        if driver:
            driver.quit()
            print("🔚 Edge浏览器已关闭")

if __name__ == "__main__":
    test_login_with_edge()
