from flask import Flask, request, jsonify

def create_app():
    """创建并配置 Flask 应用"""
    app = Flask(__name__)

    @app.route("/checkout", methods=["POST"])
    def checkout():
        """
        处理购物车结账请求
        
        请求格式:
        {
            "items": [
                {"price": 10.0, "quantity": 2},
                {"price": 5.0, "quantity": 1}
            ]
        }
        
        返回格式:
        成功: {"total": 25.0, "status": "ok"}
        失败: {"error": "empty cart"}
        """
        try:
            # 使用 force=True 和 silent=True 来更好地处理 JSON 解析
            data = request.get_json(force=True, silent=True)
            
            # 检查请求数据是否存在
            if data is None:
                return jsonify({"error": "invalid request data"}), 400
            
            # 如果data是空字典{}，items会是[]，这是正确的
            items = data.get("items", [])
            
            # 检查购物车是否为空
            if not items:
                return jsonify({"error": "empty cart"}), 400
            
            # 计算总价
            total = 0
            for item in items:
                # 验证每个商品的数据格式
                if not isinstance(item, dict):
                    return jsonify({"error": "invalid item format"}), 400
                
                price = item.get("price")
                quantity = item.get("quantity")
                
                # 验证价格和数量
                if price is None or quantity is None:
                    return jsonify({"error": "missing price or quantity"}), 400
                
                if not isinstance(price, (int, float)) or not isinstance(quantity, (int, float)):
                    return jsonify({"error": "invalid price or quantity type"}), 400
                
                if price < 0 or quantity < 0:
                    return jsonify({"error": "negative price or quantity"}), 400
                
                total += price * quantity
            
            return jsonify({"total": total, "status": "ok"}), 200
            
        except Exception as e:
            return jsonify({"error": "internal server error"}), 500

    @app.route("/health", methods=["GET"])
    def health_check():
        """健康检查端点"""
        return jsonify({"status": "healthy"}), 200
    
    return app

# 创建应用实例
app = create_app()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
