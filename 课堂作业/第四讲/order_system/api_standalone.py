"""
独立的 FastAPI 服务
解决导入问题的版本
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
import sys
import os

# 添加当前目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from inventory import Inventory, InsufficientStockError, ProductNotFoundError
from payment import PaymentProcessor, PaymentMethod, PaymentStatus, InsufficientFundsError
from order import OrderService, OrderStatus

# 创建 FastAPI 应用
app = FastAPI(title="订单系统 API", version="1.0.0")

# 初始化服务
inventory = Inventory()
payment_processor = PaymentProcessor()
order_service = OrderService(inventory, payment_processor)


# ============= Pydantic 模型 =============

class ProductStock(BaseModel):
    """商品库存模型"""
    product_id: str
    quantity: int


class OrderItemRequest(BaseModel):
    """订单项请求模型"""
    product_id: str
    quantity: int
    price: float


class CreateOrderRequest(BaseModel):
    """创建订单请求模型"""
    order_id: str
    customer_id: str


class PaymentRequest(BaseModel):
    """支付请求模型"""
    payment_method: str


# ============= 库存 API =============

@app.post("/api/inventory/products", status_code=201)
def add_product_stock(product: ProductStock):
    """添加商品库存"""
    try:
        inventory.add_product(product.product_id, product.quantity)
        return {
            "message": "商品库存添加成功",
            "product_id": product.product_id,
            "quantity": product.quantity
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/inventory/products/{product_id}")
def get_product_stock(product_id: str):
    """查询商品库存"""
    try:
        stock = inventory.get_stock(product_id)
        return {
            "product_id": product_id,
            "stock": stock
        }
    except ProductNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/api/inventory/products")
def get_all_stock():
    """获取所有库存"""
    return {
        "products": inventory.get_all_stock()
    }


@app.delete("/api/inventory/products/{product_id}")
def remove_product(product_id: str):
    """移除商品"""
    try:
        inventory.remove_product(product_id)
        return {
            "message": "商品移除成功",
            "product_id": product_id
        }
    except ProductNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ============= 订单 API =============

@app.post("/api/orders", status_code=201)
def create_order(request: CreateOrderRequest):
    """创建订单"""
    try:
        order = order_service.create_order(request.order_id, request.customer_id)
        return {
            "message": "订单创建成功",
            "order_id": order.order_id,
            "customer_id": order.customer_id,
            "status": order.status.value
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/orders/{order_id}/items")
def add_order_item(order_id: str, item: OrderItemRequest):
    """向订单添加商品"""
    try:
        order_service.add_item_to_order(
            order_id, item.product_id, item.quantity, item.price
        )
        order = order_service.get_order(order_id)
        return {
            "message": "商品添加成功",
            "order_id": order_id,
            "item_count": order.item_count,
            "total_amount": order.total_amount
        }
    except (ValueError, ProductNotFoundError) as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/orders/{order_id}")
def get_order(order_id: str):
    """获取订单详情"""
    try:
        order = order_service.get_order(order_id)
        return order.to_dict()
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/api/orders")
def get_all_orders():
    """获取所有订单"""
    orders = order_service.get_all_orders()
    return {
        "orders": [order.to_dict() for order in orders.values()]
    }


@app.post("/api/orders/{order_id}/confirm")
def confirm_order(order_id: str):
    """确认订单"""
    try:
        order_service.confirm_order(order_id)
        order = order_service.get_order(order_id)
        return {
            "message": "订单确认成功",
            "order_id": order_id,
            "status": order.status.value
        }
    except (ValueError, InsufficientStockError, ProductNotFoundError) as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/orders/{order_id}/payment")
def process_order_payment(order_id: str, payment: PaymentRequest):
    """处理订单支付"""
    try:
        # 验证支付方式
        payment_method = PaymentMethod(payment.payment_method)
        
        payment_id = order_service.process_payment(order_id, payment_method)
        order = order_service.get_order(order_id)
        
        return {
            "message": "支付成功",
            "order_id": order_id,
            "payment_id": payment_id,
            "status": order.status.value,
            "amount": order.total_amount
        }
    except (ValueError, InsufficientFundsError) as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/orders/{order_id}/ship")
def ship_order(order_id: str):
    """发货"""
    try:
        order_service.ship_order(order_id)
        order = order_service.get_order(order_id)
        return {
            "message": "发货成功",
            "order_id": order_id,
            "status": order.status.value
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/orders/{order_id}/complete")
def complete_order(order_id: str):
    """完成订单"""
    try:
        order_service.complete_order(order_id)
        order = order_service.get_order(order_id)
        return {
            "message": "订单完成",
            "order_id": order_id,
            "status": order.status.value
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/orders/{order_id}/cancel")
def cancel_order(order_id: str):
    """取消订单"""
    try:
        order_service.cancel_order(order_id)
        order = order_service.get_order(order_id)
        return {
            "message": "订单已取消",
            "order_id": order_id,
            "status": order.status.value
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============= 支付 API =============

@app.get("/api/payments/{payment_id}")
def get_payment(payment_id: str):
    """获取支付信息"""
    try:
        payment = payment_processor.get_payment(payment_id)
        return payment.to_dict()
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/api/payments/balance/{payment_method}")
def get_payment_balance(payment_method: str):
    """获取支付方式余额"""
    try:
        method = PaymentMethod(payment_method)
        balance = payment_processor.get_balance(method)
        return {
            "payment_method": payment_method,
            "balance": balance
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============= 健康检查 =============

@app.get("/")
def root():
    """根路径"""
    return {
        "message": "订单系统 API",
        "version": "1.0.0",
        "endpoints": {
            "inventory": "/api/inventory",
            "orders": "/api/orders",
            "payments": "/api/payments"
        }
    }


@app.get("/health")
def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "inventory_products": len(inventory.get_all_stock()),
        "total_orders": len(order_service.get_all_orders())
    }


# ============= 测试数据初始化 =============

@app.post("/api/test/init-data")
def init_test_data():
    """初始化测试数据"""
    # 清空现有数据
    inventory.clear()
    payment_processor.clear()
    order_service.clear()
    
    # 添加测试商品
    inventory.add_product("P001", 100)
    inventory.add_product("P002", 50)
    inventory.add_product("P003", 200)
    
    return {
        "message": "测试数据初始化成功",
        "products": inventory.get_all_stock()
    }


@app.delete("/api/test/clear-data")
def clear_test_data():
    """清空所有数据"""
    inventory.clear()
    payment_processor.clear()
    order_service.clear()
    
    return {
        "message": "所有数据已清空"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
