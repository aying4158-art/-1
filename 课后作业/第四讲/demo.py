"""
图书管理系统演示程序
展示如何使用图书管理系统的借书功能
"""

from library_system import LibrarySystem, User, Book, UserNotExistError, BookNotExistError, BookOutOfStockError

def main():
    print("=" * 50)
    print("图书管理系统 - 借书功能演示")
    print("=" * 50)
    
    # 创建图书管理系统
    library = LibrarySystem()
    
    # 创建用户
    print("\n1. 创建用户")
    user1 = User("U001", "张三")
    user2 = User("U002", "李四")
    
    library.add_user(user1)
    library.add_user(user2)
    print(f"   添加用户: {user1}")
    print(f"   添加用户: {user2}")
    
    # 创建图书
    print("\n2. 添加图书")
    book1 = Book("B001", "Python编程从入门到精通", "作者A", stock=3)
    book2 = Book("B002", "软件测试实战", "作者B", stock=1)
    book3 = Book("B003", "数据结构与算法", "作者C", stock=0)  # 库存为0
    
    library.add_book(book1)
    library.add_book(book2)
    library.add_book(book3)
    print(f"   添加图书: {book1}")
    print(f"   添加图书: {book2}")
    print(f"   添加图书: {book3}")
    
    print("\n3. 借书操作演示")
    
    # 正常借书
    print("\n3.1 正常借书情况")
    try:
        message = library.borrow_book("U001", "B001")
        print(f"   ✅ {message}")
        print(f"   📚 当前库存: {library.get_book_stock('B001')}")
    except Exception as e:
        print(f"   ❌ 借书失败: {e}")
    
    # 用户不存在
    print("\n3.2 用户不存在的异常情况")
    try:
        message = library.borrow_book("U999", "B001")
        print(f"   ✅ {message}")
    except UserNotExistError as e:
        print(f"   ❌ 捕获到用户不存在异常: {e}")
    except Exception as e:
        print(f"   ❌ 其他异常: {e}")
    
    # 图书不存在
    print("\n3.3 图书不存在的异常情况")
    try:
        message = library.borrow_book("U001", "B999")
        print(f"   ✅ {message}")
    except BookNotExistError as e:
        print(f"   ❌ 捕获到图书不存在异常: {e}")
    except Exception as e:
        print(f"   ❌ 其他异常: {e}")
    
    # 图书库存不足
    print("\n3.4 图书库存为0的异常情况")
    try:
        message = library.borrow_book("U001", "B003")
        print(f"   ✅ {message}")
    except BookOutOfStockError as e:
        print(f"   ❌ 捕获到库存不足异常: {e}")
    except Exception as e:
        print(f"   ❌ 其他异常: {e}")
    
    # 借阅最后一本书
    print("\n3.5 借阅最后一本书")
    try:
        message = library.borrow_book("U002", "B002")
        print(f"   ✅ {message}")
        print(f"   📚 当前库存: {library.get_book_stock('B002')}")
        
        # 再次尝试借阅
        print("   尝试再次借阅同一本书...")
        message2 = library.borrow_book("U001", "B002")
        print(f"   ✅ {message2}")
    except BookOutOfStockError as e:
        print(f"   ❌ 预期的库存不足异常: {e}")
    except Exception as e:
        print(f"   ❌ 其他异常: {e}")
    
    # 显示借书记录
    print("\n4. 借书记录统计")
    print(f"   总借书记录数: {len(library.borrowed_records)}")
    for i, record in enumerate(library.borrowed_records, 1):
        print(f"   记录{i}: {record['user_name']} 借阅了 《{record['book_title']}》")
    
    # 显示用户借书情况
    print("\n5. 用户借书情况")
    for user_id in ["U001", "U002"]:
        if user_id in library.users:
            user = library.users[user_id]
            borrowed_books = library.get_user_borrowed_books(user_id)
            print(f"   {user.name} 借阅的图书: {borrowed_books}")
    
    print("\n" + "=" * 50)
    print("演示完成！")
    print("=" * 50)

if __name__ == "__main__":
    main()
