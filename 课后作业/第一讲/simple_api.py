# -*- coding: utf-8 -*-
"""
简单的Flask API，用于测试我们的函数
可以用Postman进行API测试
"""

from flask import Flask, request, jsonify
from defective_functions import divide, find_max, get_item

app = Flask(__name__)

@app.route('/divide', methods=['POST'])
def api_divide():
    """除法API"""
    try:
        data = request.json
        a = data.get('a')
        b = data.get('b')
        
        if a is None or b is None:
            return jsonify({'error': '缺少参数a或b'}), 400
        
        result = divide(a, b)
        return jsonify({'result': result, 'status': 'success'})
    
    except ZeroDivisionError:
        return jsonify({'error': '除数不能为零', 'status': 'error'}), 400
    except Exception as e:
        return jsonify({'error': str(e), 'status': 'error'}), 500

@app.route('/find_max', methods=['POST'])
def api_find_max():
    """查找最大值API"""
    try:
        data = request.json
        numbers = data.get('numbers')
        
        if numbers is None:
            return jsonify({'error': '缺少参数numbers'}), 400
        
        if not isinstance(numbers, list):
            return jsonify({'error': 'numbers必须是数组'}), 400
        
        result = find_max(numbers)
        return jsonify({'result': result, 'status': 'success'})
    
    except Exception as e:
        return jsonify({'error': str(e), 'status': 'error'}), 500

@app.route('/get_item', methods=['POST'])
def api_get_item():
    """获取列表元素API"""
    try:
        data = request.json
        items = data.get('items')
        index = data.get('index')
        
        if items is None or index is None:
            return jsonify({'error': '缺少参数items或index'}), 400
        
        if not isinstance(items, list):
            return jsonify({'error': 'items必须是数组'}), 400
        
        result = get_item(items, index)
        return jsonify({'result': result, 'status': 'success'})
    
    except IndexError:
        return jsonify({'error': '索引超出范围', 'status': 'error'}), 400
    except Exception as e:
        return jsonify({'error': str(e), 'status': 'error'}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({'status': 'healthy', 'message': 'API正常运行'})

if __name__ == '__main__':
    print("启动API服务器...")
    print("可以使用以下URL进行测试:")
    print("POST http://localhost:5000/divide")
    print("POST http://localhost:5000/find_max") 
    print("POST http://localhost:5000/get_item")
    print("GET  http://localhost:5000/health")
    app.run(debug=True, host='0.0.0.0', port=5000)
