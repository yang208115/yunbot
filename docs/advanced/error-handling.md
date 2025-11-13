# 错误处理

## 概述

YunBot 提供了完善的异常体系和错误处理机制,帮助你构建健壮的机器人应用。

## 异常类型

### OneBotException

所有 YunBot 异常的基类。

```python
from yunbot.exceptions import OneBotException

try:
    # YunBot 操作
    pass
except OneBotException as e:
    print(f"YunBot 异常: {e}")
```

### NetworkException

网络相关异常,如连接失败、超时等。

```python
from yunbot.exceptions import NetworkException

try:
    await client.start()
except NetworkException as e:
    print(f"网络错误: {e}")
    print(f"状态码: {e.status_code}")
    print(f"已重试: {e.retry_count}次")
```

**属性**:
- `status_code`: HTTP 状态码
- `retry_count`: 已重试次数
- `should_retry()`: 是否应该重试

### ActionFailed

API 调用失败异常。

```python
from yunbot.exceptions import ActionFailed

try:
    await client.send_private_msg(user_id=123456789, message="你好")
except ActionFailed as e:
    print(f"API 调用失败: {e}")
    print(f"返回码: {e.retcode}")
    print(f"状态: {e.status}")
    print(f"API: {e.api}")
    print(f"参数: {e.params}")
```

**属性**:
- `retcode`: 返回码
- `status`: 状态信息
- `data`: 返回数据
- `api`: API 名称
- `params`: API 参数
- `is_rate_limited()`: 是否被限流

### ApiNotAvailable

API 不可用异常,连接未建立时调用 API 会抛出。

```python
from yunbot.exceptions import ApiNotAvailable

try:
    # 未启动客户端就调用 API
    await client.send_private_msg(user_id=123456789, message="你好")
except ApiNotAvailable as e:
    print(f"API 不可用: {e}")
```

### TimeoutException

请求超时异常。

```python
from yunbot.exceptions import TimeoutException

try:
    await client.call_api("some_slow_api")
except TimeoutException as e:
    print(f"请求超时: {e}")
```

### AuthenticationFailed

身份验证失败异常。

```python
from yunbot.exceptions import AuthenticationFailed

try:
    await client.start()
except AuthenticationFailed as e:
    print(f"认证失败: {e}")
```

## 错误处理模式

### 1. Try-Except 基础模式

```python
from yunbot import OneBotClient
from yunbot.exceptions import ActionFailed, NetworkException

async def send_message_safely():
    client = OneBotClient.create_simple_client(
        connection_type="websocket",
        url="ws://localhost:3001"
    )
    
    try:
        await client.start()
        await client.send_private_msg(user_id=123456789, message="你好")
    except ActionFailed as e:
        print(f"消息发送失败: {e}")
    except NetworkException as e:
        print(f"网络错误: {e}")
    except Exception as e:
        print(f"未知错误: {e}")
    finally:
        await client.stop()
```

### 2. 异常分类处理

```python
async def handle_api_call():
    try:
        result = await client.call_api("send_private_msg", user_id=123, message="test")
    except ActionFailed as e:
        if e.is_rate_limited():
            print("被限流,稍后重试")
            await asyncio.sleep(60)
        else:
            print(f"API 调用失败: {e}")
    except NetworkException as e:
        if e.should_retry():
            print("网络错误,准备重试")
        else:
            print(f"网络错误无法恢复: {e}")
```

### 3. 重试机制

```python
import asyncio
from yunbot.exceptions import NetworkException, TimeoutException

async def retry_api_call(func, max_retries=3, delay=1):
    """带重试的 API 调用"""
    for attempt in range(max_retries):
        try:
            return await func()
        except (NetworkException, TimeoutException) as e:
            if attempt < max_retries - 1:
                print(f"尝试 {attempt + 1} 失败,{delay} 秒后重试")
                await asyncio.sleep(delay)
                delay *= 2  # 指数退避
            else:
                print(f"重试 {max_retries} 次后仍失败")
                raise

# 使用
async def send_msg():
    return await client.send_private_msg(user_id=123, message="test")

await retry_api_call(send_msg, max_retries=3)
```

### 4. 上下文管理器

```python
async def main():
    try:
        async with OneBotClient.create_simple_client(
            connection_type="websocket",
            url="ws://localhost:3001"
        ) as client:
            await client.start()
            # 使用客户端...
    except Exception as e:
        print(f"错误: {e}")
    # 自动清理资源
```

## 事件处理器中的错误处理

### 捕获处理器异常

```python
@client.on_message
async def handle_message(event):
    try:
        # 处理消息
        from yunbot import Message
        msg = Message(event.message)
        text = msg.extract_plain_text()
        
        # 可能出错的操作
        result = await some_risky_operation(text)
        
        # 发送回复
        await client.send_private_msg(event.user_id, f"结果: {result}")
        
    except ValueError as e:
        logger.error(f"数据验证失败: {e}")
        await client.send_private_msg(event.user_id, "输入格式错误")
    except ActionFailed as e:
        logger.error(f"消息发送失败: {e}")
    except Exception as e:
        logger.exception(f"未知错误: {e}")
        await client.send_private_msg(event.user_id, "处理出错,请稍后重试")
```

### 全局错误处理

```python
@client.on_event
async def global_error_handler(event):
    """全局错误处理器"""
    try:
        # 让其他处理器正常执行
        pass
    except Exception as e:
        logger.exception(f"事件处理异常: {e}")
```

## 日志记录

结合日志系统记录错误:

```python
from yunbot.logger import get_logger

logger = get_logger("ErrorHandler").setup(
    level="INFO",
    log_to_file=True
)

async def handle_with_logging():
    try:
        await client.send_private_msg(user_id=123, message="test")
        logger.info("消息发送成功")
    except ActionFailed as e:
        logger.error(f"API 调用失败: {e}")
        logger.error(f"  返回码: {e.retcode}")
        logger.error(f"  API: {e.api}")
    except NetworkException as e:
        logger.error(f"网络错误: {e}")
        logger.error(f"  状态码: {e.status_code}")
        logger.error(f"  重试次数: {e.retry_count}")
    except Exception as e:
        logger.exception(f"未知错误")  # 自动记录堆栈
```

## 最佳实践

### 1. 分层错误处理

```python
# 底层: 捕获具体异常
async def send_message(user_id, message):
    try:
        return await client.send_private_msg(user_id, message)
    except ActionFailed as e:
        logger.error(f"消息发送失败: {e}")
        raise

# 中层: 业务逻辑处理
async def handle_command(event, command):
    try:
        result = await process_command(command)
        await send_message(event.user_id, result)
    except Exception as e:
        logger.error(f"命令处理失败: {e}")
        await send_message(event.user_id, "命令执行失败")

# 上层: 统一错误处理
@client.on_message
async def handle_message(event):
    try:
        await handle_command(event, event.message)
    except Exception as e:
        logger.exception(f"消息处理异常")
```

### 2. 优雅降级

```python
async def get_user_info(user_id):
    """获取用户信息,失败时返回默认值"""
    try:
        return await client.get_stranger_info(user_id)
    except Exception as e:
        logger.warning(f"获取用户信息失败: {e}")
        return {"user_id": user_id, "nickname": "未知用户"}
```

### 3. 错误恢复

```python
async def resilient_bot():
    """具有错误恢复能力的机器人"""
    while True:
        try:
            await client.start()
            await client.run_forever()
        except NetworkException as e:
            logger.error(f"连接断开: {e}")
            logger.info("5 秒后尝试重连...")
            await asyncio.sleep(5)
        except KeyboardInterrupt:
            logger.info("收到中断信号,退出")
            break
        except Exception as e:
            logger.exception(f"未知错误: {e}")
            await asyncio.sleep(10)
        finally:
            await client.stop()
```

## 注意事项

1. **捕获具体异常**: 优先捕获具体的异常类型,避免过度使用 `except Exception`
2. **记录错误**: 使用日志系统记录所有错误,便于排查
3. **用户友好**: 向用户返回友好的错误提示,不要暴露技术细节
4. **资源清理**: 使用 finally 或上下文管理器确保资源正确释放
5. **避免静默失败**: 不要捕获异常后不做任何处理

## 相关文档

- [日志系统](logging.md) - 日志记录和管理
- [客户端使用](../guide/client.md) - 客户端的创建和管理
