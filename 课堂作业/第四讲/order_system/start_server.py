"""
启动订单系统API服务的脚本
解决导入问题
"""

import sys
import os

# 添加父目录到Python路径，这样可以导入order_system包
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

import uvicorn

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
    
    # 使用模块路径启动
    uvicorn.run(
        "order_system.api:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )
