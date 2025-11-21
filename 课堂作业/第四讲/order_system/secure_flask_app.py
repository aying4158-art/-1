"""
安全的 Flask 登录应用
✅ 使用参数化查询防止 SQL 注入
"""

import sqlite3
import hashlib
import os
from flask import Flask, request, jsonify, render_template_string
from datetime import datetime

app = Flask(__name__)

# 数据库文件路径
DB_FILE = 'secure_users.db'

def hash_password(password):
    """使用 SHA-256 哈希密码"""
    return hashlib.sha256(password.encode()).hexdigest()

def init_database():
    """初始化数据库和测试数据"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # 创建用户表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
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
    
    # 插入测试用户数据（密码已哈希）
    test_users = [
        ('admin', hash_password('admin123'), 'admin@example.com', 'admin'),
        ('user', hash_password('user123'), 'user@example.com', 'user'),
        ('test', hash_password('test123'), 'test@example.com', 'user'),
        ('alice', hash_password('alice456'), 'alice@example.com', 'user'),
        ('bob', hash_password('bob789'), 'bob@example.com', 'user'),
        ('manager', hash_password('manager123'), 'manager@example.com', 'manager'),
        ('guest', hash_password('guest123'), 'guest@example.com', 'guest')
    ]
    
    # 检查是否已有数据
    cursor.execute('SELECT COUNT(*) FROM users')
    if cursor.fetchone()[0] == 0:
        cursor.executemany(
            'INSERT INTO users (username, password_hash, email, role) VALUES (?, ?, ?, ?)',
            test_users
        )
        print("✅ 安全的测试用户数据已插入")
    
    conn.commit()
    conn.close()

def log_login_attempt(username, ip_address, success, user_agent):
    """记录登录尝试"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    # ✅ 使用参数化查询
    cursor.execute(
        'INSERT INTO login_logs (username, ip_address, success, user_agent) VALUES (?, ?, ?, ?)',
        (username, ip_address, success, user_agent)
    )
    conn.commit()
    conn.close()

def validate_input(username, password):
    """输入验证"""
    if not username or not password:
        return False, "用户名和密码不能为空"
    
    if len(username) > 50:
        return False, "用户名过长"
    
    if len(password) > 100:
        return False, "密码过长"
    
    # 检查是否包含可疑字符
    suspicious_chars = ["'", '"', ";", "--", "/*", "*/", "xp_", "sp_"]
    for char in suspicious_chars:
        if char in username or char in password:
            return False, f"输入包含不允许的字符: {char}"
    
    return True, ""

# 安全登录页面HTML模板
SECURE_LOGIN_TEMPLATE = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>安全的 Flask 登录接口</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
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
        .security-notice {
            background: #d1ecf1;
            border: 1px solid #bee5eb;
            color: #0c5460;
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
            background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
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
        .security-features {
            margin-top: 30px;
            background: #f8f9fa;
            padding: 20px;
            border-radius: 5px;
            border-left: 4px solid #28a745;
        }
        .security-features h3 {
            color: #28a745;
            margin-top: 0;
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
        <div class="security-notice">
            <strong>🔒 安全提示：</strong> 此应用使用了安全的编程实践，防止 SQL 注入攻击！
        </div>
        
        <div class="header">
            <h1>安全的 Flask 登录接口</h1>
            <p>防 SQL 注入演示</p>
        </div>
        
        <form id="loginForm">
            <div class="form-group">
                <label for="username">用户名：</label>
                <input type="text" id="username" name="username" required maxlength="50">
            </div>
            
            <div class="form-group">
                <label for="password">密码：</label>
                <input type="password" id="password" name="password" required maxlength="100">
            </div>
            
            <button type="submit">安全登录</button>
        </form>
        
        <div id="result" class="result"></div>
        
        <div class="test-accounts">
            <h3>🧪 测试账号</h3>
            <p><strong>管理员：</strong> admin / admin123</p>
            <p><strong>普通用户：</strong> user / user123</p>
            <p><strong>测试用户：</strong> test / test123</p>
        </div>
        
        <div class="security-features">
            <h3>🛡️ 安全特性</h3>
            <ul>
                <li>✅ 参数化查询防止 SQL 注入</li>
                <li>✅ 密码哈希存储</li>
                <li>✅ 输入验证和过滤</li>
                <li>✅ 长度限制</li>
                <li>✅ 可疑字符检测</li>
                <li>✅ 错误信息不泄露敏感信息</li>
            </ul>
            <p><em>尝试使用 SQL 注入攻击，系统会安全地拒绝</em></p>
        </div>
    </div>

    <script>
        document.getElementById('loginForm').addEventListener('submit', function(e) {
            e.preventDefault();
            
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            const resultDiv = document.getElementById('result');
            
            fetch('/secure-login', {
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
                        <p><strong>欢迎，${data.user_info.username}！</strong></p>
                        <p>角色: ${data.user_info.role}</p>
                        <p>邮箱: ${data.user_info.email}</p>
                    `;
                } else {
                    resultDiv.className = 'result error';
                    resultDiv.innerHTML = `
                        <h4>❌ 登录失败</h4>
                        <p>${data.message}</p>
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
    """主页 - 显示安全登录表单"""
    return render_template_string(SECURE_LOGIN_TEMPLATE)

@app.route('/secure-login', methods=['POST'])
def secure_login():
    """
    安全的登录接口
    ✅ 使用参数化查询防止 SQL 注入
    """
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    
    # 获取客户端信息
    ip_address = request.remote_addr
    user_agent = request.headers.get('User-Agent', '')
    
    # ✅ 输入验证
    is_valid, error_message = validate_input(username, password)
    if not is_valid:
        log_login_attempt(username, ip_address, False, user_agent)
        return jsonify({
            'success': False,
            'message': error_message
        })
    
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # ✅ 使用参数化查询防止 SQL 注入
        cursor.execute(
            'SELECT id, username, password_hash, email, role FROM users WHERE username = ?',
            (username,)
        )
        result = cursor.fetchone()
        
        if result:
            # 验证密码哈希
            stored_hash = result[2]
            input_hash = hash_password(password)
            
            if stored_hash == input_hash:
                # 登录成功
                user_info = {
                    'id': result[0],
                    'username': result[1],
                    'email': result[3],
                    'role': result[4]
                }
                
                log_login_attempt(username, ip_address, True, user_agent)
                conn.close()
                
                return jsonify({
                    'success': True,
                    'message': '登录成功',
                    'user_info': user_info
                })
            else:
                # 密码错误
                log_login_attempt(username, ip_address, False, user_agent)
                conn.close()
                return jsonify({
                    'success': False,
                    'message': '用户名或密码错误'  # 不透露具体是哪个字段错误
                })
        else:
            # 用户不存在
            log_login_attempt(username, ip_address, False, user_agent)
            conn.close()
            return jsonify({
                'success': False,
                'message': '用户名或密码错误'  # 不透露用户是否存在
            })
            
    except sqlite3.Error as e:
        # 数据库错误
        log_login_attempt(username, ip_address, False, user_agent)
        print(f"数据库错误: {e}")  # 仅在服务器端记录详细错误
        return jsonify({
            'success': False,
            'message': '系统错误，请稍后重试'  # 不向客户端泄露具体错误信息
        })

@app.route('/users')
def list_users():
    """列出用户（不包含密码哈希）"""
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
    return jsonify({'message': '安全数据库已重置'})

if __name__ == '__main__':
    print("🔒 启动安全的 Flask 应用")
    print("✅ 使用参数化查询防止 SQL 注入")
    print("=" * 60)
    
    # 初始化数据库
    init_database()
    
    print("📊 可用的测试端点:")
    print("  - http://localhost:5001/ (安全登录页面)")
    print("  - http://localhost:5001/secure-login (安全登录接口)")
    print("  - http://localhost:5001/users (用户列表)")
    print("  - http://localhost:5001/logs (登录日志)")
    print("  - http://localhost:5001/reset-db (重置数据库)")
    print()
    print("🛡️ 安全特性:")
    print("  - 参数化查询")
    print("  - 密码哈希")
    print("  - 输入验证")
    print("  - 错误信息不泄露")
    print("=" * 60)
    
    # 启动 Flask 应用（使用不同端口避免冲突）
    app.run(debug=True, host='0.0.0.0', port=5001)
