#!/usr/bin/env python3
"""
Web登录功能测试执行脚本
"""

import os
import sys
import subprocess
import datetime

def install_requirements():
    """安装依赖包"""
    print("正在安装测试依赖...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("依赖安装完成！")
        return True
    except subprocess.CalledProcessError as e:
        print(f"依赖安装失败: {e}")
        return False

def run_tests():
    """执行测试"""
    print("开始执行Web登录功能测试...")
    
    # 获取当前时间作为报告文件名
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"test_report_{timestamp}.html"
    
    # 构建pytest命令
    cmd = [
        sys.executable, "-m", "pytest",
        "test_login.py",
        "-v",  # 详细输出
        "--html=" + report_file,  # 生成HTML报告
        "--self-contained-html",  # 生成独立的HTML文件
        "--tb=short"  # 简短的错误回溯
    ]
    
    try:
        # 执行测试
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        print("测试执行完成！")
        print(f"HTML测试报告已生成: {report_file}")
        
        # 输出测试结果摘要
        if result.returncode == 0:
            print("✅ 所有测试通过")
        else:
            print("❌ 部分测试失败")
            
        print("\n测试输出:")
        print(result.stdout)
        
        if result.stderr:
            print("\n错误信息:")
            print(result.stderr)
            
        return result.returncode == 0, report_file
        
    except Exception as e:
        print(f"测试执行失败: {e}")
        return False, None

def main():
    """主函数"""
    print("=" * 60)
    print("Web登录功能测试自动化执行")
    print("=" * 60)
    
    # 检查当前目录
    current_dir = os.getcwd()
    print(f"当前工作目录: {current_dir}")
    
    # 检查必要文件
    required_files = ["test_login.py", "login.html", "requirements.txt"]
    for file in required_files:
        if not os.path.exists(file):
            print(f"❌ 缺少必要文件: {file}")
            return
    
    print("✅ 所有必要文件存在")
    
    # 安装依赖
    if not install_requirements():
        print("❌ 依赖安装失败，测试终止")
        return
    
    # 执行测试
    success, report_file = run_tests()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 测试执行成功完成！")
    else:
        print("⚠️ 测试执行完成，但有部分测试失败")
    
    if report_file and os.path.exists(report_file):
        print(f"📊 详细测试报告: {report_file}")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
