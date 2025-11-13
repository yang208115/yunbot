# 日志系统

## 概述

YunBot 提供了强大的日志系统,基于 loguru 实现,支持彩色输出、文件轮转、多实例隔离等功能。

## 快速开始

### 使用默认日志器

```python
from yunbot.logger import default_logger as logger

# 直接使用默认日志器
logger.info("应用启动")
logger.debug("调试信息")
logger.warning("警告信息")
logger.error("错误信息")
```

### 创建自定义日志器

```python
from yunbot.logger import get_logger

# 创建命名日志器
logger = get_logger("MyBot").setup(level="INFO")

logger.info("这是一条信息日志")
logger.error("这是一条错误日志")
```

## 日志级别

YunBot 支持以下标准日志级别:

| 级别 | 数值 | 说明 | 使用场景 |
|------|------|------|---------|
| DEBUG | 10 | 调试信息 | 开发调试 |
| INFO | 20 | 一般信息 | 正常运行信息 |
| SUCCESS | 25 | 成功信息 | 操作成功提示 |
| WARNING | 30 | 警告信息 | 潜在问题 |
| ERROR | 40 | 错误信息 | 错误但可恢复 |
| CRITICAL | 50 | 严重错误 | 严重错误,可能导致程序崩溃 |

### 使用不同级别

```python
from yunbot.logger import get_logger

logger = get_logger("App").setup(level="DEBUG")

logger.debug("调试信息: 变量 x = {}", 10)
logger.info("程序启动成功")
logger.success("任务完成")
logger.warning("磁盘空间不足")
logger.error("文件读取失败")
logger.critical("数据库连接失败")
```

## 日志配置

### 基础配置

```python
from yunbot.logger import get_logger

logger = get_logger("MyBot").setup(
    level="INFO",                    # 日志级别
    log_to_file=False                # 是否输出到文件
)
```

### 文件日志配置

```python
logger = get_logger("MyBot").setup(
    level="DEBUG",
    log_to_file=True,                # 启用文件日志
    log_dir="logs",                  # 日志目录
    max_size=10 * 1024 * 1024,      # 单文件最大 10MB
    backup_count=5                   # 保留 5 个备份文件
)
```

### 自定义格式

```python
custom_format = (
    "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
    "<level>{message}</level>"
)

logger = get_logger("MyBot").setup(
    level="INFO",
    format_string=custom_format
)
```

## 多实例隔离

YunBot 的日志系统支持真正的多实例隔离,每个实例有独立的配置。

```python
from yunbot.logger import get_logger

# Bot 1 的日志器
bot1_logger = get_logger("Bot1").setup(
    level="INFO",
    log_to_file=True,
    log_dir="logs/bot1"
)

# Bot 2 的日志器
bot2_logger = get_logger("Bot2").setup(
    level="DEBUG",
    log_to_file=True,
    log_dir="logs/bot2"
)

# 两个日志器互不影响
bot1_logger.info("Bot1 日志")
bot2_logger.debug("Bot2 日志")
```

## 与 YunBot 客户端集成

```python
import asyncio
from yunbot import OneBotClient
from yunbot.logger import get_logger

# 创建日志器
logger = get_logger("YunBot").setup(
    level="INFO",
    log_to_file=True,
    log_dir="logs",
    max_size=10 * 1024 * 1024,
    backup_count=5
)

async def main():
    client = OneBotClient.create_simple_client(
        connection_type="websocket",
        url="ws://localhost:3001"
    )
    
    @client.on_message
    async def handle_message(event):
        logger.info(f"收到消息: {event.message}")
        
        try:
            # 处理消息...
            logger.success("消息处理成功")
        except Exception as e:
            logger.error(f"消息处理失败: {e}")
    
    await client.start()
    logger.info("客户端启动成功")
    await client.run_forever()

asyncio.run(main())
```

## 日志文件管理

### 文件轮转

当日志文件达到指定大小时自动创建新文件:

```python
logger = get_logger("MyBot").setup(
    log_to_file=True,
    max_size=10 * 1024 * 1024  # 10MB 后轮转
)
```

### 文件保留

只保留最近的 N 个日志文件:

```python
logger = get_logger("MyBot").setup(
    log_to_file=True,
    backup_count=5  # 只保留最近 5 个文件
)
```

### 文件命名

日志文件自动包含日期:

```
logs/
├── MyBot_20240101.log
├── MyBot_20240102.log
└── MyBot_20240103.log
```

## 异常日志

使用 `exception()` 方法记录异常,自动包含堆栈信息:

```python
from yunbot.logger import get_logger

logger = get_logger("MyBot").setup(level="DEBUG")

try:
    result = 10 / 0
except Exception as e:
    logger.exception("发生异常")
    # 输出:
    # ERROR | 发生异常
    # Traceback (most recent call last):
    #   ...
    # ZeroDivisionError: division by zero
```

## 最佳实践

### 1. 为每个模块创建日志器

```python
# bot.py
from yunbot.logger import get_logger
logger = get_logger("Bot").setup(level="INFO")

# handler.py
from yunbot.logger import get_logger
logger = get_logger("Handler").setup(level="INFO")
```

### 2. 生产环境配置

```python
import os

env = os.getenv("ENV", "development")

if env == "production":
    logger = get_logger("YunBot").setup(
        level="WARNING",        # 生产环境只记录警告及以上
        log_to_file=True,
        log_dir="/var/log/yunbot",
        max_size=50 * 1024 * 1024,  # 50MB
        backup_count=10
    )
else:
    logger = get_logger("YunBot").setup(
        level="DEBUG",          # 开发环境记录所有日志
        log_to_file=True,
        log_dir="logs"
    )
```

### 3. 结构化日志

```python
logger.info("用户 {} 执行了操作 {}", user_id, action)
logger.error("API 调用失败: {} | 参数: {}", api_name, params)
```

### 4. 避免敏感信息泄露

```python
# ❌ 不推荐: 记录完整 token
logger.info(f"Token: {access_token}")

# ✅ 推荐: 脱敏处理
logger.info(f"Token: {access_token[:6]}...{access_token[-4:]}")
```

## 注意事项

1. **日志级别**: 生产环境建议使用 INFO 或 WARNING
2. **文件大小**: 合理设置 max_size,避免单文件过大
3. **备份数量**: backup_count 不宜过大,占用磁盘空间
4. **性能影响**: DEBUG 级别会影响性能,仅在调试时使用
5. **线程安全**: 日志系统是线程安全的,可以在多线程环境使用

## 相关文档

- [错误处理](error-handling.md) - 异常处理和错误恢复
- [客户端使用](../guide/client.md) - 客户端的创建和管理
