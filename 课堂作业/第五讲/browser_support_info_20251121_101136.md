# 多浏览器测试支持说明

## 支持的浏览器

### 1. Microsoft Edge（推荐）
- **优势**: Windows系统内置，兼容性好
- **测试脚本**: `test_login_edge.py`
- **执行命令**: `python run_tests_edge.py`

### 2. Google Chrome
- **测试脚本**: `test_login_local.py`
- **执行命令**: `python run_tests_simple.py`

### 3. Firefox（可扩展）
- 可以创建类似的Firefox版本测试脚本

## EdgeDriver安装说明

如果遇到EdgeDriver问题，请：

1. **自动安装**（推荐）:
   ```bash
   pip install webdriver-manager
   ```

2. **手动安装**:
   - 访问: https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/
   - 下载对应Edge版本的EdgeDriver
   - 将EdgeDriver.exe放入系统PATH或项目目录

3. **检查Edge版本**:
   - 打开Edge浏览器
   - 地址栏输入: `edge://version/`
   - 查看版本号并下载对应的EdgeDriver

## 测试执行优先级

1. **首选**: Edge浏览器（Windows系统兼容性最好）
2. **备选**: Chrome浏览器
3. **手动**: 直接在浏览器中打开login.html测试

## 当前测试时间
2025年11月21日 10:11:36
