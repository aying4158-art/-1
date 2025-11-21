#!/usr/bin/env python3
"""
CI配置验证脚本
用于验证GitHub Actions配置是否符合要求
"""

import os
import yaml
import sys

def check_file_exists(filepath, description):
    """检查文件是否存在"""
    if os.path.exists(filepath):
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description}: {filepath} (文件不存在)")
        return False

def check_yaml_syntax(filepath):
    """检查YAML语法"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            yaml.safe_load(f)
        print(f"✅ YAML语法正确: {filepath}")
        return True
    except yaml.YAMLError as e:
        print(f"❌ YAML语法错误: {filepath} - {e}")
        return False
    except Exception as e:
        print(f"❌ 文件读取错误: {filepath} - {e}")
        return False

def check_ci_config():
    """检查CI配置内容"""
    ci_file = '.github/workflows/python-test.yml'
    
    if not os.path.exists(ci_file):
        print(f"❌ CI配置文件不存在: {ci_file}")
        return False
    
    try:
        with open(ci_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        checks = []
        
        # 检查基本结构
        checks.append(('name' in config, "工作流名称 (name)"))
        
        # 检查触发条件 (处理YAML中on关键字的问题)
        on_key = 'on' if 'on' in config else True if True in config else None
        has_on = on_key is not None
        checks.append((has_on, "触发条件 (on)"))
        checks.append(('jobs' in config, "作业定义 (jobs)"))
        
        # 检查触发条件内容
        if has_on:
            on_config = config[on_key]
            is_push_trigger = (
                on_config == ['push'] or 
                on_config == 'push' or 
                (isinstance(on_config, list) and 'push' in on_config) or
                (isinstance(on_config, dict) and 'push' in on_config)
            )
            checks.append((is_push_trigger, "推送触发 (on: [push])"))
        
        # 检查作业配置
        if 'jobs' in config and 'test' in config['jobs']:
            job = config['jobs']['test']
            checks.append(('runs-on' in job, "运行环境 (runs-on)"))
            checks.append(('steps' in job, "执行步骤 (steps)"))
            
            if 'runs-on' in job:
                checks.append((job['runs-on'] == 'ubuntu-latest', "Ubuntu环境"))
            
            # 检查步骤
            if 'steps' in job:
                steps = job['steps']
                step_checks = [
                    (any('checkout' in str(step.get('uses', '')) for step in steps), "代码检出步骤"),
                    (any('setup-python' in str(step.get('uses', '')) for step in steps), "Python环境设置"),
                    (any('pip install' in str(step.get('run', '')) for step in steps), "依赖安装"),
                    (any('pytest' in str(step.get('run', '')) for step in steps), "pytest测试"),
                    (any('--html=report.html' in str(step.get('run', '')) for step in steps), "HTML报告生成"),
                ]
                checks.extend(step_checks)
        
        # 输出检查结果
        all_passed = True
        for passed, description in checks:
            if passed:
                print(f"✅ {description}")
            else:
                print(f"❌ {description}")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"❌ CI配置检查失败: {e}")
        return False

def main():
    """主验证函数"""
    print("🔍 CI配置验证开始...")
    print("=" * 50)
    
    score = 0
    total_checks = 0
    
    # 检查文件存在性
    files_to_check = [
        ('.github/workflows/python-test.yml', 'GitHub Actions配置文件'),
        ('requirements.txt', '依赖文件'),
        ('checkout_service.py', '服务模块'),
        ('simple_pytest.py', 'pytest测试文件'),
    ]
    
    print("\n📁 文件存在性检查:")
    for filepath, description in files_to_check:
        if check_file_exists(filepath, description):
            score += 1
        total_checks += 1
    
    # 检查YAML语法
    print("\n📝 YAML语法检查:")
    if check_yaml_syntax('.github/workflows/python-test.yml'):
        score += 1
    total_checks += 1
    
    # 检查CI配置内容
    print("\n⚙️ CI配置内容检查:")
    if check_ci_config():
        score += 5  # CI配置权重更高
    total_checks += 5
    
    # 计算得分
    print("\n" + "=" * 50)
    print(f"📊 验证结果: {score}/{total_checks}")
    percentage = (score / total_checks) * 100
    print(f"📈 完成度: {percentage:.1f}%")
    
    if percentage >= 90:
        print("🎉 优秀! CI配置完全符合要求!")
        grade = "A"
    elif percentage >= 80:
        print("👍 良好! CI配置基本符合要求!")
        grade = "B"
    elif percentage >= 70:
        print("📝 中等! CI配置需要一些改进!")
        grade = "C"
    else:
        print("⚠️ 需要改进! CI配置存在问题!")
        grade = "D"
    
    print(f"🏆 评级: {grade}")
    
    return score == total_checks

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
