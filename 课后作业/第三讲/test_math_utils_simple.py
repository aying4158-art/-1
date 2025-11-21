# -*- coding: utf-8 -*-
"""
数学工具库的简化pytest单元测试
只包含3个测试用例，每个覆盖至少两个逻辑分支
"""

import pytest
from math_utils import MathUtils

class TestMathUtilsSimple:
    """简化的数学工具类测试 - 只有3个测试用例"""
    
    def test_factorial_branches(self):
        """
        测试用例1: 阶乘函数的多个分支
        覆盖分支:
        1. 基础情况分支 (n=0, n=1)
        2. 递归计算分支 (n>1)
        3. 错误处理分支 (负数输入)
        """
        # 分支1: 基础情况
        assert MathUtils.factorial(0) == 1  # n=0
        assert MathUtils.factorial(1) == 1  # n=1
        
        # 分支2: 递归计算
        assert MathUtils.factorial(5) == 120  # n>1
        assert MathUtils.factorial(4) == 24   # n>1
        
        # 分支3: 错误处理
        with pytest.raises(ValueError, match="输入必须是非负整数"):
            MathUtils.factorial(-1)
    
    def test_is_prime_branches(self):
        """
        测试用例2: 质数判断函数的多个分支
        覆盖分支:
        1. 小数分支 (n<2)
        2. 特殊情况分支 (n=2)
        3. 偶数分支 (n%2==0)
        4. 奇数检查分支 (奇数质数和合数)
        """
        # 分支1: 小于2的数不是质数
        assert MathUtils.is_prime(0) == False
        assert MathUtils.is_prime(1) == False
        
        # 分支2: 2是质数
        assert MathUtils.is_prime(2) == True
        
        # 分支3: 偶数不是质数（除了2）
        assert MathUtils.is_prime(4) == False
        assert MathUtils.is_prime(8) == False
        
        # 分支4: 奇数检查
        assert MathUtils.is_prime(7) == True   # 奇数质数
        assert MathUtils.is_prime(9) == False  # 奇数合数
    
    def test_average_branches(self):
        """
        测试用例3: 平均值函数的多个分支
        覆盖分支:
        1. 空列表错误分支
        2. 类型检查错误分支
        3. 正常计算分支
        """
        # 分支1: 空列表
        with pytest.raises(ValueError, match="列表不能为空"):
            MathUtils.average([])
        
        # 分支2: 类型检查错误
        with pytest.raises(TypeError, match="列表中必须都是数字"):
            MathUtils.average([1, 2, "3"])
        
        # 分支3: 正常计算
        assert MathUtils.average([1, 2, 3]) == 2.0
        assert MathUtils.average([1, 5]) == 3.0
        assert MathUtils.average([2.5, 3.5]) == 3.0


def test_coverage_summary():
    """显示测试覆盖情况"""
    print("\n" + "="*50)
    print("简化测试用例覆盖情况")
    print("="*50)
    
    coverage_info = {
        "测试用例1 - factorial": {
            "覆盖分支": ["基础情况(n=0,1)", "递归计算(n>1)", "错误处理(负数)"],
            "分支数": 3
        },
        "测试用例2 - is_prime": {
            "覆盖分支": ["小数(<2)", "特殊情况(=2)", "偶数", "奇数检查"],
            "分支数": 4
        },
        "测试用例3 - average": {
            "覆盖分支": ["空列表", "类型检查", "正常计算"],
            "分支数": 3
        }
    }
    
    total_branches = sum(info["分支数"] for info in coverage_info.values())
    
    print(f"总测试用例数: 3")
    print(f"总覆盖分支数: {total_branches}")
    print("\n各测试用例详情:")
    
    for test_name, info in coverage_info.items():
        print(f"\n{test_name}:")
        print(f"  覆盖分支数: {info['分支数']}")
        print(f"  覆盖分支: {', '.join(info['覆盖分支'])}")
    
    print("\n" + "="*50)

    print("="*50)


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v"])
    
    # 显示覆盖情况
    test_coverage_summary()
