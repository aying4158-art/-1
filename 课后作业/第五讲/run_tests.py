#!/usr/bin/env python3
"""
测试运行脚本
提供便捷的测试运行和报告生成功能
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path


def run_command(command, description):
    """运行命令并处理结果"""
    print(f"\n{'='*60}")
    print(f"正在执行: {description}")
    print(f"命令: {command}")
    print('='*60)
    
    try:
        result = subprocess.run(command, shell=True, check=True, 
                              capture_output=False, text=True)
        print(f"✅ {description} 完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} 失败: {e}")
        return False


def create_directories():
    """创建必要的目录"""
    directories = ['reports', 'htmlcov']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"📁 创建目录: {directory}")


def run_tests(args):
    """运行测试"""
    create_directories()
    
    success = True
    
    if args.basic or args.all:
        # 基本测试
        success &= run_command("pytest tests/ -v", "基本单元测试")
    
    if args.coverage or args.all:
        # 覆盖率测试
        success &= run_command(
            "pytest tests/ --cov=src --cov-report=html --cov-report=term-missing --cov-report=xml -v",
            "测试覆盖率分析"
        )
    
    if args.pylint or args.all:
        # 代码质量检查
        success &= run_command("pylint src/ --output-format=text", "代码质量检查")
    
    if args.html_report or args.all:
        # 生成HTML测试报告
        success &= run_command(
            "pytest tests/ --html=reports/pytest_report.html --self-contained-html -v",
            "生成HTML测试报告"
        )
    
    return success


def open_reports():
    """打开测试报告"""
    reports = {
        'HTML测试报告': 'reports/pytest_report.html',
        'HTML覆盖率报告': 'htmlcov/index.html'
    }
    
    for name, path in reports.items():
        if os.path.exists(path):
            print(f"📊 {name}: {os.path.abspath(path)}")
            if sys.platform.startswith('win'):
                os.startfile(os.path.abspath(path))
            elif sys.platform.startswith('darwin'):
                subprocess.run(['open', os.path.abspath(path)])
            else:
                subprocess.run(['xdg-open', os.path.abspath(path)])
        else:
            print(f"⚠️  {name} 不存在: {path}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='Python单元测试项目测试运行器')
    
    parser.add_argument('--basic', action='store_true', help='运行基本测试')
    parser.add_argument('--coverage', action='store_true', help='运行覆盖率测试')
    parser.add_argument('--pylint', action='store_true', help='运行代码质量检查')
    parser.add_argument('--html-report', action='store_true', help='生成HTML报告')
    parser.add_argument('--all', action='store_true', help='运行所有测试和检查')
    parser.add_argument('--open-reports', action='store_true', help='打开测试报告')
    
    args = parser.parse_args()
    
    # 如果没有指定参数，默认运行所有测试
    if not any([args.basic, args.coverage, args.pylint, args.html_report, args.all, args.open_reports]):
        args.all = True
    
    print("🚀 Python单元测试项目测试运行器")
    print(f"📂 工作目录: {os.getcwd()}")
    
    if args.open_reports:
        open_reports()
        return
    
    # 检查依赖
    try:
        import pytest
        import coverage
        import pylint
        print("✅ 所有依赖已安装")
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        print("请运行: pip install -r requirements.txt")
        sys.exit(1)
    
    # 运行测试
    success = run_tests(args)
    
    if success:
        print("\n🎉 所有测试和检查都成功完成！")
        print("\n📊 查看报告:")
        print("   - HTML测试报告: reports/pytest_report.html")
        print("   - HTML覆盖率报告: htmlcov/index.html")
        print("   - XML覆盖率报告: coverage.xml")
        
        # 询问是否打开报告
        try:
            if input("\n是否打开测试报告? (y/N): ").lower().startswith('y'):
                open_reports()
        except KeyboardInterrupt:
            print("\n👋 再见！")
    else:
        print("\n❌ 部分测试或检查失败，请查看上面的错误信息")
        sys.exit(1)


if __name__ == "__main__":
    main()
