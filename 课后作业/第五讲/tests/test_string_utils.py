"""
字符串工具模块的单元测试
"""

import pytest
from src.string_utils import is_palindrome, reverse_string, count_vowels, capitalize_words


class TestIsPalindrome:
    """测试is_palindrome函数"""
    
    def test_simple_palindrome(self):
        """测试简单回文"""
        assert is_palindrome("aba") is True
        assert is_palindrome("racecar") is True
        assert is_palindrome("level") is True
    
    def test_non_palindrome(self):
        """测试非回文"""
        assert is_palindrome("hello") is False
        assert is_palindrome("python") is False
        assert is_palindrome("test") is False
    
    def test_empty_string(self):
        """测试空字符串"""
        assert is_palindrome("") is True
    
    def test_single_character(self):
        """测试单个字符"""
        assert is_palindrome("a") is True
        assert is_palindrome("Z") is True
    
    def test_case_insensitive(self):
        """测试大小写不敏感"""
        assert is_palindrome("Aba") is True
        assert is_palindrome("RaceCar") is True
        assert is_palindrome("LEVEL") is True
    
    def test_palindrome_with_spaces(self):
        """测试包含空格的回文"""
        assert is_palindrome("a man a plan a canal panama") is True
        assert is_palindrome("race a car") is False
    
    def test_palindrome_with_punctuation(self):
        """测试包含标点符号的回文"""
        assert is_palindrome("A man, a plan, a canal: Panama") is True
        assert is_palindrome("race a car!") is False
    
    def test_numeric_palindrome(self):
        """测试数字回文"""
        assert is_palindrome("12321") is True
        assert is_palindrome("12345") is False
    
    def test_mixed_alphanumeric(self):
        """测试字母数字混合"""
        assert is_palindrome("A1B2b1a") is True
        assert is_palindrome("A1B2C3") is False
    
    def test_invalid_input_type(self):
        """测试无效输入类型"""
        with pytest.raises(TypeError, match="输入必须是字符串类型"):
            is_palindrome(123)
        
        with pytest.raises(TypeError, match="输入必须是字符串类型"):
            is_palindrome(None)
        
        with pytest.raises(TypeError, match="输入必须是字符串类型"):
            is_palindrome([1, 2, 3])


class TestReverseString:
    """测试reverse_string函数"""
    
    def test_normal_string(self):
        """测试普通字符串反转"""
        assert reverse_string("hello") == "olleh"
        assert reverse_string("python") == "nohtyp"
    
    def test_empty_string(self):
        """测试空字符串反转"""
        assert reverse_string("") == ""
    
    def test_single_character(self):
        """测试单个字符反转"""
        assert reverse_string("a") == "a"
    
    def test_palindrome_string(self):
        """测试回文字符串反转"""
        assert reverse_string("aba") == "aba"
        assert reverse_string("racecar") == "racecar"
    
    def test_string_with_spaces(self):
        """测试包含空格的字符串反转"""
        assert reverse_string("hello world") == "dlrow olleh"
    
    def test_invalid_input_type(self):
        """测试无效输入类型"""
        with pytest.raises(TypeError, match="输入必须是字符串类型"):
            reverse_string(123)


class TestCountVowels:
    """测试count_vowels函数"""
    
    def test_string_with_vowels(self):
        """测试包含元音的字符串"""
        assert count_vowels("hello") == 2  # e, o
        assert count_vowels("python") == 1  # o
        assert count_vowels("aeiou") == 5   # a, e, i, o, u
    
    def test_string_without_vowels(self):
        """测试不包含元音的字符串"""
        assert count_vowels("bcdfg") == 0
        assert count_vowels("xyz") == 0
    
    def test_empty_string(self):
        """测试空字符串"""
        assert count_vowels("") == 0
    
    def test_mixed_case_vowels(self):
        """测试大小写混合的元音"""
        assert count_vowels("AeIoU") == 5
        assert count_vowels("Hello World") == 3  # e, o, o
    
    def test_string_with_numbers(self):
        """测试包含数字的字符串"""
        assert count_vowels("hello123") == 2  # e, o
        assert count_vowels("12345") == 0
    
    def test_invalid_input_type(self):
        """测试无效输入类型"""
        with pytest.raises(TypeError, match="输入必须是字符串类型"):
            count_vowels(123)


class TestCapitalizeWords:
    """测试capitalize_words函数"""
    
    def test_normal_sentence(self):
        """测试普通句子"""
        assert capitalize_words("hello world") == "Hello World"
        assert capitalize_words("python programming") == "Python Programming"
    
    def test_single_word(self):
        """测试单个单词"""
        assert capitalize_words("hello") == "Hello"
        assert capitalize_words("python") == "Python"
    
    def test_empty_string(self):
        """测试空字符串"""
        assert capitalize_words("") == ""
    
    def test_already_capitalized(self):
        """测试已经大写的字符串"""
        assert capitalize_words("Hello World") == "Hello World"
        assert capitalize_words("HELLO WORLD") == "Hello World"
    
    def test_mixed_case(self):
        """测试混合大小写"""
        assert capitalize_words("hELLo WoRLd") == "Hello World"
    
    def test_string_with_punctuation(self):
        """测试包含标点符号的字符串"""
        assert capitalize_words("hello, world!") == "Hello, World!"
        assert capitalize_words("python-programming") == "Python-Programming"
    
    def test_string_with_numbers(self):
        """测试包含数字的字符串"""
        assert capitalize_words("hello 123 world") == "Hello 123 World"
    
    def test_invalid_input_type(self):
        """测试无效输入类型"""
        with pytest.raises(TypeError, match="输入必须是字符串类型"):
            capitalize_words(123)


# 参数化测试示例
@pytest.mark.parametrize("input_str,expected", [
    ("aba", True),
    ("racecar", True),
    ("hello", False),
    ("A man a plan a canal Panama", True),
    ("race a car", False),
    ("", True),
    ("a", True),
])
def test_palindrome_parametrized(input_str, expected):
    """参数化测试回文函数"""
    assert is_palindrome(input_str) == expected


# 测试夹具示例
@pytest.fixture
def sample_strings():
    """提供测试用的字符串样本"""
    return {
        'palindrome': 'racecar',
        'non_palindrome': 'hello',
        'empty': '',
        'single_char': 'a',
        'with_spaces': 'hello world',
        'mixed_case': 'Hello World'
    }


def test_string_operations_with_fixture(sample_strings):
    """使用测试夹具的综合测试"""
    # 测试回文
    assert is_palindrome(sample_strings['palindrome']) is True
    assert is_palindrome(sample_strings['non_palindrome']) is False
    
    # 测试反转
    assert reverse_string(sample_strings['palindrome']) == sample_strings['palindrome']
    assert reverse_string(sample_strings['with_spaces']) == 'dlrow olleh'
    
    # 测试元音计数
    assert count_vowels(sample_strings['palindrome']) == 3  # a, e, a
    assert count_vowels(sample_strings['mixed_case']) == 3  # e, o, o
