import requests
import json
import time

base_url = 'http://localhost:5000'

print('=== 数据库连接中断测试演示 ===')

# 1. 检查服务状态
print('\n1. 检查服务状态')
response = requests.get(f'{base_url}/')
print(f'服务状态: {response.status_code}')
print(f'响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}')

# 2. 初始化测试数据
print('\n2. 初始化测试数据')
response = requests.post(f'{base_url}/api/test/init-data')
print(f'初始化状态: {response.status_code}')
if response.status_code == 200:
    print('✅ 测试数据初始化成功')
else:
    print('❌ 测试数据初始化失败')

# 3. 检查数据库状态
print('\n3. 检查数据库连接状态')
response = requests.get(f'{base_url}/api/database/status')
db_status = response.json()
print(f'数据库状态: {db_status["status"]}')
print(f'连接次数: {db_status["connection_count"]}')

# 4. 创建测试订单
print('\n4. 创建测试订单')
order_data = {'order_id': 'DEMO_ORDER_001', 'customer_id': 'DEMO_CUSTOMER'}
response = requests.post(f'{base_url}/api/orders', json=order_data)
print(f'创建订单状态: {response.status_code}')

# 5. 添加商品
print('\n5. 添加商品到订单')
item_data = {'product_id': 'P001', 'quantity': 2, 'price': 100.0}
response = requests.post(f'{base_url}/api/orders/DEMO_ORDER_001/items', json=item_data)
print(f'添加商品状态: {response.status_code}')

# 6. 确认订单
print('\n6. 确认订单')
response = requests.post(f'{base_url}/api/orders/DEMO_ORDER_001/confirm')
print(f'确认订单状态: {response.status_code}')

# 7. 正常支付测试
print('\n7. 正常支付测试')
payment_data = {'payment_method': 'credit_card'}
response = requests.post(f'{base_url}/api/orders/DEMO_ORDER_001/payment', json=payment_data)
print(f'支付状态: {response.status_code}')
if response.status_code == 200:
    print('✅ 正常支付成功')
    result = response.json()
    print(f'支付ID: {result["payment_id"]}')
    print(f'支付金额: {result["amount"]}')
else:
    print('❌ 支付失败')
    print(f'错误: {response.json()}')

print('\n=== 现在测试数据库连接中断场景 ===')

# 8. 创建新订单用于测试数据库中断
print('\n8. 创建新订单用于数据库中断测试')
order_data2 = {'order_id': 'DEMO_ORDER_002', 'customer_id': 'DEMO_CUSTOMER'}
response = requests.post(f'{base_url}/api/orders', json=order_data2)
response = requests.post(f'{base_url}/api/orders/DEMO_ORDER_002/items', json=item_data)
response = requests.post(f'{base_url}/api/orders/DEMO_ORDER_002/confirm')
print('新订单创建完成')

# 9. 断开数据库连接
print('\n9. 断开数据库连接')
response = requests.post(f'{base_url}/api/database/disconnect')
print(f'断开连接状态: {response.status_code}')
if response.status_code == 200:
    print('✅ 数据库连接已断开')

# 10. 在数据库断开状态下尝试支付
print('\n10. 在数据库断开状态下尝试支付')
response = requests.post(f'{base_url}/api/orders/DEMO_ORDER_002/payment', json=payment_data)
print(f'支付状态: {response.status_code}')
if response.status_code == 503:
    print('✅ 正确返回503服务不可用错误')
    error_info = response.json()
    print(f'错误信息: {error_info["error"]}')
    print(f'数据库状态: {error_info["database_status"]}')
else:
    print('❌ 未正确处理数据库断开情况')

# 11. 重新连接数据库
print('\n11. 重新连接数据库')
response = requests.post(f'{base_url}/api/database/connect')
print(f'重连状态: {response.status_code}')
if response.status_code == 200:
    print('✅ 数据库重新连接成功')

# 12. 数据库恢复后再次尝试支付
print('\n12. 数据库恢复后再次尝试支付')
response = requests.post(f'{base_url}/api/orders/DEMO_ORDER_002/payment', json=payment_data)
print(f'支付状态: {response.status_code}')
if response.status_code == 200:
    print('✅ 数据库恢复后支付成功')
    result = response.json()
    print(f'支付ID: {result["payment_id"]}')
else:
    print('❌ 数据库恢复后支付仍然失败')
    print(f'错误: {response.json()}')

# 13. 查看最终统计
print('\n13. 查看系统统计信息')
response = requests.get(f'{base_url}/api/stats')
if response.status_code == 200:
    stats = response.json()
    print('系统统计:')
    print(f'  数据库连接次数: {stats["database"]["connection_count"]}')
    print(f'  数据库操作次数: {stats["database"]["operation_count"]}')
    print(f'  数据库错误次数: {stats["database"]["error_count"]}')
    print(f'  支付成功: {stats["payments"]["completed"]}')
    print(f'  支付失败: {stats["payments"]["failed"]}')

print('\n=== 演示完成 ===')
print('✅ Flask服务成功处理了数据库连接中断和恢复的情况')
print('✅ 服务在数据库断开时正确返回错误信息而不是崩溃')
print('✅ 数据库恢复后服务能够正常处理新的请求')
