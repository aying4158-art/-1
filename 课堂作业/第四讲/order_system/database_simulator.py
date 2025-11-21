"""
数据库连接模拟器
用于模拟数据库连接中断和恢复的情况
"""

import time
import threading
from typing import Dict, Any, Optional
from enum import Enum


class ConnectionStatus(Enum):
    """连接状态枚举"""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    ERROR = "error"


class DatabaseConnectionError(Exception):
    """数据库连接异常"""
    pass


class DatabaseOperationError(Exception):
    """数据库操作异常"""
    pass


class DatabaseSimulator:
    """数据库模拟器"""
    
    def __init__(self):
        """初始化数据库模拟器"""
        self.status = ConnectionStatus.CONNECTED
        self.connection_count = 0
        self.operation_count = 0
        self.error_count = 0
        self.last_error: Optional[str] = None
        self.last_operation_time: Optional[float] = None
        self._lock = threading.Lock()
        
        # 模拟数据存储
        self._data: Dict[str, Any] = {}
        
        # 连接配置
        self.max_retry_attempts = 3
        self.retry_delay = 1.0  # 秒
        self.connection_timeout = 5.0  # 秒
        
    def connect(self) -> bool:
        """
        连接数据库
        
        Returns:
            是否连接成功
        """
        with self._lock:
            if self.status == ConnectionStatus.CONNECTED:
                return True
                
            self.status = ConnectionStatus.CONNECTING
            self.connection_count += 1
            
            # 模拟连接延迟
            time.sleep(0.1)
            
            # 模拟连接成功
            self.status = ConnectionStatus.CONNECTED
            self.last_error = None
            return True
    
    def disconnect(self) -> None:
        """断开数据库连接"""
        with self._lock:
            self.status = ConnectionStatus.DISCONNECTED
            self.last_error = "Connection manually disconnected"
    
    def simulate_connection_failure(self) -> None:
        """模拟连接失败"""
        with self._lock:
            self.status = ConnectionStatus.ERROR
            self.error_count += 1
            self.last_error = "Simulated connection failure"
    
    def is_connected(self) -> bool:
        """检查是否已连接"""
        return self.status == ConnectionStatus.CONNECTED
    
    def execute_query(self, query: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        执行数据库查询
        
        Args:
            query: SQL查询语句
            params: 查询参数
            
        Returns:
            查询结果
            
        Raises:
            DatabaseConnectionError: 连接异常
            DatabaseOperationError: 操作异常
        """
        with self._lock:
            self.operation_count += 1
            self.last_operation_time = time.time()
            
            # 检查连接状态
            if not self.is_connected():
                self.error_count += 1
                self.last_error = f"Database not connected. Status: {self.status.value}"
                raise DatabaseConnectionError(self.last_error)
            
            # 模拟查询延迟
            time.sleep(0.05)
            
            # 模拟查询操作
            if query.upper().startswith('SELECT'):
                return self._handle_select(query, params)
            elif query.upper().startswith('INSERT'):
                return self._handle_insert(query, params)
            elif query.upper().startswith('UPDATE'):
                return self._handle_update(query, params)
            elif query.upper().startswith('DELETE'):
                return self._handle_delete(query, params)
            else:
                return {"status": "success", "message": "Query executed"}
    
    def _handle_select(self, query: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """处理SELECT查询"""
        # 简单模拟：返回一些数据
        return {
            "status": "success",
            "data": list(self._data.values()),
            "count": len(self._data)
        }
    
    def _handle_insert(self, query: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """处理INSERT查询"""
        if params:
            key = params.get('id', f"record_{len(self._data) + 1}")
            self._data[key] = params
        
        return {
            "status": "success",
            "message": "Record inserted",
            "affected_rows": 1
        }
    
    def _handle_update(self, query: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """处理UPDATE查询"""
        affected_rows = 0
        if params and 'id' in params:
            key = params['id']
            if key in self._data:
                self._data[key].update(params)
                affected_rows = 1
        
        return {
            "status": "success",
            "message": "Record updated",
            "affected_rows": affected_rows
        }
    
    def _handle_delete(self, query: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """处理DELETE查询"""
        affected_rows = 0
        if params and 'id' in params:
            key = params['id']
            if key in self._data:
                del self._data[key]
                affected_rows = 1
        
        return {
            "status": "success",
            "message": "Record deleted",
            "affected_rows": affected_rows
        }
    
    def begin_transaction(self) -> str:
        """开始事务"""
        if not self.is_connected():
            raise DatabaseConnectionError("Cannot start transaction: not connected")
        
        transaction_id = f"txn_{int(time.time() * 1000)}"
        return transaction_id
    
    def commit_transaction(self, transaction_id: str) -> bool:
        """提交事务"""
        if not self.is_connected():
            raise DatabaseConnectionError("Cannot commit transaction: not connected")
        
        # 模拟提交延迟
        time.sleep(0.02)
        return True
    
    def rollback_transaction(self, transaction_id: str) -> bool:
        """回滚事务"""
        if not self.is_connected():
            raise DatabaseConnectionError("Cannot rollback transaction: not connected")
        
        # 模拟回滚延迟
        time.sleep(0.02)
        return True
    
    def get_connection_info(self) -> Dict[str, Any]:
        """获取连接信息"""
        return {
            "status": self.status.value,
            "connection_count": self.connection_count,
            "operation_count": self.operation_count,
            "error_count": self.error_count,
            "last_error": self.last_error,
            "last_operation_time": self.last_operation_time,
            "data_records": len(self._data)
        }
    
    def reset_stats(self) -> None:
        """重置统计信息"""
        with self._lock:
            self.connection_count = 0
            self.operation_count = 0
            self.error_count = 0
            self.last_error = None
            self.last_operation_time = None
    
    def clear_data(self) -> None:
        """清空数据"""
        with self._lock:
            self._data.clear()


class DatabaseManager:
    """数据库管理器 - 包含重连机制"""
    
    def __init__(self, db_simulator: DatabaseSimulator):
        """
        初始化数据库管理器
        
        Args:
            db_simulator: 数据库模拟器实例
        """
        self.db = db_simulator
        self.auto_reconnect = True
        self.max_retry_attempts = 3
        self.retry_delay = 1.0
    
    def execute_with_retry(self, query: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        带重试机制的查询执行
        
        Args:
            query: SQL查询语句
            params: 查询参数
            
        Returns:
            查询结果
            
        Raises:
            DatabaseConnectionError: 重试后仍然连接失败
            DatabaseOperationError: 操作失败
        """
        last_error = None
        
        for attempt in range(self.max_retry_attempts):
            try:
                # 检查连接状态
                if not self.db.is_connected() and self.auto_reconnect:
                    print(f"尝试重新连接数据库 (第 {attempt + 1} 次)")
                    if not self.db.connect():
                        raise DatabaseConnectionError("Failed to reconnect to database")
                
                # 执行查询
                result = self.db.execute_query(query, params)
                return result
                
            except DatabaseConnectionError as e:
                last_error = e
                print(f"数据库连接错误 (第 {attempt + 1} 次尝试): {e}")
                
                if attempt < self.max_retry_attempts - 1:
                    print(f"等待 {self.retry_delay} 秒后重试...")
                    time.sleep(self.retry_delay)
                    continue
                else:
                    print("达到最大重试次数，放弃操作")
                    break
            
            except Exception as e:
                # 其他异常不重试
                raise DatabaseOperationError(f"Database operation failed: {e}")
        
        # 所有重试都失败了
        raise DatabaseConnectionError(f"Failed to execute query after {self.max_retry_attempts} attempts. Last error: {last_error}")
    
    def execute_transaction(self, operations: list) -> bool:
        """
        执行事务
        
        Args:
            operations: 操作列表，每个操作是 (query, params) 元组
            
        Returns:
            是否成功
        """
        transaction_id = None
        
        try:
            # 开始事务
            transaction_id = self.db.begin_transaction()
            print(f"开始事务: {transaction_id}")
            
            # 执行所有操作
            for query, params in operations:
                result = self.execute_with_retry(query, params)
                print(f"执行操作: {query[:50]}... -> {result.get('status', 'unknown')}")
            
            # 提交事务
            self.db.commit_transaction(transaction_id)
            print(f"事务提交成功: {transaction_id}")
            return True
            
        except Exception as e:
            print(f"事务执行失败: {e}")
            
            # 回滚事务
            if transaction_id:
                try:
                    self.db.rollback_transaction(transaction_id)
                    print(f"事务回滚成功: {transaction_id}")
                except Exception as rollback_error:
                    print(f"事务回滚失败: {rollback_error}")
            
            raise e
