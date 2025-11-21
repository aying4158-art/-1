import sys
import traceback
from defective_functions import divide, find_max, get_item

class TestResult:
    def __init__(self):
        self.test_cases = []
        self.passed = 0
        self.failed = 0
        self.errors = 0
    
    def add_test(self, function_name, test_name, input_data, expected, actual, status, error_msg=""):
        self.test_cases.append({
            'function': function_name,
            'test_name': test_name,
            'input': input_data,
            'expected': expected,
            'actual': actual,
            'status': status,
            'error': error_msg
        })
        if status == 'PASS':
            self.passed += 1
        elif status == 'FAIL':
            self.failed += 1
        else:
            self.errors += 1

def run_test(func, test_name, inputs, expected, test_result):
    try:
        if isinstance(inputs, tuple):
            actual = func(*inputs)
        else:
            actual = func(inputs)
        
        if actual == expected:
            status = 'PASS'
            error_msg = ""
        else:
            status = 'FAIL'
            error_msg = f"Expected {expected}, got {actual}"
        
        test_result.add_test(func.__name__, test_name, inputs, expected, actual, status, error_msg)
        
    except Exception as e:
        status = 'ERROR'
        error_msg = f"{type(e).__name__}: {str(e)}"
        test_result.add_test(func.__name__, test_name, inputs, expected, str(e), status, error_msg)

def test_divide_function():
    """测试divide函数的测试用例"""
    print("=" * 50)
    print("测试 divide 函数")
    print("=" * 50)
    
    test_result = TestResult()
    
    # 测试用例1: 正常除法
    run_test(divide, "正常除法", (10, 2), 5.0, test_result)
    
    # 测试用例2: 浮点数除法
    run_test(divide, "浮点数除法", (7.5, 2.5), 3.0, test_result)
    
    # 测试用例3: 除数为零 (暴露缺陷)
    run_test(divide, "除数为零", (10, 0), "ZeroDivisionError", test_result)
    
    # 测试用例4: 零除以非零数
    run_test(divide, "零除以非零数", (0, 5), 0.0, test_result)
    
    # 测试用例5: 负数除法
    run_test(divide, "负数除法", (-10, 2), -5.0, test_result)
    
    return test_result

def test_find_max_function():
    """测试find_max函数的测试用例"""
    print("=" * 50)
    print("测试 find_max 函数")
    print("=" * 50)
    
    test_result = TestResult()
    
    # 测试用例1: 正常正数列表
    run_test(find_max, "正常正数列表", [1, 5, 3, 9, 2], 9, test_result)
    
    # 测试用例2: 全负数列表 (暴露缺陷)
    run_test(find_max, "全负数列表", [-1, -5, -3, -2], -1, test_result)
    
    # 测试用例3: 单元素负数列表 (暴露缺陷)
    run_test(find_max, "单元素负数列表", [-42], -42, test_result)
    
    # 测试用例4: 包含零的列表
    run_test(find_max, "包含零的列表", [0, -1, -5, -2], 0, test_result)
    
    # 测试用例5: 空列表
    run_test(find_max, "空列表", [], "应该处理空列表", test_result)
    
    return test_result

def test_get_item_function():
    """测试get_item函数的测试用例"""
    print("=" * 50)
    print("测试 get_item 函数")
    print("=" * 50)
    
    test_result = TestResult()
    
    # 测试用例1: 正常索引访问
    run_test(get_item, "正常索引访问", (['a', 'b', 'c', 'd'], 2), 'c', test_result)
    
    # 测试用例2: 第一个元素
    run_test(get_item, "第一个元素", ([1, 2, 3], 0), 1, test_result)
    
    # 测试用例3: 负索引
    run_test(get_item, "负索引", ([1, 2, 3], -1), 3, test_result)
    
    # 测试用例4: 索引越界 (暴露缺陷)
    run_test(get_item, "索引越界", ([1, 2, 3], 5), "IndexError", test_result)
    
    # 测试用例5: 空列表访问 (暴露缺陷)
    run_test(get_item, "空列表访问", ([], 0), "IndexError", test_result)
    
    return test_result

def print_test_results(test_result, function_name):
    """打印测试结果"""
    print(f"\n{function_name} 函数测试结果:")
    print(f"总测试用例: {len(test_result.test_cases)}")
    print(f"通过: {test_result.passed}")
    print(f"失败: {test_result.failed}")
    print(f"错误: {test_result.errors}")
    print("-" * 50)
    
    for test_case in test_result.test_cases:
        status_symbol = "✓" if test_case['status'] == 'PASS' else "✗"
        print(f"{status_symbol} {test_case['test_name']}: {test_case['status']}")
        print(f"  输入: {test_case['input']}")
        print(f"  期望: {test_case['expected']}")
        print(f"  实际: {test_case['actual']}")
        if test_case['error']:
            print(f"  错误: {test_case['error']}")
        print()

def main():
    print("开始执行缺陷函数测试")
    print("=" * 80)
    
    # 测试所有函数
    divide_results = test_divide_function()
    find_max_results = test_find_max_function()
    get_item_results = test_get_item_function()
    
    # 打印详细结果
    print_test_results(divide_results, "divide")
    print_test_results(find_max_results, "find_max")
    print_test_results(get_item_results, "get_item")
    
    # 总结
    total_tests = len(divide_results.test_cases) + len(find_max_results.test_cases) + len(get_item_results.test_cases)
    total_passed = divide_results.passed + find_max_results.passed + get_item_results.passed
    total_failed = divide_results.failed + find_max_results.failed + get_item_results.failed
    total_errors = divide_results.errors + find_max_results.errors + get_item_results.errors
    
    print("=" * 80)
    print("测试总结:")
    print(f"总测试用例: {total_tests}")
    print(f"通过: {total_passed}")
    print(f"失败: {total_failed}")
    print(f"错误: {total_errors}")
    print(f"成功率: {(total_passed/total_tests)*100:.1f}%")
    
    return {
        'divide': divide_results,
        'find_max': find_max_results,
        'get_item': get_item_results,
        'summary': {
            'total': total_tests,
            'passed': total_passed,
            'failed': total_failed,
            'errors': total_errors
        }
    }

if __name__ == "__main__":
    results = main()
