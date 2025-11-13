"""logger 模块基础测试。

测试内容:
    - 基础功能测试
    - 多实例隔离测试
    - 动态级别测试
"""

import sys
import os

# 添加项目路径到 sys.path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from yunbot.logger import (
    get_logger,
    register_logger_level,
    success,
    log_success,
    default_logger
)


def test_basic_logging():
    """测试基本日志记录功能。"""
    print("=" * 60)
    print("测试 1: 基本日志记录")
    print("=" * 60)
    
    logger = get_logger("Test1").setup(level="DEBUG")
    
    logger.debug("这是调试信息")
    logger.info("这是一条普通信息")
    logger.success("这是成功信息")
    logger.warning("这是警告信息")
    logger.error("这是错误信息")
    logger.critical("这是严重错误信息")
    
    print()


def test_formatting():
    """测试消息格式化。"""
    print("=" * 60)
    print("测试 2: 消息格式化")
    print("=" * 60)
    
    logger = get_logger("Test2").setup(level="INFO")
    
    # 位置参数
    logger.info("用户 {} 登录成功", "Alice")
    
    # 命名参数
    logger.info("用户 {name} 从 {ip} 登录", name="Bob", ip="192.168.1.100")
    
    # 混合使用
    logger.warning("进程 {} 耗费内存 {memory}MB", "worker-1", memory=256)
    
    print()


def test_multi_instance():
    """测试多实例隔离。"""
    print("=" * 60)
    print("测试 3: 多实例隔离")
    print("=" * 60)
    
    # 创建三个不同配置的 logger
    app_logger = get_logger("App").setup(level="INFO")
    db_logger = get_logger("Database").setup(level="DEBUG")
    net_logger = get_logger("Network").setup(level="WARNING")
    
    # 各自记录日志
    app_logger.info("应用启动中...")
    db_logger.debug("SQL: SELECT * FROM users WHERE id=1")
    db_logger.info("数据库连接成功")
    net_logger.warning("网络连接超时,正在重试...")
    app_logger.success("应用启动完成")
    
    print()


def test_custom_level():
    """测试自定义日志级别。"""
    print("=" * 60)
    print("测试 4: 自定义日志级别")
    print("=" * 60)
    
    # 注册自定义级别
    register_logger_level("VERBOSE", 15, "<blue>")
    register_logger_level("TRACE", 5, "<dim>")
    
    logger = get_logger("Custom").setup(level="TRACE")
    
    # 使用自定义级别
    logger.trace("这是跟踪信息")
    logger.verbose("这是详细信息")
    logger.debug("这是调试信息")
    logger.info("这是普通信息")
    
    print()


def test_module_functions():
    """测试模块级函数。"""
    print("=" * 60)
    print("测试 5: 模块级函数")
    print("=" * 60)
    
    # 使用默认 logger
    default_logger.info("使用 default_logger 记录信息")
    
    # 使用模块级函数
    success("使用 success() 函数")
    log_success("使用 log_success() 函数")
    
    print()


def test_config_hot_reload():
    """测试配置热更新。"""
    print("=" * 60)
    print("测试 6: 配置热更新")
    print("=" * 60)
    
    logger = get_logger("HotReload").setup(level="INFO")
    
    logger.debug("这条 DEBUG 信息不会显示")
    logger.info("这条 INFO 信息会显示")
    
    print("\n--- 调整级别为 DEBUG ---\n")
    
    # 重新配置
    logger.setup(level="DEBUG")
    
    logger.debug("现在 DEBUG 信息可以显示了")
    logger.info("这条 INFO 信息仍然显示")
    
    print()


def main():
    """运行所有测试。"""
    print("\n")
    print("*" * 60)
    print("       Logger 模块基础功能测试")
    print("*" * 60)
    print()
    
    try:
        test_basic_logging()
        test_formatting()
        test_multi_instance()
        test_custom_level()
        test_module_functions()
        test_config_hot_reload()
        
        print("=" * 60)
        print("✅ 所有测试通过!")
        print("=" * 60)
        print()
        
    except Exception as e:
        print()
        print("=" * 60)
        print(f"❌ 测试失败: {e}")
        print("=" * 60)
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
