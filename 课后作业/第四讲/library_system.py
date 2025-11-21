"""
图书管理系统 - 借书功能实现
"""

class UserNotExistError(Exception):
    """用户不存在异常"""
    pass

class BookNotExistError(Exception):
    """图书不存在异常"""
    pass

class BookOutOfStockError(Exception):
    """图书库存不足异常"""
    pass

class User:
    """用户类"""
    def __init__(self, user_id, name):
        self.user_id = user_id
        self.name = name
        self.borrowed_books = []
    
    def __str__(self):
        return f"User({self.user_id}, {self.name})"

class Book:
    """图书类"""
    def __init__(self, book_id, title, author, stock=1):
        self.book_id = book_id
        self.title = title
        self.author = author
        self.stock = stock
    
    def __str__(self):
        return f"Book({self.book_id}, {self.title}, stock={self.stock})"

class LibrarySystem:
    """图书管理系统"""
    def __init__(self):
        self.users = {}  # user_id -> User对象
        self.books = {}  # book_id -> Book对象
        self.borrowed_records = []  # 借书记录
    
    def add_user(self, user):
        """添加用户"""
        self.users[user.user_id] = user
    
    def add_book(self, book):
        """添加图书"""
        self.books[book.book_id] = book
    
    def borrow_book(self, user_id, book_id):
        """
        借书功能
        
        Args:
            user_id: 用户ID
            book_id: 图书ID
            
        Returns:
            str: 成功信息
            
        Raises:
            UserNotExistError: 用户不存在时抛出
            BookNotExistError: 图书不存在时抛出
            BookOutOfStockError: 图书库存不足时抛出
            
        功能要求：
        1. 用户是否存在 - 不存在则抛出异常
        2. 图书是否可借 - 不存在或库存不足则抛出异常
        3. 借书后库存减少
        """
        # 1. 检查用户是否存在
        if user_id not in self.users:
            raise UserNotExistError(f"用户不存在: {user_id}")
        
        user = self.users[user_id]
        
        # 2. 检查图书是否存在
        if book_id not in self.books:
            raise BookNotExistError(f"图书不存在: {book_id}")
        
        book = self.books[book_id]
        
        # 3. 检查图书库存是否可借
        if book.stock <= 0:
            raise BookOutOfStockError(f"图书库存不足: {book.title} (当前库存: {book.stock})")
        
        # 4. 执行借书操作
        book.stock -= 1
        user.borrowed_books.append(book_id)
        
        # 5. 记录借书信息
        borrow_record = {
            'user_id': user_id,
            'user_name': user.name,
            'book_id': book_id,
            'book_title': book.title,
            'remaining_stock': book.stock
        }
        self.borrowed_records.append(borrow_record)
        
        return f"借书成功: {user.name} 借阅了 《{book.title}》，剩余库存: {book.stock}"
    
    def get_user_borrowed_books(self, user_id):
        """获取用户借阅的图书列表"""
        if user_id not in self.users:
            return []
        return self.users[user_id].borrowed_books
    
    def get_book_stock(self, book_id):
        """获取图书库存"""
        if book_id not in self.books:
            return -1
        return self.books[book_id].stock
