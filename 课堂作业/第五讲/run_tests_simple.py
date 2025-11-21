#!/usr/bin/env python3
"""
Web登录功能测试执行脚本（简化版本）
"""

import os
import sys
import subprocess
import datetime

def run_simple_tests():
    """执行简化版测试（不需要下载ChromeDriver）"""
    print("开始执行Web登录功能测试（简化版本）...")
    
    # 获取当前时间作为报告文件名
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"test_report_simple_{timestamp}.html"
    
    # 构建pytest命令
    cmd = [
        sys.executable, "-m", "pytest",
        "test_login_local.py",
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

def create_manual_test_report():
    """创建手动测试报告模板"""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"manual_test_report_{timestamp}.md"
    
    report_content = f"""# Web登录功能测试报告

## 测试概述
- **测试时间**: {datetime.datetime.now().strftime("%Y年%m月%d日 %H:%M:%S")}
- **测试人员**: 测试工程师
- **测试环境**: Windows + Chrome浏览器
- **被测系统**: Web登录功能

## 测试结果汇总
| 测试用例ID | 测试用例名称 | 执行结果 | 备注 |
|-----------|-------------|----------|------|
| TC001 | 正常登录测试 | ⏳ 待执行 | |
| TC002 | 用户名为空测试 | ⏳ 待执行 | |
| TC003 | 密码为空测试 | ⏳ 待执行 | |
| TC004 | 用户名和密码都为空测试 | ⏳ 待执行 | |
| TC005 | 错误用户名测试 | ⏳ 待执行 | |
| TC006 | 错误密码测试 | ⏳ 待执行 | |
| TC007 | SQL注入测试 | ⏳ 待执行 | |
| TC008 | 密码显示隐藏测试 | ⏳ 待执行 | |
| TC009 | 登录按钮状态测试 | ⏳ 待执行 | |
| TC010 | 页面元素存在性测试 | ⏳ 待执行 | |

## 手动测试步骤

### 1. 打开登录页面
1. 在浏览器中打开 `login.html` 文件
2. 验证页面正常显示

### 2. 执行各项测试用例
按照 `test_cases.md` 中的测试用例逐一执行

### 3. 记录测试结果
- ✅ 通过
- ❌ 失败
- ⚠️ 部分通过
- ⏳ 待执行

## 缺陷记录
（如发现缺陷，请在此记录）

## 测试结论
（测试完成后填写）

## 改进建议
（如有改进建议，请在此记录）
"""
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    return report_file

def main():
    """主函数"""
    print("=" * 60)
    print("Web登录功能测试自动化执行（简化版本）")
    print("=" * 60)
    
    # 检查当前目录
    current_dir = os.getcwd()
    print(f"当前工作目录: {current_dir}")
    
    # 检查必要文件
    required_files = ["test_login_local.py", "login.html"]
    for file in required_files:
        if not os.path.exists(file):
            print(f"❌ 缺少必要文件: {file}")
            return
    
    print("✅ 所有必要文件存在")
    
    # 尝试执行自动化测试
    print("\n尝试执行自动化测试...")
    success, report_file = run_simple_tests()
    
    # 创建手动测试报告模板
    manual_report = create_manual_test_report()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 自动化测试执行成功完成！")
    else:
        print("⚠️ 自动化测试可能需要手动配置浏览器驱动")
        print("💡 建议：手动打开 login.html 进行测试")
    
    if report_file and os.path.exists(report_file):
        print(f"📊 自动化测试报告: {report_file}")
    
    print(f"📝 手动测试报告模板: {manual_report}")
    print("=" * 60)

if __name__ == "__main__":
    main()
