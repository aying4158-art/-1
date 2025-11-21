"""
图书管理系统单元测试
使用pytest框架进行测试
"""

import pytest
from library_system import LibrarySystem, User, Book, UserNotExistError, BookNotExistError, BookOutOfStockError


class TestLibrarySystem:
    """图书管理系统测试类"""
    
    def setup_method(self):
        """每个测试方法执行前的准备工作"""
        self.library = LibrarySystem()
        
        # 创建测试用户
        self.user1 = User("U001", "张三")
        self.user2 = User("U002", "李四")
        
        # 创建测试图书
        self.book1 = Book("B001", "Python编程", "作者A", stock=3)
        self.book2 = Book("B002", "软件测试", "作者B", stock=1)
        self.book3 = Book("B003", "数据结构", "作者C", stock=0)  # 库存为0的书
        
        # 添加到系统中
        self.library.add_user(self.user1)
        self.library.add_user(self.user2)
        self.library.add_book(self.book1)
        self.library.add_book(self.book2)
        self.library.add_book(self.book3)
    
    def test_borrow_book_success(self):
        """测试正常借书情况"""
        # 执行借书操作
        message = self.library.borrow_book("U001", "B001")
        
        # 验证结果
        assert "借书成功" in message
        assert "张三" in message
        assert "Python编程" in message
        
        # 验证库存减少
        assert self.library.get_book_stock("B001") == 2
        
        # 验证用户借书记录
        borrowed_books = self.library.get_user_borrowed_books("U001")
        assert "B001" in borrowed_books
        
        # 验证借书记录
        assert len(self.library.borrowed_records) == 1
        record = self.library.borrowed_records[0]
        assert record['user_id'] == "U001"
        assert record['book_id'] == "B001"
        assert record['remaining_stock'] == 2
    
    def test_borrow_book_user_not_exist(self):
        """测试用户不存在的异常情况"""
        # 使用pytest.raises测试异常抛出
        with pytest.raises(UserNotExistError) as exc_info:
            self.library.borrow_book("U999", "B001")
        
        # 验证异常信息
        assert "用户不存在" in str(exc_info.value)
        assert "U999" in str(exc_info.value)
        
        # 验证库存未变化
        assert self.library.get_book_stock("B001") == 3
        
        # 验证无借书记录
        assert len(self.library.borrowed_records) == 0
    
    def test_borrow_book_book_not_exist(self):
        """测试图书不存在的异常情况"""
        # 使用pytest.raises测试异常抛出
        with pytest.raises(BookNotExistError) as exc_info:
            self.library.borrow_book("U001", "B999")
        
        # 验证异常信息
        assert "图书不存在" in str(exc_info.value)
        assert "B999" in str(exc_info.value)
        
        # 验证用户无借书记录
        borrowed_books = self.library.get_user_borrowed_books("U001")
        assert len(borrowed_books) == 0
        
        # 验证无借书记录
        assert len(self.library.borrowed_records) == 0
    
    def test_borrow_book_no_stock(self):
        """测试图书库存为0的异常情况"""
        # 使用pytest.raises测试异常抛出
        with pytest.raises(BookOutOfStockError) as exc_info:
            self.library.borrow_book("U001", "B003")
        
        # 验证异常信息
        assert "图书库存不足" in str(exc_info.value)
        assert "数据结构" in str(exc_info.value)
        assert "当前库存: 0" in str(exc_info.value)
        
        # 验证库存未变化
        assert self.library.get_book_stock("B003") == 0
        
        # 验证用户无借书记录
        borrowed_books = self.library.get_user_borrowed_books("U001")
        assert len(borrowed_books) == 0
    
    def test_borrow_book_last_copy(self):
        """测试借阅最后一本书的情况"""
        # 借阅库存为1的书
        message = self.library.borrow_book("U002", "B002")
        
        assert "借书成功" in message
        assert "李四" in message
        assert "软件测试" in message
        assert "剩余库存: 0" in message
        
        # 验证库存变为0
        assert self.library.get_book_stock("B002") == 0
        
        # 验证用户借书记录
        borrowed_books = self.library.get_user_borrowed_books("U002")
        assert "B002" in borrowed_books
        
        # 再次尝试借阅同一本书应该抛出异常
        with pytest.raises(BookOutOfStockError) as exc_info:
            self.library.borrow_book("U001", "B002")
        assert "图书库存不足" in str(exc_info.value)
    
    def test_multiple_users_borrow_same_book(self):
        """测试多个用户借阅同一本书"""
        # 用户1借书
        message1 = self.library.borrow_book("U001", "B001")
        assert "借书成功" in message1
        assert self.library.get_book_stock("B001") == 2
        
        # 用户2借同一本书
        message2 = self.library.borrow_book("U002", "B001")
        assert "借书成功" in message2
        assert self.library.get_book_stock("B001") == 1
        
        # 验证两个用户都有借书记录
        user1_books = self.library.get_user_borrowed_books("U001")
        user2_books = self.library.get_user_borrowed_books("U002")
        assert "B001" in user1_books
        assert "B001" in user2_books
        
        # 验证有两条借书记录
        assert len(self.library.borrowed_records) == 2
    
    def test_user_borrow_multiple_books(self):
        """测试用户借阅多本书"""
        # 用户借阅第一本书
        message1 = self.library.borrow_book("U001", "B001")
        assert "借书成功" in message1
        
        # 用户借阅第二本书
        message2 = self.library.borrow_book("U001", "B002")
        assert "借书成功" in message2
        
        # 验证用户借书记录
        borrowed_books = self.library.get_user_borrowed_books("U001")
        assert len(borrowed_books) == 2
        assert "B001" in borrowed_books
        assert "B002" in borrowed_books
        
        # 验证库存变化
        assert self.library.get_book_stock("B001") == 2
        assert self.library.get_book_stock("B002") == 0


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v"])
