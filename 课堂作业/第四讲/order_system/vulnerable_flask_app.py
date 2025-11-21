"""
存在 SQL 注入漏洞的 Flask 登录应用
⚠️ 警告：此代码仅用于安全测试演示，包含严重的安全漏洞！
"""

import sqlite3
import os
from flask import Flask, request, jsonify, render_template_string
from datetime import datetime

app = Flask(__name__)

# 数据库文件路径
DB_FILE = 'vulnerable_users.db'

def init_database():
    """初始化数据库和测试数据"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # 创建用户表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            email TEXT,
            role TEXT DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 创建日志表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS login_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            ip_address TEXT,
            success INTEGER,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            user_agent TEXT
        )
    ''')
    
    # 插入测试用户数据
    test_users = [
        ('admin', 'admin123', 'admin@example.com', 'admin'),
        ('user', 'user123', 'user@example.com', 'user'),
        ('test', 'test123', 'test@example.com', 'user'),
        ('alice', 'alice456', 'alice@example.com', 'user'),
        ('bob', 'bob789', 'bob@example.com', 'user'),
        ('manager', 'manager123', 'manager@example.com', 'manager'),
        ('guest', 'guest123', 'guest@example.com', 'guest')
    ]
    
    # 检查是否已有数据
    cursor.execute('SELECT COUNT(*) FROM users')
    if cursor.fetchone()[0] == 0:
        cursor.executemany(
            'INSERT INTO users (username, password, email, role) VALUES (?, ?, ?, ?)',
            test_users
        )
        print("✅ 测试用户数据已插入")
    
    conn.commit()
    conn.close()

def log_login_attempt(username, ip_address, success, user_agent):
    """记录登录尝试"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO login_logs (username, ip_address, success, user_agent) VALUES (?, ?, ?, ?)',
        (username, ip_address, success, user_agent)
    )
    conn.commit()
    conn.close()

# 登录页面HTML模板
LOGIN_TEMPLATE = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Flask 登录测试 - SQL 注入演示</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            margin: 0;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .container {
            background: white;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
            width: 100%;
            max-width: 500px;
        }
        .warning {
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            color: #856404;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 8px;
            font-weight: bold;
        }
        input[type="text"], input[type="password"] {
            width: 100%;
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 5px;
            font-size: 16px;
            box-sizing: border-box;
        }
        button {
            width: 100%;
            padding: 12px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 5px;
            font-size: 16px;
            cursor: pointer;
        }
        button:hover {
            opacity: 0.9;
        }
        .result {
            margin-top: 20px;
            padding: 15px;
            border-radius: 5px;
            display: none;
        }
        .success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        .error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        .sql-examples {
            margin-top: 30px;
            background: #f8f9fa;
            padding: 20px;
            border-radius: 5px;
            border-left: 4px solid #dc3545;
        }
        .sql-examples h3 {
            color: #dc3545;
            margin-top: 0;
        }
        .sql-examples code {
            background: #e9ecef;
            padding: 2px 4px;
            border-radius: 3px;
            font-family: monospace;
        }
        .test-accounts {
            margin-top: 20px;
            background: #e7f3ff;
            padding: 15px;
            border-radius: 5px;
            border-left: 4px solid #007bff;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="warning">
            <strong>⚠️ 安全警告：</strong> 此应用包含故意的 SQL 注入漏洞，仅用于安全测试演示！
        </div>
        
        <div class="header">
            <h1>Flask 登录接口</h1>
            <p>SQL 注入漏洞演示</p>
        </div>
        
        <form id="loginForm">
            <div class="form-group">
                <label for="username">用户名：</label>
                <input type="text" id="username" name="username" required>
            </div>
            
            <div class="form-group">
                <label for="password">密码：</label>
                <input type="password" id="password" name="password" required>
            </div>
            
            <button type="submit">登录</button>
        </form>
        
        <div id="result" class="result"></div>
        
        <div class="test-accounts">
            <h3>🧪 测试账号</h3>
            <p><strong>管理员：</strong> admin / admin123</p>
            <p><strong>普通用户：</strong> user / user123</p>
            <p><strong>测试用户：</strong> test / test123</p>
        </div>
        
        <div class="sql-examples">
            <h3>🔓 SQL 注入测试用例</h3>
            <p><strong>经典注入：</strong> <code>' OR 1=1 --</code></p>
            <p><strong>联合查询：</strong> <code>' UNION SELECT username, password FROM users --</code></p>
            <p><strong>绕过登录：</strong> <code>admin'--</code></p>
            <p><strong>获取所有用户：</strong> <code>' OR '1'='1</code></p>
            <p><em>在用户名或密码字段中尝试这些输入</em></p>
        </div>
    </div>

    <script>
        document.getElementById('loginForm').addEventListener('submit', function(e) {
            e.preventDefault();
            
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            const resultDiv = document.getElementById('result');
            
            fetch('/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    username: username,
                    password: password
                })
            })
            .then(response => response.json())
            .then(data => {
                resultDiv.style.display = 'block';
                
                if (data.success) {
                    resultDiv.className = 'result success';
                    resultDiv.innerHTML = `
                        <h4>✅ 登录成功！</h4>
                        <p><strong>用户信息：</strong></p>
                        <pre>${JSON.stringify(data.user_info, null, 2)}</pre>
                        ${data.debug_info ? `<p><strong>调试信息：</strong></p><pre>${data.debug_info}</pre>` : ''}
                    `;
                } else {
                    resultDiv.className = 'result error';
                    resultDiv.innerHTML = `
                        <h4>❌ 登录失败</h4>
                        <p>${data.message}</p>
                        ${data.debug_info ? `<p><strong>调试信息：</strong></p><pre>${data.debug_info}</pre>` : ''}
                    `;
                }
            })
            .catch(error => {
                resultDiv.style.display = 'block';
                resultDiv.className = 'result error';
                resultDiv.innerHTML = `<h4>❌ 请求失败</h4><p>${error.message}</p>`;
            });
        });
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    """主页 - 显示登录表单"""
    return render_template_string(LOGIN_TEMPLATE)

@app.route('/login', methods=['POST'])
def vulnerable_login():
    """
    存在 SQL 注入漏洞的登录接口
    ⚠️ 危险：直接拼接 SQL 语句，没有参数化查询
    """
    data = request.get_json()
    username = data.get('username', '')
    password = data.get('password', '')
    
    # 获取客户端信息
    ip_address = request.remote_addr
    user_agent = request.headers.get('User-Agent', '')
    
    # ⚠️ 漏洞代码：直接字符串拼接 SQL 查询
    # 这里故意不使用参数化查询，创建 SQL 注入漏洞
    sql_query = f"""
        SELECT id, username, password, email, role 
        FROM users 
        WHERE username = '{username}' AND password = '{password}'
    """
    
    print(f"🔍 执行的 SQL 查询: {sql_query}")
    
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # 执行可能被注入的 SQL 查询
        cursor.execute(sql_query)
        result = cursor.fetchall()
        
        # 记录登录尝试
        success = len(result) > 0
        log_login_attempt(username, ip_address, success, user_agent)
        
        if result:
            # 登录成功
            user_info = {
                'id': result[0][0],
                'username': result[0][1],
                'email': result[0][3],
                'role': result[0][4]
            }
            
            # 如果查询返回多个结果（可能是注入攻击），显示所有结果
            if len(result) > 1:
                all_users = []
                for row in result:
                    all_users.append({
                        'id': row[0],
                        'username': row[1],
                        'password': row[2],  # ⚠️ 危险：泄露密码
                        'email': row[3],
                        'role': row[4]
                    })
                user_info = all_users
            
            conn.close()
            return jsonify({
                'success': True,
                'message': '登录成功',
                'user_info': user_info,
                'debug_info': f'SQL查询: {sql_query}\\n查询结果数量: {len(result)}'
            })
        else:
            # 登录失败
            conn.close()
            return jsonify({
                'success': False,
                'message': '用户名或密码错误',
                'debug_info': f'SQL查询: {sql_query}'
            })
            
    except sqlite3.Error as e:
        # SQL 错误（可能由于注入攻击导致）
        log_login_attempt(username, ip_address, False, user_agent)
        return jsonify({
            'success': False,
            'message': f'数据库错误: {str(e)}',
            'debug_info': f'SQL查询: {sql_query}\\n错误: {str(e)}'
        })

@app.route('/users')
def list_users():
    """列出所有用户（用于演示数据泄露）"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT id, username, email, role FROM users')
    users = cursor.fetchall()
    conn.close()
    
    user_list = []
    for user in users:
        user_list.append({
            'id': user[0],
            'username': user[1],
            'email': user[2],
            'role': user[3]
        })
    
    return jsonify({'users': user_list})

@app.route('/logs')
def view_logs():
    """查看登录日志"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT username, ip_address, success, timestamp, user_agent 
        FROM login_logs 
        ORDER BY timestamp DESC 
        LIMIT 50
    ''')
    logs = cursor.fetchall()
    conn.close()
    
    log_list = []
    for log in logs:
        log_list.append({
            'username': log[0],
            'ip_address': log[1],
            'success': bool(log[2]),
            'timestamp': log[3],
            'user_agent': log[4]
        })
    
    return jsonify({'logs': log_list})

@app.route('/reset-db')
def reset_database():
    """重置数据库"""
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
    init_database()
    return jsonify({'message': '数据库已重置'})

if __name__ == '__main__':
    print("🚀 启动存在 SQL 注入漏洞的 Flask 应用")
    print("⚠️  警告：此应用包含故意的安全漏洞，仅用于测试！")
    print("=" * 60)
    
    # 初始化数据库
    init_database()
    
    print("📊 可用的测试端点:")
    print("  - http://localhost:5000/ (登录页面)")
    print("  - http://localhost:5000/login (登录接口)")
    print("  - http://localhost:5000/users (用户列表)")
    print("  - http://localhost:5000/logs (登录日志)")
    print("  - http://localhost:5000/reset-db (重置数据库)")
    print()
    print("🔓 SQL 注入测试用例:")
    print("  用户名: ' OR 1=1 --")
    print("  密码: 任意")
    print("=" * 60)
    
    # 启动 Flask 应用
    app.run(debug=True, host='0.0.0.0', port=5000)
