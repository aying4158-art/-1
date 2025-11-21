"""
使用 requests 库演示订单系统 API 调用
完整的订单流程演示
"""

import requests
import json
import time

# API 基础地址
BASE_URL = "http://localhost:8000"

def print_response(response, title):
    """打印响应结果"""
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")
    print(f"状态码: {response.status_code}")
    try:
        result = response.json()
        print(f"响应内容: {json.dumps(result, indent=2, ensure_ascii=False)}")
    except:
        print(f"响应内容: {response.text}")
    print(f"{'='*60}")

def demo_complete_order_flow():
    """演示完整的订单流程"""
    print("🚀 开始演示完整的订单系统流程")
    
    # 1. 健康检查
    print("\n📋 步骤 1: 健康检查")
    response = requests.get(f"{BASE_URL}/")
    print_response(response, "健康检查")
    
    # 2. 添加商品库存
    print("\n📦 步骤 2: 添加商品库存")
    products = [
        {"product_id": "P001", "quantity": 100},
        {"product_id": "P002", "quantity": 50},
        {"product_id": "P003", "quantity": 200}
    ]
    
    for product in products:
        response = requests.post(
            f"{BASE_URL}/api/inventory/products",
            json=product
        )
        print_response(response, f"添加商品 {product['product_id']}")
    
    # 3. 查询库存
    print("\n📊 步骤 3: 查询库存")
    response = requests.get(f"{BASE_URL}/api/inventory/products")
    print_response(response, "查询所有库存")
    
    # 4. 创建订单
    print("\n📋 步骤 4: 创建订单")
    order_data = {
        "order_id": "ORD001",
        "customer_id": "CUST001"
    }
    response = requests.post(
        f"{BASE_URL}/api/orders",
        json=order_data
    )
    print_response(response, "创建订单")
    
    # 5. 添加订单项
    print("\n🛒 步骤 5: 添加订单项")
    order_items = [
        {"product_id": "P001", "quantity": 2, "price": 50.0},
        {"product_id": "P002", "quantity": 1, "price": 100.0}
    ]
    
    for item in order_items:
        response = requests.post(
            f"{BASE_URL}/api/orders/ORD001/items",
            json=item
        )
        print_response(response, f"添加订单项 {item['product_id']}")
    
    # 6. 查询订单详情
    print("\n📄 步骤 6: 查询订单详情")
    response = requests.get(f"{BASE_URL}/api/orders/ORD001")
    print_response(response, "查询订单详情")
    
    # 7. 确认订单（预留库存）
    print("\n✅ 步骤 7: 确认订单")
    response = requests.post(f"{BASE_URL}/api/orders/ORD001/confirm")
    print_response(response, "确认订单")
    
    # 8. 查看库存变化
    print("\n📊 步骤 8: 查看库存变化")
    response = requests.get(f"{BASE_URL}/api/inventory/products")
    print_response(response, "确认后的库存状态")
    
    # 9. 处理支付
    print("\n💳 步骤 9: 处理支付")
    payment_data = {"payment_method": "alipay"}
    response = requests.post(
        f"{BASE_URL}/api/orders/ORD001/payment",
        json=payment_data
    )
    print_response(response, "处理支付")
    
    # 10. 发货
    print("\n🚚 步骤 10: 发货")
    response = requests.post(f"{BASE_URL}/api/orders/ORD001/ship")
    print_response(response, "订单发货")
    
    # 11. 完成订单
    print("\n🎉 步骤 11: 完成订单")
    response = requests.post(f"{BASE_URL}/api/orders/ORD001/complete")
    print_response(response, "完成订单")
    
    # 12. 查看最终状态
    print("\n📊 步骤 12: 查看最终状态")
    response = requests.get(f"{BASE_URL}/api/orders/ORD001")
    print_response(response, "最终订单状态")

def demo_error_handling():
    """演示错误处理"""
    print("\n🚨 演示错误处理")
    
    # 1. 库存不足
    print("\n❌ 测试库存不足")
    order_data = {"order_id": "ORD002", "customer_id": "CUST002"}
    requests.post(f"{BASE_URL}/api/orders", json=order_data)
    
    # 添加超出库存的订单项
    item_data = {"product_id": "P001", "quantity": 1000, "price": 50.0}
    response = requests.post(f"{BASE_URL}/api/orders/ORD002/items", json=item_data)
    print_response(response, "添加大量订单项")
    
    # 尝试确认订单
    response = requests.post(f"{BASE_URL}/api/orders/ORD002/confirm")
    print_response(response, "确认库存不足的订单")
    
    # 2. 重复订单ID
    print("\n❌ 测试重复订单ID")
    response = requests.post(f"{BASE_URL}/api/orders", json=order_data)
    print_response(response, "创建重复订单ID")

def demo_payment_methods():
    """演示不同支付方式"""
    print("\n💳 演示不同支付方式")
    
    payment_methods = ["credit_card", "debit_card", "alipay", "wechat", "paypal"]
    
    for i, method in enumerate(payment_methods, 1):
        order_id = f"ORD00{i+2}"
        
        # 创建订单
        order_data = {"order_id": order_id, "customer_id": f"CUST00{i+2}"}
        requests.post(f"{BASE_URL}/api/orders", json=order_data)
        
        # 添加订单项
        item_data = {"product_id": "P003", "quantity": 1, "price": 30.0}
        requests.post(f"{BASE_URL}/api/orders/{order_id}/items", json=item_data)
        
        # 确认订单
        requests.post(f"{BASE_URL}/api/orders/{order_id}/confirm")
        
        # 使用不同支付方式
        payment_data = {"payment_method": method}
        response = requests.post(f"{BASE_URL}/api/orders/{order_id}/payment", json=payment_data)
        print_response(response, f"使用 {method} 支付")

def main():
    """主函数"""
    print("🎯 订单系统 API 调用演示")
    print("=" * 80)
    
    try:
        # 检查服务器是否运行
        response = requests.get(f"{BASE_URL}/", timeout=5)
        if response.status_code != 200:
            print("❌ 服务器未正常运行，请先启动服务器")
            return
    except requests.exceptions.RequestException:
        print("❌ 无法连接到服务器，请确保服务器在 http://localhost:8000 运行")
        return
    
    # 清空数据
    print("\n🧹 清空测试数据")
    try:
        requests.delete(f"{BASE_URL}/api/test/clear-data")
    except:
        pass
    
    # 演示完整流程
    demo_complete_order_flow()
    
    # 演示错误处理
    demo_error_handling()
    
    # 演示不同支付方式
    demo_payment_methods()
    
    print("\n🎉 演示完成！")
    print("你可以访问以下地址查看API文档：")
    print(f"  - Swagger UI: {BASE_URL}/docs")
    print(f"  - ReDoc: {BASE_URL}/redoc")

if __name__ == "__main__":
    main()
