"""
Flask应用 - 测试数据库连接中断和恢复
集成订单系统，在支付过程中模拟数据库连接问题
"""

from flask import Flask, request, jsonify
import threading
import time
from datetime import datetime
from typing import Dict, Any

# 导入现有模块
from inventory import Inventory, InsufficientStockError, ProductNotFoundError
from payment import PaymentProcessor, PaymentMethod, PaymentStatus, InsufficientFundsError
from order import OrderService, OrderStatus
from database_simulator import DatabaseSimulator, DatabaseManager, DatabaseConnectionError, DatabaseOperationError

app = Flask(__name__)

# 全局变量
db_simulator = DatabaseSimulator()
db_manager = DatabaseManager(db_simulator)
inventory = Inventory()
payment_processor = PaymentProcessor()
order_service = OrderService(inventory, payment_processor)

# 支付处理状态跟踪
payment_processing_status = {}


class EnhancedPaymentProcessor(PaymentProcessor):
    """增强的支付处理器，集成数据库操作"""
    
    def __init__(self, db_manager: DatabaseManager):
        super().__init__()
        self.db_manager = db_manager
    
    def process_payment_with_db(self, payment_id: str) -> bool:
        """
        带数据库操作的支付处理
        
        Args:
            payment_id: 支付ID
            
        Returns:
            是否成功
        """
        payment = self.get_payment(payment_id)
        
        # 更新支付处理状态
        payment_processing_status[payment_id] = {
            "status": "processing",
            "start_time": datetime.now().isoformat(),
            "steps": []
        }
        
        try:
            # 步骤1: 开始支付处理
            payment.process()
            self._log_step(payment_id, "payment_processing_started", "支付处理开始")
            
            # 步骤2: 记录支付开始到数据库
            self._log_step(payment_id, "db_insert_payment_start", "记录支付开始")
            self.db_manager.execute_with_retry(
                "INSERT INTO payment_logs (payment_id, status, timestamp, amount, method)",
                {
                    "id": f"log_{payment_id}_start",
                    "payment_id": payment_id,
                    "status": "processing",
                    "timestamp": datetime.now().isoformat(),
                    "amount": payment.amount,
                    "method": payment.method.value
                }
            )
            
            # 步骤3: 检查余额（数据库查询）
            self._log_step(payment_id, "db_check_balance", "检查账户余额")
            balance_result = self.db_manager.execute_with_retry(
                "SELECT balance FROM accounts WHERE payment_method = ?",
                {"payment_method": payment.method.value}
            )
            
            # 步骤4: 验证余额
            if self._account_balances[payment.method] < payment.amount:
                self._log_step(payment_id, "insufficient_funds", "余额不足")
                payment.fail()
                
                # 记录失败到数据库
                self.db_manager.execute_with_retry(
                    "INSERT INTO payment_logs (payment_id, status, timestamp, error)",
                    {
                        "id": f"log_{payment_id}_failed",
                        "payment_id": payment_id,
                        "status": "failed",
                        "timestamp": datetime.now().isoformat(),
                        "error": "insufficient_funds"
                    }
                )
                
                raise InsufficientFundsError(
                    f"余额不足。支付方式: {payment.method.value}, "
                    f"需要: {payment.amount}, "
                    f"可用: {self._account_balances[payment.method]}"
                )
            
            # 步骤5: 执行扣款事务
            self._log_step(payment_id, "db_transaction_start", "开始扣款事务")
            transaction_operations = [
                ("UPDATE accounts SET balance = balance - ? WHERE payment_method = ?", 
                 {"amount": payment.amount, "payment_method": payment.method.value}),
                ("INSERT INTO payment_records (payment_id, order_id, amount, method, status, timestamp)",
                 {
                     "id": payment_id,
                     "payment_id": payment_id,
                     "order_id": payment.order_id,
                     "amount": payment.amount,
                     "method": payment.method.value,
                     "status": "success",
                     "timestamp": datetime.now().isoformat()
                 })
            ]
            
            # 执行事务
            self.db_manager.execute_transaction(transaction_operations)
            
            # 步骤6: 更新内存中的余额
            self._account_balances[payment.method] -= payment.amount
            payment.complete()
            
            self._log_step(payment_id, "payment_completed", "支付完成")
            
            # 更新处理状态
            payment_processing_status[payment_id]["status"] = "completed"
            payment_processing_status[payment_id]["end_time"] = datetime.now().isoformat()
            
            return True
            
        except (DatabaseConnectionError, DatabaseOperationError) as e:
            self._log_step(payment_id, "database_error", f"数据库错误: {str(e)}")
            payment.fail()
            
            # 更新处理状态
            payment_processing_status[payment_id]["status"] = "failed"
            payment_processing_status[payment_id]["error"] = str(e)
            payment_processing_status[payment_id]["end_time"] = datetime.now().isoformat()
            
            raise e
        
        except Exception as e:
            self._log_step(payment_id, "general_error", f"其他错误: {str(e)}")
            payment.fail()
            
            # 更新处理状态
            payment_processing_status[payment_id]["status"] = "failed"
            payment_processing_status[payment_id]["error"] = str(e)
            payment_processing_status[payment_id]["end_time"] = datetime.now().isoformat()
            
            raise e
    
    def _log_step(self, payment_id: str, step: str, description: str):
        """记录处理步骤"""
        if payment_id in payment_processing_status:
            payment_processing_status[payment_id]["steps"].append({
                "step": step,
                "description": description,
                "timestamp": datetime.now().isoformat()
            })
        print(f"[{payment_id}] {step}: {description}")


# 创建增强的支付处理器
enhanced_payment_processor = EnhancedPaymentProcessor(db_manager)
order_service.payment_processor = enhanced_payment_processor


# ============= Flask路由 =============

@app.route('/')
def home():
    """首页"""
    return jsonify({
        "message": "订单系统数据库连接测试",
        "endpoints": {
            "database": "/api/database",
            "orders": "/api/orders",
            "payments": "/api/payments",
            "test": "/api/test"
        }
    })


@app.route('/api/database/status')
def get_database_status():
    """获取数据库状态"""
    return jsonify(db_simulator.get_connection_info())


@app.route('/api/database/disconnect', methods=['POST'])
def disconnect_database():
    """断开数据库连接"""
    db_simulator.disconnect()
    return jsonify({
        "message": "数据库连接已断开",
        "status": db_simulator.status.value
    })


@app.route('/api/database/connect', methods=['POST'])
def connect_database():
    """连接数据库"""
    success = db_simulator.connect()
    return jsonify({
        "message": "数据库连接成功" if success else "数据库连接失败",
        "status": db_simulator.status.value,
        "success": success
    })


@app.route('/api/database/simulate-failure', methods=['POST'])
def simulate_database_failure():
    """模拟数据库连接失败"""
    db_simulator.simulate_connection_failure()
    return jsonify({
        "message": "已模拟数据库连接失败",
        "status": db_simulator.status.value
    })


@app.route('/api/test/init-data', methods=['POST'])
def init_test_data():
    """初始化测试数据"""
    # 清空现有数据
    inventory.clear()
    enhanced_payment_processor.clear()
    order_service.clear()
    db_simulator.clear_data()
    db_simulator.reset_stats()
    
    # 连接数据库
    db_simulator.connect()
    
    # 添加测试商品
    inventory.add_product("P001", 100)
    inventory.add_product("P002", 50)
    inventory.add_product("P003", 200)
    
    return jsonify({
        "message": "测试数据初始化成功",
        "database_status": db_simulator.status.value,
        "products": inventory.get_all_stock()
    })


@app.route('/api/orders', methods=['POST'])
def create_order():
    """创建订单"""
    data = request.json
    try:
        order = order_service.create_order(data['order_id'], data['customer_id'])
        return jsonify({
            "message": "订单创建成功",
            "order_id": order.order_id,
            "status": order.status.value
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/api/orders/<order_id>/items', methods=['POST'])
def add_order_item(order_id):
    """添加订单项"""
    data = request.json
    try:
        order_service.add_item_to_order(
            order_id, data['product_id'], data['quantity'], data['price']
        )
        order = order_service.get_order(order_id)
        return jsonify({
            "message": "商品添加成功",
            "order_id": order_id,
            "total_amount": order.total_amount
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/api/orders/<order_id>/confirm', methods=['POST'])
def confirm_order(order_id):
    """确认订单"""
    try:
        order_service.confirm_order(order_id)
        order = order_service.get_order(order_id)
        return jsonify({
            "message": "订单确认成功",
            "order_id": order_id,
            "status": order.status.value
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/api/orders/<order_id>/payment', methods=['POST'])
def process_payment(order_id):
    """处理支付 - 关键测试接口"""
    data = request.json
    payment_method = data.get('payment_method', 'credit_card')
    
    try:
        # 获取订单
        order = order_service.get_order(order_id)
        
        # 创建支付记录
        payment_id = f"PAY_{order_id}"
        payment_method_enum = PaymentMethod(payment_method)
        
        payment = enhanced_payment_processor.create_payment(
            payment_id, order_id, order.total_amount, payment_method_enum
        )
        
        # 处理支付（包含数据库操作）
        enhanced_payment_processor.process_payment_with_db(payment_id)
        
        # 标记订单为已支付
        order.mark_paid(payment_id)
        
        return jsonify({
            "message": "支付成功",
            "order_id": order_id,
            "payment_id": payment_id,
            "amount": order.total_amount,
            "status": order.status.value,
            "database_status": db_simulator.status.value
        })
        
    except (DatabaseConnectionError, DatabaseOperationError) as e:
        return jsonify({
            "error": "数据库连接错误",
            "details": str(e),
            "database_status": db_simulator.status.value,
            "payment_status": payment_processing_status.get(f"PAY_{order_id}", {})
        }), 503
        
    except Exception as e:
        return jsonify({
            "error": str(e),
            "database_status": db_simulator.status.value,
            "payment_status": payment_processing_status.get(f"PAY_{order_id}", {})
        }), 400


@app.route('/api/orders/<order_id>')
def get_order(order_id):
    """获取订单详情"""
    try:
        order = order_service.get_order(order_id)
        return jsonify(order.to_dict())
    except Exception as e:
        return jsonify({"error": str(e)}), 404


@app.route('/api/payments/<payment_id>/status')
def get_payment_status(payment_id):
    """获取支付处理状态"""
    if payment_id in payment_processing_status:
        return jsonify(payment_processing_status[payment_id])
    else:
        return jsonify({"error": "支付记录不存在"}), 404


@app.route('/api/test/scenario/payment-with-db-failure', methods=['POST'])
def test_payment_with_db_failure():
    """测试场景：支付过程中数据库连接中断"""
    data = request.json
    order_id = data.get('order_id', 'TEST_ORDER_001')
    
    def simulate_failure_during_payment():
        """在支付过程中模拟数据库失败"""
        time.sleep(2)  # 等待支付开始
        print("模拟数据库连接中断...")
        db_simulator.simulate_connection_failure()
        
        time.sleep(5)  # 等待一段时间后恢复
        print("恢复数据库连接...")
        db_simulator.connect()
    
    # 启动后台线程模拟数据库失败
    failure_thread = threading.Thread(target=simulate_failure_during_payment)
    failure_thread.start()
    
    return jsonify({
        "message": "已启动支付过程中数据库失败测试场景",
        "order_id": order_id,
        "instructions": f"请立即调用 POST /api/orders/{order_id}/payment 来触发支付"
    })


@app.route('/api/test/scenario/recovery-test', methods=['POST'])
def test_recovery():
    """测试恢复机制"""
    try:
        # 先断开连接
        db_simulator.disconnect()
        
        # 尝试执行数据库操作（应该会自动重连）
        result = db_manager.execute_with_retry(
            "SELECT * FROM test_table",
            {"test": "recovery"}
        )
        
        return jsonify({
            "message": "恢复测试成功",
            "database_status": db_simulator.status.value,
            "result": result
        })
        
    except Exception as e:
        return jsonify({
            "error": "恢复测试失败",
            "details": str(e),
            "database_status": db_simulator.status.value
        }), 500


@app.route('/api/stats')
def get_stats():
    """获取统计信息"""
    return jsonify({
        "database": db_simulator.get_connection_info(),
        "inventory": {
            "products": len(inventory.get_all_stock()),
            "total_stock": sum(inventory.get_all_stock().values())
        },
        "orders": {
            "total": len(order_service.get_all_orders())
        },
        "payments": {
            "processing": len([p for p in payment_processing_status.values() 
                            if p.get("status") == "processing"]),
            "completed": len([p for p in payment_processing_status.values() 
                           if p.get("status") == "completed"]),
            "failed": len([p for p in payment_processing_status.values() 
                         if p.get("status") == "failed"])
        }
    })


if __name__ == '__main__':
    print("启动订单系统数据库连接测试服务...")
    print("访问 http://localhost:5000 查看API文档")
    print("测试场景：")
    print("1. POST /api/test/init-data - 初始化测试数据")
    print("2. POST /api/test/scenario/payment-with-db-failure - 测试支付过程中数据库失败")
    print("3. POST /api/orders/{order_id}/payment - 触发支付处理")
    print("4. GET /api/database/status - 查看数据库状态")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
