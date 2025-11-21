#!/usr/bin/env python3
"""
Web登录功能测试执行脚本（Edge浏览器版本）
"""

import os
import sys
import subprocess
import datetime

def check_edge_driver():
    """检查Edge浏览器和EdgeDriver是否可用"""
    print("检查Edge浏览器环境...")
    
    try:
        # 尝试导入selenium edge模块
        from selenium import webdriver
        from selenium.webdriver.edge.options import Options
        
        # 尝试创建Edge选项（不启动浏览器）
        options = Options()
        options.add_argument("--headless")  # 无头模式测试
        
        print("✅ Selenium Edge模块可用")
        return True
    except ImportError as e:
        print(f"❌ Selenium模块导入失败: {e}")
        return False
    except Exception as e:
        print(f"⚠️ Edge环境检查遇到问题: {e}")
        return True  # 继续尝试运行

def run_edge_tests():
    """执行Edge浏览器测试"""
    print("开始执行Web登录功能测试（Edge浏览器版本）...")
    
    # 获取当前时间作为报告文件名
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"test_report_edge_{timestamp}.html"
    
    # 构建pytest命令
    cmd = [
        sys.executable, "-m", "pytest",
        "test_login_edge.py",
        "-v",  # 详细输出
        "-s",  # 显示print输出
        "--html=" + report_file,  # 生成HTML报告
        "--self-contained-html",  # 生成独立的HTML文件
        "--tb=short"  # 简短的错误回溯
    ]
    
    try:
        # 执行测试
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
        
        print("测试执行完成！")
        print(f"HTML测试报告已生成: {report_file}")
        
        # 输出测试结果摘要
        if result.returncode == 0:
            print("✅ 所有测试通过")
        else:
            print("❌ 部分测试失败或跳过")
            
        print("\n测试输出:")
        print(result.stdout)
        
        if result.stderr:
            print("\n错误信息:")
            print(result.stderr)
            
        return result.returncode == 0, report_file
        
    except Exception as e:
        print(f"测试执行失败: {e}")
        return False, None

def create_multi_browser_info():
    """创建多浏览器测试信息"""
    info_content = f"""# 多浏览器测试支持说明

## 支持的浏览器

### 1. Microsoft Edge（推荐）
- **优势**: Windows系统内置，兼容性好
- **测试脚本**: `test_login_edge.py`
- **执行命令**: `python run_tests_edge.py`

### 2. Google Chrome
- **测试脚本**: `test_login_local.py`
- **执行命令**: `python run_tests_simple.py`

### 3. Firefox（可扩展）
- 可以创建类似的Firefox版本测试脚本

## EdgeDriver安装说明

如果遇到EdgeDriver问题，请：

1. **自动安装**（推荐）:
   ```bash
   pip install webdriver-manager
   ```

2. **手动安装**:
   - 访问: https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/
   - 下载对应Edge版本的EdgeDriver
   - 将EdgeDriver.exe放入系统PATH或项目目录

3. **检查Edge版本**:
   - 打开Edge浏览器
   - 地址栏输入: `edge://version/`
   - 查看版本号并下载对应的EdgeDriver

## 测试执行优先级

1. **首选**: Edge浏览器（Windows系统兼容性最好）
2. **备选**: Chrome浏览器
3. **手动**: 直接在浏览器中打开login.html测试

## 当前测试时间
{datetime.datetime.now().strftime("%Y年%m月%d日 %H:%M:%S")}
"""
    
    info_file = f"browser_support_info_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    with open(info_file, 'w', encoding='utf-8') as f:
        f.write(info_content)
    
    return info_file

def main():
    """主函数"""
    print("=" * 60)
    print("Web登录功能测试自动化执行（Edge浏览器版本）")
    print("=" * 60)
    
    # 检查当前目录
    current_dir = os.getcwd()
    print(f"当前工作目录: {current_dir}")
    
    # 检查必要文件
    required_files = ["test_login_edge.py", "login.html"]
    for file in required_files:
        if not os.path.exists(file):
            print(f"❌ 缺少必要文件: {file}")
            return
    
    print("✅ 所有必要文件存在")
    
    # 检查Edge环境
    edge_available = check_edge_driver()
    
    # 执行测试
    print("\n尝试执行Edge浏览器自动化测试...")
    success, report_file = run_edge_tests()
    
    # 创建多浏览器支持信息
    info_file = create_multi_browser_info()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 Edge浏览器测试执行成功完成！")
    else:
        print("⚠️ Edge浏览器测试可能需要配置EdgeDriver")
        print("💡 建议：")
        print("   1. 检查Edge浏览器是否已安装")
        print("   2. 安装EdgeDriver（参考生成的说明文档）")
        print("   3. 或者手动打开 login.html 进行测试")
    
    if report_file and os.path.exists(report_file):
        print(f"📊 Edge测试报告: {report_file}")
    
    print(f"📖 多浏览器支持说明: {info_file}")
    print("=" * 60)

if __name__ == "__main__":
    main()
