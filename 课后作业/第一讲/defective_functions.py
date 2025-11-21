# -*- coding: utf-8 -*-
"""
有缺陷的Python函数示例
包含3个存在缺陷的函数，用于测试练习
"""

def divide(a, b):
    """
    除法函数
    缺陷1: 未检查除数为0的情况
    """
    return a / b

def find_max(lst):
    """
    查找列表中的最大值
    缺陷2: 如果列表全是负数，返回结果错误
    """
    max_val = 0
    for x in lst:
        if x > max_val:
            max_val = x
    return max_val

def get_item(lst, idx):
    """
    获取列表中指定索引的元素
    缺陷3: 未检查索引越界
    """
    return lst[idx]
