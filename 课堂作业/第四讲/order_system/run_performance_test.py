"""
快速运行性能测试的脚本
"""

import subprocess
import sys
import time
import requests

def check_server():
    """检查服务器是否运行"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def run_performance_test():
    """运行性能测试"""
    print("🚀 订单系统性能测试")
    print("=" * 60)
    
    # 检查服务器
    if not check_server():
        print("❌ 服务器未运行，请先启动服务器:")
        print("   python run_server.py")
        return
    
    print("✅ 服务器运行正常")
    print("\n📊 测试配置:")
    print("   - 并发用户数: 100")
    print("   - 用户增长速率: 10用户/秒")
    print("   - 测试时长: 60秒")
    print("   - 目标接口: /api/orders")
    
    print("\n🔄 开始性能测试...")
    print("=" * 60)
    
    # 运行 Locust 测试
    cmd = [
        "locust",
        "-f", "order_load_test.py",
        "--host=http://localhost:8000",
        "--users", "100",
        "--spawn-rate", "10",
        "--run-time", "60s",
        "--headless",
        "--html", "performance_report.html"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        print("✅ 测试完成!")
        print("\n📈 测试结果:")
        print(result.stdout)
        
        if result.stderr:
            print("\n⚠️ 警告信息:")
            print(result.stderr)
            
        print("\n📄 报告文件:")
        print("   - HTML报告: performance_report.html")
        print("   - 详细分析: performance_test_report.md")
        
    except subprocess.TimeoutExpired:
        print("❌ 测试超时")
    except Exception as e:
        print(f"❌ 测试失败: {e}")

def run_quick_test():
    """运行快速测试（30秒）"""
    print("⚡ 快速性能测试 (30秒)")
    print("=" * 40)
    
    if not check_server():
        print("❌ 服务器未运行")
        return
    
    cmd = [
        "locust",
        "-f", "order_load_test.py",
        "--host=http://localhost:8000",
        "--users", "50",
        "--spawn-rate", "5",
        "--run-time", "30s",
        "--headless"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        print("✅ 快速测试完成!")
        print(result.stdout)
    except Exception as e:
        print(f"❌ 测试失败: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "quick":
        run_quick_test()
    else:
        run_performance_test()
