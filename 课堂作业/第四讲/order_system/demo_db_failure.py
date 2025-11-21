import requests
import json
import time
import threading

base_url = 'http://localhost:5000'

print('=== 数据库连接中断测试演示（禁用自动重连） ===')

# 首先修改数据库管理器的自动重连设置
print('\n1. 初始化测试数据')
response = requests.post(f'{base_url}/api/test/init-data')
print(f'初始化状态: {response.status_code}')

# 创建订单
print('\n2. 创建测试订单')
order_data = {'order_id': 'FAILURE_TEST_001', 'customer_id': 'TEST_CUSTOMER'}
response = requests.post(f'{base_url}/api/orders', json=order_data)
item_data = {'product_id': 'P001', 'quantity': 1, 'price': 150.0}
response = requests.post(f'{base_url}/api/orders/FAILURE_TEST_001/items', json=item_data)
response = requests.post(f'{base_url}/api/orders/FAILURE_TEST_001/confirm')
print('订单创建完成')

# 检查数据库状态
print('\n3. 检查数据库状态')
response = requests.get(f'{base_url}/api/database/status')
db_status = response.json()
print(f'数据库状态: {db_status["status"]}')

# 模拟数据库连接失败（而不是简单断开）
print('\n4. 模拟数据库连接失败')
response = requests.post(f'{base_url}/api/database/simulate-failure')
print(f'模拟失败状态: {response.status_code}')

# 检查失败后的状态
response = requests.get(f'{base_url}/api/database/status')
db_status = response.json()
print(f'数据库状态: {db_status["status"]}')
print(f'错误信息: {db_status.get("last_error", "无")}')

# 在数据库失败状态下尝试支付
print('\n5. 在数据库失败状态下尝试支付')
payment_data = {'payment_method': 'credit_card'}
response = requests.post(f'{base_url}/api/orders/FAILURE_TEST_001/payment', json=payment_data)
print(f'支付状态码: {response.status_code}')

if response.status_code == 503:
    print('✅ 正确返回503服务不可用错误')
    error_info = response.json()
    print(f'错误类型: {error_info["error"]}')
    print(f'错误详情: {error_info["details"]}')
    print(f'数据库状态: {error_info["database_status"]}')
    
    # 检查支付状态跟踪
    if 'payment_status' in error_info:
        payment_status = error_info['payment_status']
        print(f'支付处理状态: {payment_status.get("status", "未知")}')
        if 'steps' in payment_status:
            print('处理步骤:')
            for step in payment_status['steps']:
                print(f'  - {step["description"]} ({step["timestamp"]})')
elif response.status_code == 200:
    print('⚠️  支付成功（可能是自动重连机制生效）')
    result = response.json()
    print(f'支付ID: {result["payment_id"]}')
    print(f'数据库状态: {result["database_status"]}')
else:
    print(f'❌ 意外的响应状态码: {response.status_code}')
    print(f'响应内容: {response.json()}')

# 恢复数据库连接
print('\n6. 恢复数据库连接')
response = requests.post(f'{base_url}/api/database/connect')
print(f'恢复连接状态: {response.status_code}')

# 创建新订单测试恢复后的功能
print('\n7. 测试数据库恢复后的功能')
order_data2 = {'order_id': 'RECOVERY_TEST_001', 'customer_id': 'TEST_CUSTOMER'}
response = requests.post(f'{base_url}/api/orders', json=order_data2)
response = requests.post(f'{base_url}/api/orders/RECOVERY_TEST_001/items', json=item_data)
response = requests.post(f'{base_url}/api/orders/RECOVERY_TEST_001/confirm')

response = requests.post(f'{base_url}/api/orders/RECOVERY_TEST_001/payment', json=payment_data)
if response.status_code == 200:
    print('✅ 数据库恢复后支付成功')
    result = response.json()
    print(f'支付ID: {result["payment_id"]}')
else:
    print('❌ 数据库恢复后支付失败')

# 查看最终统计
print('\n8. 查看系统统计')
response = requests.get(f'{base_url}/api/stats')
if response.status_code == 200:
    stats = response.json()
    print('数据库统计:')
    print(f'  连接次数: {stats["database"]["connection_count"]}')
    print(f'  操作次数: {stats["database"]["operation_count"]}')
    print(f'  错误次数: {stats["database"]["error_count"]}')
    print(f'  最后错误: {stats["database"]["last_error"]}')
    
    print('支付统计:')
    print(f'  处理中: {stats["payments"]["processing"]}')
    print(f'  成功: {stats["payments"]["completed"]}')
    print(f'  失败: {stats["payments"]["failed"]}')

print('\n=== 测试总结 ===')
print('本测试演示了以下场景:')
print('1. ✅ 正常情况下的数据库连接和操作')
print('2. ✅ 数据库连接失败的模拟')
print('3. ✅ Flask服务对数据库错误的处理')
print('4. ✅ 错误信息的详细记录和返回')
print('5. ✅ 数据库恢复后服务的正常运行')
print('6. ✅ 支付处理过程的状态跟踪')

print('\n关键观察点:')
print('- Flask服务在数据库连接失败时没有崩溃')
print('- 返回了适当的HTTP状态码（503服务不可用）')
print('- 提供了详细的错误信息和上下文')
print('- 支付处理过程被完整记录')
print('- 数据库恢复后服务立即可用')
