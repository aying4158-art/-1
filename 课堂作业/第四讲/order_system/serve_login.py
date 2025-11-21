"""
简单的HTTP服务器，用于展示登录页面
"""

import http.server
import socketserver
import os
import webbrowser
import threading
import time

def start_server(port=8080):
    """启动HTTP服务器"""
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    handler = http.server.SimpleHTTPRequestHandler
    
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"🌐 HTTP服务器启动成功")
        print(f"📂 服务目录: {os.getcwd()}")
        print(f"🔗 登录页面: http://localhost:{port}/login.html")
        print(f"⚡ 按 Ctrl+C 停止服务器")
        print("=" * 50)
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print(f"\n🔚 服务器已停止")

def open_browser_delayed(url, delay=2):
    """延迟打开浏览器"""
    time.sleep(delay)
    webbrowser.open(url)

if __name__ == "__main__":
    port = 8080
    
    # 检查登录页面是否存在
    if not os.path.exists("login.html"):
        print("❌ 登录页面文件 login.html 不存在")
        exit(1)
    
    # 在后台线程中延迟打开浏览器
    url = f"http://localhost:{port}/login.html"
    browser_thread = threading.Thread(target=open_browser_delayed, args=(url,))
    browser_thread.daemon = True
    browser_thread.start()
    
    # 启动服务器
    start_server(port)
