"""
字符串工具模块
包含各种字符串处理函数
"""


def is_palindrome(text):
    """
    判断字符串是否为回文
    
    Args:
        text (str): 要检查的字符串
        
    Returns:
        bool: 如果是回文返回True，否则返回False
        
    Raises:
        TypeError: 如果输入不是字符串类型
    """
    if not isinstance(text, str):
        raise TypeError("输入必须是字符串类型")
    if not text:
        return True

    # 转换为小写并移除空格和标点符号，只保留字母和数字
    cleaned_text = ''.join(char.lower() for char in text if char.isalnum())

    # 检查清理后的字符串是否与其反转相等
    return cleaned_text == cleaned_text[::-1]


def reverse_string(text):
    """
    反转字符串
    
    Args:
        text (str): 要反转的字符串
        
    Returns:
        str: 反转后的字符串
        
    Raises:
        TypeError: 如果输入不是字符串类型
    """
    if not isinstance(text, str):
        raise TypeError("输入必须是字符串类型")

    return text[::-1]


def count_vowels(text):
    """
    计算字符串中元音字母的数量
    
    Args:
        text (str): 要检查的字符串
        
    Returns:
        int: 元音字母的数量
        
    Raises:
        TypeError: 如果输入不是字符串类型
    """
    if not isinstance(text, str):
        raise TypeError("输入必须是字符串类型")

    vowels = 'aeiouAEIOU'
    return sum(1 for char in text if char in vowels)


def capitalize_words(text):
    """
    将字符串中每个单词的首字母大写
    
    Args:
        text (str): 要处理的字符串
        
    Returns:
        str: 处理后的字符串
        
    Raises:
        TypeError: 如果输入不是字符串类型
    """
    if not isinstance(text, str):
        raise TypeError("输入必须是字符串类型")

    return text.title()
