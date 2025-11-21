# -*- coding: utf-8 -*-
"""
密码验证函数实现
函数: isValidPassword(s: str) -> bool
要求: 长度6-12位，必须包含数字和字母
"""

import re

def isValidPassword(s: str) -> bool:
    """
    验证密码是否符合要求
    
    参数:
        s (str): 待验证的密码字符串
    
    返回:
        bool: 密码有效返回True，无效返回False
    
    规则:
        1. 长度必须在6-12位之间
        2. 必须包含至少一个数字
        3. 必须包含至少一个字母（大小写均可）
    """
    # 检查输入是否为字符串
    if not isinstance(s, str):
        return False
    
    # 检查长度
    if len(s) < 6 or len(s) > 12:
        return False
    
    # 检查是否包含数字
    has_digit = any(c.isdigit() for c in s)
    if not has_digit:
        return False
    
    # 检查是否包含字母
    has_letter = any(c.isalpha() for c in s)
    if not has_letter:
        return False
    
    return True
