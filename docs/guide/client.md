# 客户端使用指南

本文档详细介绍 YunBot 客户端的创建、配置和生命周期管理。

## OneBotClient 简介

`OneBotClient` 是 YunBot 的高级客户端接口,提供了简化的 API 来创建和管理 OneBot 机器人。它封装了底层的连接管理、事件分发和 Bot 实例管理,让您可以专注于业务逻辑的实现。

### 主要功能

- 🔧 **简化的客户端创建** - 提供工厂方法快速创建客户端
- 🔌 **连接管理** - 自动管理 WebSocket 连接和重连
- 📨 **事件分发** - 自动分发各类事件到注册的处理器
- 🤖 **Bot 实例管理** - 管理单个或多个 Bot 实例
- ⏰ **生命周期管理** - 完整的启动、运行、停止流程

## 创建客户端

### 方式一: 使用工厂方法 (推荐)

最简单的创建方式是使用 `create_simple_client()` 工厂方法:

```python
from yunbot import OneBotClient

# 创建 WebSocket 客户端
client = OneBotClient.create_simple_client(
    connection_type="websocket",
    url="ws://localhost:3001",
    access_token="your_token",      # 可选
    self_id="123456789",           # 可选,不指定则自动获取
    heartbeat_interval=30.0
)
```

**参数说明**:

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `connection_type` | str | 是 | 连接类型,目前支持 "websocket" |
| `url` | str | 是 | WebSocket 服务器地址 |
| `access_token` | str | 否 | 访问令牌,用于身份验证 |
| `self_id` | str | 否 | 机器人 ID,不指定则自动从 API 获取 |
| `heartbeat_interval` | float | 否 | 心跳间隔(秒),默认 30.0 |
| `timeout` | float | 否 | API 调用超时时间(秒),默认 30.0 |

### 方式二: 使用配置对象

如果需要更复杂的配置,可以使用配置对象:

```python
from yunbot import OneBotClient, Config
from yunbot.config import WebSocketConfig

# 创建连接配置
ws_config = WebSocketConfig(
    url="ws://localhost:3001",
    access_token="your_token",
    heartbeat_interval=30.0
)

# 创建主配置
config = Config(
    connections=[ws_config],
    api_timeout=30.0,
    max_concurrent_requests=100,
    enable_heartbeat=True
)

# 创建客户端
client = OneBotClient(config=config)
```

### 方式三: 从配置文件创建

支持从 JSON 配置文件创建客户端:

```python
from yunbot import OneBotClient

# 从配置文件创建
client = OneBotClient.from_config_file("config.json")
```

配置文件示例 (`config.json`):

```json
{
    "connections": [
        {
            "type": "websocket",
            "url": "ws://localhost:3001",
            "access_token": "your_token",
            "heartbeat_interval": 30.0
        }
    ],
    "api_timeout": 30.0,
    "max_concurrent_requests": 100,
    "enable_heartbeat": true
}
```

## 客户端生命周期

### 启动客户端

```python
import asyncio
from yunbot import OneBotClient

async def main():
    client = OneBotClient.create_simple_client(
        connection_type="websocket",
        url="ws://localhost:3001"
    )
    
    # 启动客户端 - 初始化连接和 Bot 实例
    await client.start()
    print("客户端启动成功")
```

`start()` 方法执行以下操作:
1. 初始化适配器
2. 建立 WebSocket 连接
3. 获取机器人信息 (如果未指定 self_id)
4. 注册内部事件处理器

### 持续运行

```python
async def main():
    client = OneBotClient.create_simple_client(
        connection_type="websocket",
        url="ws://localhost:3001"
    )
    
    await client.start()
    
    # 持续运行,直到收到中断信号
    await client.run_forever()
```

`run_forever()` 方法会阻塞程序,保持客户端运行状态,直到:
- 收到 `KeyboardInterrupt` (Ctrl+C)
- 发生致命错误
- 主动调用 `stop()`

### 停止客户端

```python
async def main():
    client = OneBotClient.create_simple_client(
        connection_type="websocket",
        url="ws://localhost:3001"
    )
    
    try:
        await client.start()
        await client.run_forever()
    except KeyboardInterrupt:
        print("收到中断信号")
    finally:
        # 停止客户端 - 清理资源
        await client.stop()
        print("客户端已停止")

asyncio.run(main())
```

`stop()` 方法执行以下操作:
1. 关闭所有 WebSocket 连接
2. 取消所有待处理的任务
3. 清理资源

### 使用上下文管理器

推荐使用上下文管理器,自动处理启动和停止:

```python
async def main():
    async with OneBotClient.create_simple_client(
        connection_type="websocket",
        url="ws://localhost:3001"
    ) as client:
        # 客户端已自动启动
        @client.on_message
        async def handle_message(event):
            print(f"收到消息: {event.message}")
        
        # 持续运行
        await client.run_forever()
    # 退出时自动停止

asyncio.run(main())
```

## 事件处理器注册

### 使用装饰器注册

```python
client = OneBotClient.create_simple_client(
    connection_type="websocket",
    url="ws://localhost:3001"
)

# 注册消息事件处理器
@client.on_message
async def handle_message(event):
    print(f"收到消息: {event.message}")

# 注册通知事件处理器
@client.on_notice
async def handle_notice(event):
    print(f"收到通知: {event.notice_type}")

# 注册请求事件处理器
@client.on_request
async def handle_request(event):
    print(f"收到请求: {event.request_type}")

# 注册元事件处理器
@client.on_meta_event
async def handle_meta_event(event):
    print(f"收到元事件: {event.meta_event_type}")

# 注册通用事件处理器 (处理所有事件)
@client.on_event
async def handle_all_events(event):
    print(f"收到事件: {event}")
```

### 使用方法注册

```python
async def my_message_handler(event):
    print(f"收到消息: {event.message}")

# 注册处理器
client.on_message(my_message_handler)
```

### 注册多个处理器

可以为同一类型的事件注册多个处理器,它们会按注册顺序依次执行:

```python
@client.on_message
async def handler1(event):
    print("处理器 1")

@client.on_message
async def handler2(event):
    print("处理器 2")

# 收到消息时,两个处理器都会被调用
```

## 获取 Bot 实例

### 获取默认 Bot

```python
# 获取第一个 Bot 实例
bot = client.get_bot()

# 使用 Bot 实例调用 API
await bot.send_private_msg(user_id=123456789, message="Hello!")
```

### 获取指定 Bot

如果管理多个 Bot 实例,可以通过 self_id 获取:

```python
# 获取指定 self_id 的 Bot
bot = client.get_bot(self_id="123456789")
```

### 获取所有 Bot

```python
# 获取所有 Bot 实例的字典 {self_id: bot}
bots = client.get_bots()

for self_id, bot in bots.items():
    print(f"Bot {self_id} 在线")
```

## 发送消息的便捷方法

客户端提供了便捷的消息发送方法:

### 发送私聊消息

```python
from yunbot import MessageSegment

# 发送私聊消息
await client.send_private_msg(
    user_id=123456789,
    message="你好!"
)

# 发送带消息段的消息
msg = MessageSegment.text("你好!") + MessageSegment.face(178)
await client.send_private_msg(user_id=123456789, message=msg)
```

### 发送群消息

```python
# 发送群消息
await client.send_group_msg(
    group_id=987654321,
    message="大家好!"
)
```

### 发送通用消息

```python
# 自动判断消息类型
await client.send_msg(
    user_id=123456789,      # 私聊
    message="Hello"
)

await client.send_msg(
    group_id=987654321,     # 群聊
    message="Hello Group"
)
```

## 调用 API

### 使用便捷方法

客户端提供了所有 OneBot API 的便捷方法:

```python
# 获取登录信息
login_info = await client.get_login_info()
print(f"Bot ID: {login_info['user_id']}")

# 获取好友列表
friends = await client.get_friend_list()

# 获取群列表
groups = await client.get_group_list()
```

### 动态调用 API

客户端支持动态调用任意 API:

```python
# 使用 call_api 方法
result = await client.call_api("get_login_info")

# 使用 __getattr__ 魔术方法
result = await client.get_login_info()

# 传递参数
result = await client.send_private_msg(user_id=123456789, message="Hi!")
```

## 多机器人实例管理

### 场景说明

在某些情况下,一个客户端可能连接到多个 OneBot 实例,每个实例对应一个 Bot:

```python
from yunbot import OneBotClient, Config
from yunbot.config import WebSocketConfig

# 创建多个连接配置
config = Config(
    connections=[
        WebSocketConfig(url="ws://localhost:3001"),  # Bot 1
        WebSocketConfig(url="ws://localhost:3002"),  # Bot 2
    ]
)

client = OneBotClient(config=config)

await client.start()

# 获取所有 Bot
bots = client.get_bots()
for self_id, bot in bots.items():
    print(f"Bot {self_id} 已连接")
```

### 为不同 Bot 注册不同处理器

```python
@client.on_message
async def handle_message(event):
    # 根据 self_id 区分不同 Bot
    if event.self_id == "111111111":
        # Bot 1 的处理逻辑
        await client.send_private_msg(user_id=event.user_id, message="我是 Bot 1")
    elif event.self_id == "222222222":
        # Bot 2 的处理逻辑
        await client.send_private_msg(user_id=event.user_id, message="我是 Bot 2")
```

## 完整示例

```python
import asyncio
from yunbot import OneBotClient, MessageSegment

async def main():
    # 创建客户端
    client = OneBotClient.create_simple_client(
        connection_type="websocket",
        url="ws://localhost:3001",
        access_token="your_token"
    )
    
    # 注册消息处理器
    @client.on_message
    async def handle_message(event):
        print(f"[消息] 来自 {event.user_id}: {event.message}")
        
        # 简单的命令处理
        text = str(event.message)
        if text == "/status":
            bot = client.get_bot()
            status = await bot.get_status()
            reply = f"机器人状态: {'正常' if status.get('good') else '异常'}"
            await client.send_private_msg(user_id=event.user_id, message=reply)
    
    # 注册通知处理器
    @client.on_notice
    async def handle_notice(event):
        if event.notice_type == "group_increase":
            # 欢迎新成员
            welcome = MessageSegment.at(event.user_id) + MessageSegment.text(" 欢迎加入!")
            await client.send_group_msg(group_id=event.group_id, message=welcome)
    
    # 启动客户端
    try:
        await client.start()
        print("✅ 客户端启动成功")
        await client.run_forever()
    except KeyboardInterrupt:
        print("⏹️ 收到中断信号")
    finally:
        await client.stop()
        print("👋 客户端已停止")

if __name__ == "__main__":
    asyncio.run(main())
```

## 最佳实践

### 1. 使用上下文管理器

```python
async with OneBotClient.create_simple_client(...) as client:
    await client.run_forever()
```

### 2. 适当的异常处理

```python
try:
    await client.start()
    await client.run_forever()
except NetworkException as e:
    print(f"网络错误: {e}")
except ActionFailed as e:
    print(f"API 调用失败: {e}")
except Exception as e:
    print(f"未知错误: {e}")
finally:
    await client.stop()
```

### 3. 合理的超时设置

```python
client = OneBotClient.create_simple_client(
    connection_type="websocket",
    url="ws://localhost:3001",
    timeout=60.0  # 根据网络情况调整超时时间
)
```

### 4. 使用日志记录

```python
from yunbot.logger import setup_logging

# 配置日志
logger = setup_logging(level="INFO")

@client.on_message
async def handle_message(event):
    logger.info(f"收到消息: {event.message}")
```

## 相关文档

- [快速开始](../quickstart.md)
- [事件处理](events.md)
- [配置管理](configuration.md)
- [客户端 API](../api/client.md)
