"""
SQL 注入攻击测试脚本
测试漏洞版本和安全版本的 Flask 应用
"""

import requests
import json
import time
from datetime import datetime

class SQLInjectionTester:
    """SQL 注入测试类"""
    
    def __init__(self):
        self.vulnerable_url = "http://localhost:5000"
        self.secure_url = "http://localhost:5001"
        self.test_results = []
        
        # SQL 注入测试用例
        self.injection_payloads = [
            {
                "name": "经典 OR 注入",
                "username": "' OR 1=1 --",
                "password": "anything",
                "description": "绕过登录验证，获取第一个用户信息"
            },
            {
                "name": "联合查询注入",
                "username": "' UNION SELECT id, username, password, email, role FROM users --",
                "password": "anything",
                "description": "尝试获取所有用户信息"
            },
            {
                "name": "注释绕过",
                "username": "admin'--",
                "password": "anything",
                "description": "注释掉密码验证部分"
            },
            {
                "name": "双引号注入",
                "username": '" OR "1"="1',
                "password": "anything",
                "description": "使用双引号的 OR 注入"
            },
            {
                "name": "布尔盲注",
                "username": "' OR '1'='1",
                "password": "anything",
                "description": "布尔型盲注攻击"
            },
            {
                "name": "时间盲注",
                "username": "'; WAITFOR DELAY '00:00:05' --",
                "password": "anything",
                "description": "时间延迟注入（SQLServer语法）"
            },
            {
                "name": "堆叠查询",
                "username": "admin'; DROP TABLE users; --",
                "password": "anything",
                "description": "尝试删除用户表"
            },
            {
                "name": "错误注入",
                "username": "' AND (SELECT COUNT(*) FROM users) > 0 --",
                "password": "anything",
                "description": "基于错误的信息泄露"
            }
        ]
        
        # 正常登录测试用例
        self.normal_login_tests = [
            {
                "name": "有效登录 - admin",
                "username": "admin",
                "password": "admin123",
                "description": "使用正确的管理员凭据"
            },
            {
                "name": "无效登录 - 错误密码",
                "username": "admin",
                "password": "wrongpassword",
                "description": "使用错误的密码"
            },
            {
                "name": "无效登录 - 不存在用户",
                "username": "nonexistent",
                "password": "password",
                "description": "使用不存在的用户名"
            }
        ]
    
    def test_endpoint(self, base_url, endpoint, payload, test_name):
        """测试单个端点"""
        url = f"{base_url}{endpoint}"
        
        test_result = {
            "test_name": test_name,
            "payload": payload,
            "url": url,
            "timestamp": datetime.now().isoformat(),
            "success": False,
            "response_data": None,
            "error": None,
            "response_time": 0,
            "status_code": None
        }
        
        try:
            start_time = time.time()
            
            response = requests.post(
                url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            test_result["response_time"] = round(time.time() - start_time, 3)
            test_result["status_code"] = response.status_code
            
            if response.status_code == 200:
                response_data = response.json()
                test_result["response_data"] = response_data
                test_result["success"] = response_data.get("success", False)
            else:
                test_result["error"] = f"HTTP {response.status_code}"
                
        except requests.exceptions.RequestException as e:
            test_result["error"] = str(e)
        except json.JSONDecodeError as e:
            test_result["error"] = f"JSON解析错误: {e}"
        except Exception as e:
            test_result["error"] = f"未知错误: {e}"
        
        return test_result
    
    def test_vulnerable_app(self):
        """测试存在漏洞的应用"""
        print("🔓 测试存在 SQL 注入漏洞的应用")
        print("=" * 50)
        
        vulnerable_results = []
        
        # 检查应用是否运行
        try:
            response = requests.get(f"{self.vulnerable_url}/", timeout=5)
            if response.status_code != 200:
                print("❌ 漏洞应用未运行，请先启动 vulnerable_flask_app.py")
                return []
        except:
            print("❌ 无法连接到漏洞应用 (http://localhost:5000)")
            print("   请先运行: python vulnerable_flask_app.py")
            return []
        
        print("✅ 漏洞应用连接成功")
        
        # 测试正常登录
        print("\n📝 测试正常登录功能...")
        for test_case in self.normal_login_tests:
            payload = {
                "username": test_case["username"],
                "password": test_case["password"]
            }
            
            result = self.test_endpoint(
                self.vulnerable_url, 
                "/login", 
                payload, 
                f"正常登录 - {test_case['name']}"
            )
            
            vulnerable_results.append(result)
            
            status = "✅ 成功" if result["success"] else "❌ 失败"
            print(f"  {status} {test_case['name']}")
        
        # 测试 SQL 注入攻击
        print("\n🔓 测试 SQL 注入攻击...")
        for injection in self.injection_payloads:
            payload = {
                "username": injection["username"],
                "password": injection["password"]
            }
            
            result = self.test_endpoint(
                self.vulnerable_url,
                "/login",
                payload,
                f"SQL注入 - {injection['name']}"
            )
            
            vulnerable_results.append(result)
            
            # 分析结果
            if result["success"]:
                print(f"  🚨 {injection['name']}: 注入成功！")
                if result["response_data"] and "user_info" in result["response_data"]:
                    user_info = result["response_data"]["user_info"]
                    if isinstance(user_info, list):
                        print(f"    💥 泄露了 {len(user_info)} 个用户的信息！")
                    else:
                        print(f"    💥 获取到用户信息: {user_info.get('username', 'unknown')}")
            elif result["error"]:
                print(f"  ⚠️  {injection['name']}: 引发错误 - {result['error']}")
            else:
                print(f"  ✅ {injection['name']}: 注入被阻止")
        
        return vulnerable_results
    
    def test_secure_app(self):
        """测试安全的应用"""
        print("\n🔒 测试安全的应用")
        print("=" * 50)
        
        secure_results = []
        
        # 检查应用是否运行
        try:
            response = requests.get(f"{self.secure_url}/", timeout=5)
            if response.status_code != 200:
                print("❌ 安全应用未运行，请先启动 secure_flask_app.py")
                return []
        except:
            print("❌ 无法连接到安全应用 (http://localhost:5001)")
            print("   请先运行: python secure_flask_app.py")
            return []
        
        print("✅ 安全应用连接成功")
        
        # 测试正常登录
        print("\n📝 测试正常登录功能...")
        for test_case in self.normal_login_tests:
            payload = {
                "username": test_case["username"],
                "password": test_case["password"]
            }
            
            result = self.test_endpoint(
                self.secure_url,
                "/secure-login",
                payload,
                f"正常登录 - {test_case['name']}"
            )
            
            secure_results.append(result)
            
            status = "✅ 成功" if result["success"] else "❌ 失败"
            print(f"  {status} {test_case['name']}")
        
        # 测试 SQL 注入攻击
        print("\n🛡️ 测试 SQL 注入防护...")
        for injection in self.injection_payloads:
            payload = {
                "username": injection["username"],
                "password": injection["password"]
            }
            
            result = self.test_endpoint(
                self.secure_url,
                "/secure-login",
                payload,
                f"SQL注入 - {injection['name']}"
            )
            
            secure_results.append(result)
            
            # 分析结果
            if result["success"]:
                print(f"  🚨 {injection['name']}: 意外成功！可能存在绕过")
            elif result["error"]:
                print(f"  ✅ {injection['name']}: 被安全拒绝")
            else:
                print(f"  ✅ {injection['name']}: 登录失败（正常）")
        
        return secure_results
    
    def analyze_results(self, vulnerable_results, secure_results):
        """分析测试结果"""
        print("\n📊 测试结果分析")
        print("=" * 60)
        
        # 统计漏洞应用结果
        vuln_successful_injections = 0
        vuln_total_injections = 0
        
        for result in vulnerable_results:
            if "SQL注入" in result["test_name"]:
                vuln_total_injections += 1
                if result["success"]:
                    vuln_successful_injections += 1
        
        # 统计安全应用结果
        secure_successful_injections = 0
        secure_total_injections = 0
        
        for result in secure_results:
            if "SQL注入" in result["test_name"]:
                secure_total_injections += 1
                if result["success"]:
                    secure_successful_injections += 1
        
        print(f"🔓 漏洞应用:")
        print(f"  - 总注入测试: {vuln_total_injections}")
        print(f"  - 成功注入: {vuln_successful_injections}")
        print(f"  - 成功率: {(vuln_successful_injections/vuln_total_injections*100):.1f}%" if vuln_total_injections > 0 else "  - 成功率: 0%")
        
        print(f"\n🔒 安全应用:")
        print(f"  - 总注入测试: {secure_total_injections}")
        print(f"  - 成功注入: {secure_successful_injections}")
        print(f"  - 成功率: {(secure_successful_injections/secure_total_injections*100):.1f}%" if secure_total_injections > 0 else "  - 成功率: 0%")
        
        # 详细分析
        print(f"\n🔍 详细分析:")
        
        print(f"\n漏洞应用中成功的注入:")
        for result in vulnerable_results:
            if "SQL注入" in result["test_name"] and result["success"]:
                print(f"  ✅ {result['test_name']}")
                if result["response_data"] and "user_info" in result["response_data"]:
                    user_info = result["response_data"]["user_info"]
                    if isinstance(user_info, list):
                        print(f"     💥 泄露了 {len(user_info)} 个用户信息")
                    else:
                        print(f"     💥 获取用户: {user_info.get('username', 'unknown')}")
        
        print(f"\n安全应用中被阻止的注入:")
        blocked_count = 0
        for result in secure_results:
            if "SQL注入" in result["test_name"] and not result["success"]:
                blocked_count += 1
        
        print(f"  🛡️ 成功阻止了 {blocked_count}/{secure_total_injections} 个注入攻击")
        
        return {
            "vulnerable_app": {
                "total_injections": vuln_total_injections,
                "successful_injections": vuln_successful_injections,
                "success_rate": (vuln_successful_injections/vuln_total_injections*100) if vuln_total_injections > 0 else 0
            },
            "secure_app": {
                "total_injections": secure_total_injections,
                "successful_injections": secure_successful_injections,
                "success_rate": (secure_successful_injections/secure_total_injections*100) if secure_total_injections > 0 else 0
            }
        }
    
    def generate_report(self, vulnerable_results, secure_results, analysis):
        """生成测试报告"""
        report = {
            "test_summary": {
                "timestamp": datetime.now().isoformat(),
                "total_tests": len(vulnerable_results) + len(secure_results),
                "vulnerable_app_tests": len(vulnerable_results),
                "secure_app_tests": len(secure_results)
            },
            "analysis": analysis,
            "vulnerable_app_results": vulnerable_results,
            "secure_app_results": secure_results,
            "injection_payloads": self.injection_payloads
        }
        
        # 保存 JSON 报告
        with open("sql_injection_test_report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        # 生成 HTML 报告
        self.generate_html_report(report)
        
        print(f"\n📄 报告已生成:")
        print(f"  - JSON: sql_injection_test_report.json")
        print(f"  - HTML: sql_injection_test_report.html")
    
    def generate_html_report(self, report):
        """生成 HTML 报告"""
        html_content = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SQL 注入测试报告</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .header {{ text-align: center; margin-bottom: 30px; }}
        .warning {{ background: #fff3cd; border: 1px solid #ffeaa7; color: #856404; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
        .summary {{ display: flex; justify-content: space-around; margin-bottom: 30px; }}
        .stat-card {{ background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; min-width: 150px; }}
        .vulnerable {{ border-left: 4px solid #dc3545; }}
        .secure {{ border-left: 4px solid #28a745; }}
        .stat-number {{ font-size: 2em; font-weight: bold; }}
        .vulnerable .stat-number {{ color: #dc3545; }}
        .secure .stat-number {{ color: #28a745; }}
        .results-section {{ margin-bottom: 30px; }}
        .results-table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
        .results-table th, .results-table td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
        .results-table th {{ background-color: #f8f9fa; }}
        .success {{ color: #28a745; font-weight: bold; }}
        .fail {{ color: #dc3545; font-weight: bold; }}
        .payload {{ font-family: monospace; background: #f8f9fa; padding: 2px 4px; border-radius: 3px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔒 SQL 注入安全测试报告</h1>
            <p>生成时间: {report['test_summary']['timestamp']}</p>
        </div>
        
        <div class="warning">
            <strong>⚠️ 重要提示：</strong> 此报告展示了 SQL 注入漏洞的危害性。请确保在生产环境中使用安全的编程实践！
        </div>
        
        <div class="summary">
            <div class="stat-card vulnerable">
                <div class="stat-number">{report['analysis']['vulnerable_app']['successful_injections']}/{report['analysis']['vulnerable_app']['total_injections']}</div>
                <div class="stat-label">漏洞应用 - 成功注入</div>
                <div class="stat-detail">{report['analysis']['vulnerable_app']['success_rate']:.1f}% 成功率</div>
            </div>
            <div class="stat-card secure">
                <div class="stat-number">{report['analysis']['secure_app']['successful_injections']}/{report['analysis']['secure_app']['total_injections']}</div>
                <div class="stat-label">安全应用 - 成功注入</div>
                <div class="stat-detail">{report['analysis']['secure_app']['success_rate']:.1f}% 成功率</div>
            </div>
        </div>
        
        <div class="results-section">
            <h2>🔓 漏洞应用测试结果</h2>
            <table class="results-table">
                <thead>
                    <tr>
                        <th>测试名称</th>
                        <th>用户名</th>
                        <th>密码</th>
                        <th>结果</th>
                        <th>响应时间</th>
                        <th>状态码</th>
                    </tr>
                </thead>
                <tbody>
"""
        
        for result in report['vulnerable_app_results']:
            status_class = "success" if result['success'] else "fail"
            status_text = "成功" if result['success'] else "失败"
            
            html_content += f"""
                    <tr>
                        <td>{result['test_name']}</td>
                        <td class="payload">{result['payload']['username']}</td>
                        <td class="payload">{result['payload']['password']}</td>
                        <td class="{status_class}">{status_text}</td>
                        <td>{result['response_time']}s</td>
                        <td>{result['status_code']}</td>
                    </tr>
"""
        
        html_content += """
                </tbody>
            </table>
        </div>
        
        <div class="results-section">
            <h2>🔒 安全应用测试结果</h2>
            <table class="results-table">
                <thead>
                    <tr>
                        <th>测试名称</th>
                        <th>用户名</th>
                        <th>密码</th>
                        <th>结果</th>
                        <th>响应时间</th>
                        <th>状态码</th>
                    </tr>
                </thead>
                <tbody>
"""
        
        for result in report['secure_app_results']:
            status_class = "success" if result['success'] else "fail"
            status_text = "成功" if result['success'] else "失败"
            
            html_content += f"""
                    <tr>
                        <td>{result['test_name']}</td>
                        <td class="payload">{result['payload']['username']}</td>
                        <td class="payload">{result['payload']['password']}</td>
                        <td class="{status_class}">{status_text}</td>
                        <td>{result['response_time']}s</td>
                        <td>{result['status_code']}</td>
                    </tr>
"""
        
        html_content += """
                </tbody>
            </table>
        </div>
        
        <div class="results-section">
            <h2>🔍 SQL 注入测试用例</h2>
            <table class="results-table">
                <thead>
                    <tr>
                        <th>攻击类型</th>
                        <th>用户名载荷</th>
                        <th>描述</th>
                    </tr>
                </thead>
                <tbody>
"""
        
        for payload in report['injection_payloads']:
            html_content += f"""
                    <tr>
                        <td>{payload['name']}</td>
                        <td class="payload">{payload['username']}</td>
                        <td>{payload['description']}</td>
                    </tr>
"""
        
        html_content += """
                </tbody>
            </table>
        </div>
    </div>
</body>
</html>
"""
        
        with open("sql_injection_test_report.html", "w", encoding="utf-8") as f:
            f.write(html_content)
    
    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始 SQL 注入安全测试")
        print("=" * 60)
        
        # 测试漏洞应用
        vulnerable_results = self.test_vulnerable_app()
        
        # 测试安全应用
        secure_results = self.test_secure_app()
        
        if vulnerable_results or secure_results:
            # 分析结果
            analysis = self.analyze_results(vulnerable_results, secure_results)
            
            # 生成报告
            self.generate_report(vulnerable_results, secure_results, analysis)
            
            print(f"\n🎉 测试完成！")
        else:
            print(f"\n❌ 无法连接到测试应用，请确保应用正在运行")


def main():
    """主函数"""
    print("🔒 SQL 注入安全测试工具")
    print("=" * 40)
    print("此工具将测试以下应用:")
    print("  - 漏洞应用: http://localhost:5000 (vulnerable_flask_app.py)")
    print("  - 安全应用: http://localhost:5001 (secure_flask_app.py)")
    print()
    print("请确保两个应用都在运行，然后按 Enter 继续...")
    input()
    
    tester = SQLInjectionTester()
    tester.run_all_tests()


if __name__ == "__main__":
    main()
