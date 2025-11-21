# 账户转账功能测试

## 项目简介

本项目实现了一个简单的账户转账功能，并使用 pytest 和 unittest.mock 进行全面测试。

## 功能特性

- ✅ 账户余额管理
- ✅ 转账功能（支持跨账户转账）
- ✅ 异常处理（余额不足、负数金额等）
- ✅ 完整的单元测试覆盖

## 项目结构

```
.
├── account.py          # 账户和转账功能实现
├── test_account.py     # 测试套件
├── pytest.ini          # pytest 配置文件
├── requirements.txt    # 依赖包列表
└── README.md          # 项目说明文档
```

## 安装依赖

```bash
pip install -r requirements.txt
```

## 运行测试

### 运行所有测试
```bash
pytest
```

### 运行特定测试文件
```bash
pytest test_account.py
```

### 运行特定测试类
```bash
pytest test_account.py::TestTransferNormalCases
```

### 运行特定测试方法
```bash
pytest test_account.py::TestTransferNormalCases::test_transfer_success
```

### 显示详细输出
```bash
pytest -v
```

### 显示测试覆盖率
```bash
pytest --cov=account --cov-report=html
```

### 显示打印输出
```bash
pytest -s
```

## 测试覆盖

### 测试点

1. **正常转账场景**
   - ✅ 正常转账成功
   - ✅ 转账金额等于余额
   - ✅ 小额转账
   - ✅ 大额转账

2. **余额不足场景**
   - ✅ 余额不足时抛出异常
   - ✅ 零余额转账
   - ✅ 余额略微不足

3. **负数金额场景**
   - ✅ 负数金额转账
   - ✅ 零金额转账
   - ✅ 极小负数金额

4. **使用 Mock 测试**
   - ✅ 验证方法调用
   - ✅ 验证调用顺序
   - ✅ 使用 patch 装饰器

5. **边界条件**
   - ✅ 无效账户类型
   - ✅ None 账户
   - ✅ 同一账户转账
   - ✅ 浮点数精度

6. **多次操作**
   - ✅ 多次转账
   - ✅ 转账链失败处理

7. **参数化测试**
   - ✅ 不同金额的转账
   - ✅ 各种无效金额

## 使用示例

```python
from account import Account, transfer

# 创建账户
account_a = Account("A001", 1000)
account_b = Account("B001", 500)

# 转账
transfer(account_a, account_b, 200)

print(f"账户A余额: {account_a.balance}")  # 800
print(f"账户B余额: {account_b.balance}")  # 700
```

## 异常处理

### InsufficientBalanceError
当账户余额不足时抛出：
```python
from account import Account, transfer, InsufficientBalanceError

account_a = Account("A001", 100)
account_b = Account("B001", 0)

try:
    transfer(account_a, account_b, 200)
except InsufficientBalanceError as e:
    print(f"转账失败: {e}")
```

### InvalidAmountError
当转账金额无效（负数或零）时抛出：
```python
from account import Account, transfer, InvalidAmountError

account_a = Account("A001", 1000)
account_b = Account("B001", 0)

try:
    transfer(account_a, account_b, -100)
except InvalidAmountError as e:
    print(f"转账失败: {e}")
```

## 工具和技术

- **Python 3.x**
- **pytest**: 测试框架
- **unittest.mock**: Mock 对象和补丁
- **VS Code**: 开发环境
- **Python 插件**: VS Code Python 扩展

## 测试最佳实践

1. **使用描述性的测试名称**: 测试方法名清楚地描述了测试内容
2. **测试隔离**: 每个测试独立运行，不依赖其他测试
3. **使用 fixtures**: 复用测试数据和设置
4. **参数化测试**: 使用 `@pytest.mark.parametrize` 测试多种输入
5. **Mock 使用**: 使用 Mock 验证方法调用和顺序
6. **异常测试**: 使用 `pytest.raises` 测试异常情况
7. **边界条件**: 测试极端情况和边界值

## 许可证

MIT License
