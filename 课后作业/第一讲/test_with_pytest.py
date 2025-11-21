# -*- coding: utf-8 -*-
"""
使用pytest进行单元测试
测试有缺陷的函数
"""

import pytest
from defective_functions import divide, find_max, get_item


class TestDivideFunction:
    """测试divide函数"""
    
    def test_normal_divide(self):
        """正常除法测试"""
        assert divide(10, 2) == 5.0
        assert divide(7.5, 2.5) == 3.0
        assert divide(-10, 2) == -5.0
    
    def test_zero_dividend(self):
        """零除以非零数"""
        assert divide(0, 5) == 0.0
    
    def test_divide_by_zero(self):
        """除数为零应该抛出异常"""
        with pytest.raises(ZeroDivisionError):
            divide(10, 0)


class TestFindMaxFunction:
    """测试find_max函数"""
    
    def test_positive_numbers(self):
        """正数列表测试"""
        assert find_max([1, 5, 3, 9, 2]) == 9
    
    def test_with_zero(self):
        """包含零的列表"""
        assert find_max([0, -1, -5, -2]) == 0
    
    def test_negative_numbers(self):
        """全负数列表 - 这个测试会失败，暴露缺陷"""
        # 这个断言会失败，因为函数有缺陷
        assert find_max([-1, -5, -3, -2]) == -1
    
    def test_single_negative(self):
        """单个负数 - 这个测试会失败，暴露缺陷"""
        assert find_max([-42]) == -42
    
    def test_empty_list(self):
        """空列表测试"""
        # 这个函数对空列表的处理也有问题
        assert find_max([]) == 0  # 实际上应该抛出异常或有其他处理


class TestGetItemFunction:
    """测试get_item函数"""
    
    def test_normal_access(self):
        """正常索引访问"""
        assert get_item(['a', 'b', 'c', 'd'], 2) == 'c'
        assert get_item([1, 2, 3], 0) == 1
    
    def test_negative_index(self):
        """负索引测试"""
        assert get_item([1, 2, 3], -1) == 3
    
    def test_index_out_of_range(self):
        """索引越界应该抛出异常"""
        with pytest.raises(IndexError):
            get_item([1, 2, 3], 5)
    
    def test_empty_list_access(self):
        """空列表访问应该抛出异常"""
        with pytest.raises(IndexError):
            get_item([], 0)


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v"])
