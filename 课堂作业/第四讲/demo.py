"""
转账功能演示脚本
展示正常场景和异常场景
"""

from account import Account, transfer, InsufficientBalanceError, InvalidAmountError


def print_separator():
    """打印分隔线"""
    print("\n" + "=" * 60 + "\n")


def demo_normal_transfer():
    """演示正常转账"""
    print("【场景1: 正常转账】")
    print("-" * 60)
    
    alice = Account("Alice", 1000)
    bob = Account("Bob", 500)
    
    print(f"转账前:")
    print(f"  Alice账户余额: {alice.balance}")
    print(f"  Bob账户余额: {bob.balance}")
    
    transfer(alice, bob, 200)
    
    print(f"\n转账 200 元后:")
    print(f"  Alice账户余额: {alice.balance}")
    print(f"  Bob账户余额: {bob.balance}")
    print("\n✅ 转账成功!")


def demo_insufficient_balance():
    """演示余额不足"""
    print("【场景2: 余额不足】")
    print("-" * 60)
    
    alice = Account("Alice", 100)
    bob = Account("Bob", 500)
    
    print(f"转账前:")
    print(f"  Alice账户余额: {alice.balance}")
    print(f"  Bob账户余额: {bob.balance}")
    
    try:
        print(f"\n尝试转账 200 元...")
        transfer(alice, bob, 200)
    except InsufficientBalanceError as e:
        print(f"❌ 转账失败: {e}")
        print(f"\n转账失败后:")
        print(f"  Alice账户余额: {alice.balance} (未改变)")
        print(f"  Bob账户余额: {bob.balance} (未改变)")


def demo_negative_amount():
    """演示负数金额"""
    print("【场景3: 负数金额】")
    print("-" * 60)
    
    alice = Account("Alice", 1000)
    bob = Account("Bob", 500)
    
    print(f"转账前:")
    print(f"  Alice账户余额: {alice.balance}")
    print(f"  Bob账户余额: {bob.balance}")
    
    try:
        print(f"\n尝试转账 -100 元...")
        transfer(alice, bob, -100)
    except InvalidAmountError as e:
        print(f"❌ 转账失败: {e}")
        print(f"\n转账失败后:")
        print(f"  Alice账户余额: {alice.balance} (未改变)")
        print(f"  Bob账户余额: {bob.balance} (未改变)")


def demo_zero_amount():
    """演示零金额"""
    print("【场景4: 零金额】")
    print("-" * 60)
    
    alice = Account("Alice", 1000)
    bob = Account("Bob", 500)
    
    print(f"转账前:")
    print(f"  Alice账户余额: {alice.balance}")
    print(f"  Bob账户余额: {bob.balance}")
    
    try:
        print(f"\n尝试转账 0 元...")
        transfer(alice, bob, 0)
    except InvalidAmountError as e:
        print(f"❌ 转账失败: {e}")
        print(f"\n转账失败后:")
        print(f"  Alice账户余额: {alice.balance} (未改变)")
        print(f"  Bob账户余额: {bob.balance} (未改变)")


def demo_exact_balance():
    """演示转账全部余额"""
    print("【场景5: 转账全部余额】")
    print("-" * 60)
    
    alice = Account("Alice", 500)
    bob = Account("Bob", 200)
    
    print(f"转账前:")
    print(f"  Alice账户余额: {alice.balance}")
    print(f"  Bob账户余额: {bob.balance}")
    
    transfer(alice, bob, 500)
    
    print(f"\n转账 500 元后:")
    print(f"  Alice账户余额: {alice.balance}")
    print(f"  Bob账户余额: {bob.balance}")
    print("\n✅ 转账成功! Alice账户余额为0")


def demo_multiple_transfers():
    """演示多次转账"""
    print("【场景6: 多次转账】")
    print("-" * 60)
    
    alice = Account("Alice", 1000)
    bob = Account("Bob", 500)
    charlie = Account("Charlie", 200)
    
    print(f"初始状态:")
    print(f"  Alice账户余额: {alice.balance}")
    print(f"  Bob账户余额: {bob.balance}")
    print(f"  Charlie账户余额: {charlie.balance}")
    
    print(f"\n第1次转账: Alice -> Bob (100元)")
    transfer(alice, bob, 100)
    print(f"  Alice: {alice.balance}, Bob: {bob.balance}, Charlie: {charlie.balance}")
    
    print(f"\n第2次转账: Bob -> Charlie (150元)")
    transfer(bob, charlie, 150)
    print(f"  Alice: {alice.balance}, Bob: {bob.balance}, Charlie: {charlie.balance}")
    
    print(f"\n第3次转账: Charlie -> Alice (50元)")
    transfer(charlie, alice, 50)
    print(f"  Alice: {alice.balance}, Bob: {bob.balance}, Charlie: {charlie.balance}")
    
    print("\n✅ 所有转账成功!")


def demo_edge_cases():
    """演示边界情况"""
    print("【场景7: 边界情况】")
    print("-" * 60)
    
    # 小额转账
    print("1. 小额转账 (0.01元)")
    alice = Account("Alice", 100)
    bob = Account("Bob", 0)
    transfer(alice, bob, 0.01)
    print(f"   Alice: {alice.balance:.2f}, Bob: {bob.balance:.2f}")
    print("   ✅ 成功")
    
    # 大额转账
    print("\n2. 大额转账 (999999元)")
    rich = Account("Rich", 1000000)
    poor = Account("Poor", 0)
    transfer(rich, poor, 999999)
    print(f"   Rich: {rich.balance}, Poor: {poor.balance}")
    print("   ✅ 成功")
    
    # 余额略微不足
    print("\n3. 余额略微不足 (余额99.99, 尝试转账100)")
    alice = Account("Alice", 99.99)
    bob = Account("Bob", 0)
    try:
        transfer(alice, bob, 100)
    except InsufficientBalanceError:
        print(f"   Alice: {alice.balance}, Bob: {bob.balance}")
        print("   ❌ 转账失败 (余额不足)")


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print(" " * 15 + "转账功能演示程序")
    print("=" * 60)
    
    demo_normal_transfer()
    print_separator()
    
    demo_insufficient_balance()
    print_separator()
    
    demo_negative_amount()
    print_separator()
    
    demo_zero_amount()
    print_separator()
    
    demo_exact_balance()
    print_separator()
    
    demo_multiple_transfers()
    print_separator()
    
    demo_edge_cases()
    print_separator()
    
    print("演示完成! 所有场景已展示。")
    print("\n运行测试: pytest -v")
    print("查看覆盖率: pytest --cov=account --cov-report=term-missing")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
