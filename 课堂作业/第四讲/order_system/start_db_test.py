"""
启动数据库连接测试服务
"""

import subprocess
import sys
import time
import requests


def check_dependencies():
    """检查依赖"""
    try:
        import flask
        print("✅ Flask 已安装")
    except ImportError:
        print("❌ Flask 未安装，请运行: pip install flask")
        return False
    
    try:
        import requests
        print("✅ Requests 已安装")
    except ImportError:
        print("❌ Requests 未安装，请运行: pip install requests")
        return False
    
    return True


def start_server():
    """启动Flask服务"""
    print("启动Flask数据库连接测试服务...")
    
    try:
        # 启动Flask应用
        subprocess.run([sys.executable, "flask_db_test_app.py"], check=True)
    except KeyboardInterrupt:
        print("\n服务已停止")
    except Exception as e:
        print(f"启动服务时出错: {e}")


def main():
    print("=" * 50)
    print("数据库连接中断测试系统")
    print("=" * 50)
    
    # 检查依赖
    if not check_dependencies():
        return
    
    print("\n测试说明:")
    print("1. 此系统模拟订单支付过程中的数据库连接中断")
    print("2. 测试Flask服务的错误处理和恢复能力")
    print("3. 服务将在 http://localhost:5000 启动")
    print("4. 使用 test_db_connection_failure.py 运行自动化测试")
    
    print("\n手动测试步骤:")
    print("1. POST /api/test/init-data - 初始化测试数据")
    print("2. POST /api/orders - 创建订单")
    print("3. POST /api/orders/{order_id}/items - 添加商品")
    print("4. POST /api/orders/{order_id}/confirm - 确认订单")
    print("5. POST /api/database/disconnect - 断开数据库连接")
    print("6. POST /api/orders/{order_id}/payment - 尝试支付（应该失败）")
    print("7. POST /api/database/connect - 恢复数据库连接")
    print("8. POST /api/orders/{order_id}/payment - 再次支付（应该成功）")
    
    input("\n按回车键启动服务...")
    start_server()


if __name__ == "__main__":
    main()
