"""
启动 FastAPI 服务器的便捷脚本
"""

import uvicorn
from api import app

if __name__ == "__main__":
    print("=" * 60)
    print("订单系统 API 服务启动中...")
    print("=" * 60)
    print("\n服务地址:")
    print("  - API 根路径: http://localhost:8000")
    print("  - Swagger 文档: http://localhost:8000/docs")
    print("  - ReDoc 文档: http://localhost:8000/redoc")
    print("\n按 Ctrl+C 停止服务")
    print("=" * 60 + "\n")
    
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )
