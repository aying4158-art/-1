# -*- coding: utf-8 -*-
"""
数学工具库 - 一个简单的开源Python项目示例
包含常用的数学计算函数
"""

import math
from typing import List, Union

class MathUtils:
    """数学工具类"""
    
    @staticmethod
    def factorial(n: int) -> int:
        """
        计算阶乘
        
        Args:
            n (int): 非负整数
            
        Returns:
            int: n的阶乘
            
        Raises:
            ValueError: 当n为负数时
            TypeError: 当n不是整数时
        """
        if not isinstance(n, int):
            raise TypeError("输入必须是整数")
        
        if n < 0:
            raise ValueError("输入必须是非负整数")
        
        if n == 0 or n == 1:  # 分支1: 基础情况
            return 1
        else:  # 分支2: 递归情况
            result = 1
            for i in range(2, n + 1):
                result *= i
            return result
    
    @staticmethod
    def is_prime(n: int) -> bool:
        """
        判断是否为质数
        
        Args:
            n (int): 待判断的整数
            
        Returns:
            bool: 是质数返回True，否则返回False
        """
        if not isinstance(n, int):
            return False
        
        if n < 2:  # 分支1: 小于2的数不是质数
            return False
        
        if n == 2:  # 分支2: 2是质数
            return True
        
        if n % 2 == 0:  # 分支3: 偶数不是质数（除了2）
            return False
        
        # 分支4: 检查奇数因子
        for i in range(3, int(math.sqrt(n)) + 1, 2):
            if n % i == 0:
                return False
        
        return True
    
    @staticmethod
    def gcd(a: int, b: int) -> int:
        """
        计算最大公约数（使用欧几里得算法）
        
        Args:
            a (int): 第一个整数
            b (int): 第二个整数
            
        Returns:
            int: 最大公约数
        """
        a, b = abs(a), abs(b)
        
        if b == 0:  # 分支1: 递归终止条件
            return a
        else:  # 分支2: 递归继续
            return MathUtils.gcd(b, a % b)
    
    @staticmethod
    def fibonacci(n: int) -> int:
        """
        计算斐波那契数列第n项
        
        Args:
            n (int): 项数（从0开始）
            
        Returns:
            int: 第n项的值
            
        Raises:
            ValueError: 当n为负数时
        """
        if n < 0:
            raise ValueError("n必须是非负整数")
        
        if n <= 1:  # 分支1: 基础情况
            return n
        
        # 分支2: 迭代计算
        a, b = 0, 1
        for _ in range(2, n + 1):
            a, b = b, a + b
        return b
    
    @staticmethod
    def average(numbers: List[Union[int, float]]) -> float:
        """
        计算平均值
        
        Args:
            numbers (List[Union[int, float]]): 数字列表
            
        Returns:
            float: 平均值
            
        Raises:
            ValueError: 当列表为空时
            TypeError: 当列表包含非数字类型时
        """
        if not numbers:  # 分支1: 空列表
            raise ValueError("列表不能为空")
        
        # 分支2: 检查类型
        for num in numbers:
            if not isinstance(num, (int, float)):
                raise TypeError("列表中必须都是数字")
        
        # 分支3: 计算平均值
        return sum(numbers) / len(numbers)
    
    @staticmethod
    def power(base: Union[int, float], exponent: int) -> Union[int, float]:
        """
        计算幂运算
        
        Args:
            base (Union[int, float]): 底数
            exponent (int): 指数
            
        Returns:
            Union[int, float]: 幂运算结果
        """
        if exponent == 0:  # 分支1: 指数为0
            return 1
        elif exponent > 0:  # 分支2: 正指数
            result = 1
            for _ in range(exponent):
                result *= base
            return result
        else:  # 分支3: 负指数
            return 1 / MathUtils.power(base, -exponent)
