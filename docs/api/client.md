# 客户端 API

## 概述

OneBotClient 是 YunBot 的核心客户端类,提供了简化的接口来管理连接、注册事件处理器和调用 OneBot API。本文档详细介绍 OneBotClient 类的所有方法和属性。

## 类定义

```python
class OneBotClient:
    """YunBot 高级客户端接口"""
    
    def __init__(self, config: Optional[Config] = None):
        """初始化客户端
        
        Args:
            config: 配置对象
        """
```

## 创建客户端

### create_simple_client()

**功能**: 快速创建单连接客户端

**签名**:
```python
@classmethod
def create_simple_client(
    cls,
    connection_type: str,
    **kwargs
) -> "OneBotClient":
    """创建简单客户端
    
    Args:
        connection_type: 连接类型 ("websocket", "http", "reverse_ws", "webhook")
        **kwargs: 连接配置参数
        
    Returns:
        OneBotClient: 客户端实例
    """
```

**参数**:

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| connection_type | str | 是 | 连接类型 ("websocket", "http", "reverse_ws", "webhook") |
| **kwargs | Any | 是 | 连接配置参数,根据连接类型不同而不同 |

**WebSocket 连接参数**:

| 参数 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| url | str | 是 | - | WebSocket 服务器地址 |
| access_token | str | 否 | None | 访问令牌 |
| heartbeat_interval | float | 否 | None | 心跳间隔(秒) |
| timeout | float | 否 | 30.0 | 超时时间(秒) |

**返回值**: OneBotClient 实例

**示例**:

```python
from yunbot import OneBotClient

# 创建 WebSocket 客户端
client = OneBotClient.create_simple_client(
    connection_type="websocket",
    url="ws://localhost:3001",
    access_token="your_token",
    heartbeat_interval=30.0,
    timeout=30.0
)

# 创建 HTTP 客户端 (开发中)
client = OneBotClient.create_simple_client(
    connection_type="http",
    url="http://localhost:3000",
    access_token="your_token"
)
```

**注意事项**:
- 推荐使用此方法创建客户端,简单快捷
- 如果需要更复杂的配置,使用 `from_config_file()` 或直接传入 Config 对象

---

### from_config_file()

**功能**: 从配置文件创建客户端

**签名**:
```python
@classmethod
def from_config_file(cls, config_path: str) -> "OneBotClient":
    """从配置文件创建客户端
    
    Args:
        config_path: 配置文件路径 (.json 或 .yaml)
        
    Returns:
        OneBotClient: 客户端实例
        
    Raises:
        OneBotException: 不支持的配置文件格式
    """
```

**参数**:

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| config_path | str | 是 | 配置文件路径,支持 .json、.yaml、.yml 格式 |

**返回值**: OneBotClient 实例

**示例**:

```python
from yunbot import OneBotClient

# 从 JSON 配置文件创建
client = OneBotClient.from_config_file("config.json")

# 从 YAML 配置文件创建
client = OneBotClient.from_config_file("config.yaml")
```

**配置文件示例 (config.json)**:
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
  "enable_heartbeat": true,
  "heartbeat_interval": 30.0,
  "reconnect_interval": 5.0,
  "max_reconnect_attempts": 10
}
```

**配置文件示例 (config.yaml)**:
```yaml
connections:
  - type: websocket
    url: ws://localhost:3001
    access_token: your_token
    heartbeat_interval: 30.0
api_timeout: 30.0
max_concurrent_requests: 100
enable_heartbeat: true
heartbeat_interval: 30.0
reconnect_interval: 5.0
max_reconnect_attempts: 10
```

---

## 生命周期管理

### start()

**功能**: 启动客户端

**签名**:
```python
async def start(self, config: Optional[Config] = None) -> None:
    """启动客户端
    
    Args:
        config: 可选配置对象,用于覆盖初始化时的配置
        
    Raises:
        OneBotException: 未提供配置时抛出
    """
```

**参数**:

| 参数 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| config | Config | 否 | None | 配置对象,用于覆盖初始化时的配置 |

**返回值**: None

**示例**:

```python
import asyncio
from yunbot import OneBotClient

async def main():
    client = OneBotClient.create_simple_client(
        connection_type="websocket",
        url="ws://localhost:3001"
    )
    
    # 启动客户端
    await client.start()
    
    # 客户端已就绪,可以调用 API
    login_info = await client.get_login_info()
    print(f"Bot ID: {login_info['user_id']}")
    
    await client.stop()

asyncio.run(main())
```

**注意事项**:
- 必须在调用任何 API 之前先调用 `start()`
- 此方法会建立连接并初始化 Bot 实例
- 如果客户端已经运行,再次调用会记录警告

---

### stop()

**功能**: 停止客户端

**签名**:
```python
async def stop(self) -> None:
    """停止客户端"""
```

**返回值**: None

**示例**:

```python
async def main():
    client = OneBotClient.create_simple_client(
        connection_type="websocket",
        url="ws://localhost:3001"
    )
    
    await client.start()
    
    # 执行一些操作...
    
    # 停止客户端
    await client.stop()
```

**注意事项**:
- 停止客户端会关闭所有连接
- 停止后无法再调用 API
- 建议使用上下文管理器自动管理生命周期

---

### run_forever()

**功能**: 持续运行客户端

**签名**:
```python
async def run_forever(self) -> None:
    """持续运行客户端,直到收到中断信号"""
```

**返回值**: None

**示例**:

```python
import asyncio
from yunbot import OneBotClient

async def main():
    client = OneBotClient.create_simple_client(
        connection_type="websocket",
        url="ws://localhost:3001"
    )
    
    # 注册事件处理器
    @client.on_message
    async def handle_message(event):
        print(f"收到消息: {event.message}")
    
    # 启动并持续运行
    await client.start()
    await client.run_forever()  # 阻塞直到收到 Ctrl+C

asyncio.run(main())
```

**注意事项**:
- 此方法会阻塞,直到收到键盘中断 (Ctrl+C)
- 适用于需要持续运行的机器人程序
- 收到中断信号后会自动调用 `stop()`

---

### 上下文管理器

**功能**: 使用 async with 管理客户端生命周期

**签名**:
```python
async def __aenter__(self):
    """进入异步上下文"""
    
async def __aexit__(self, exc_type, exc_val, exc_tb):
    """退出异步上下文"""
```

**示例**:

```python
import asyncio
from yunbot import OneBotClient

async def main():
    # 使用上下文管理器自动管理生命周期
    async with OneBotClient.create_simple_client(
        connection_type="websocket",
        url="ws://localhost:3001"
    ) as client:
        await client.start()
        
        # 在这里使用客户端
        await client.send_private_msg(user_id=123456789, message="你好")
    
    # 退出上下文时自动调用 stop()

asyncio.run(main())
```

**注意事项**:
- 推荐使用上下文管理器,确保资源正确释放
- 退出上下文时会自动调用 `stop()`

---

## 事件处理

### on_message()

**功能**: 注册消息事件处理器

**签名**:
```python
def on_message(self, handler: Callable[[MessageEvent], Awaitable[None]]) -> None:
    """注册消息事件处理器
    
    Args:
        handler: 消息事件处理函数
    """
```

**参数**:

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| handler | Callable | 是 | 异步函数,接收 MessageEvent 参数 |

**返回值**: None

**示例**:

```python
from yunbot import OneBotClient, MessageSegment

async def main():
    client = OneBotClient.create_simple_client(
        connection_type="websocket",
        url="ws://localhost:3001"
    )
    
    # 使用装饰器注册消息处理器
    @client.on_message
    async def handle_message(event):
        """处理所有消息事件"""
        print(f"收到消息: {event.message}")
        
        # 根据消息来源回复
        if hasattr(event, 'group_id'):
            # 群消息
            await client.send_group_msg(
                group_id=event.group_id,
                message=MessageSegment.text("收到群消息")
            )
        else:
            # 私聊消息
            await client.send_private_msg(
                user_id=event.user_id,
                message=MessageSegment.text("收到私聊消息")
            )
    
    await client.start()
    await client.run_forever()

asyncio.run(main())
```

**注意事项**:
- 可以注册多个消息处理器,按注册顺序依次调用
- 处理器函数必须是异步函数
- 处理器中的异常不会影响其他处理器的执行

---

### on_notice()

**功能**: 注册通知事件处理器

**签名**:
```python
def on_notice(self, handler: Callable[[Event], Awaitable[None]]) -> None:
    """注册通知事件处理器
    
    Args:
        handler: 通知事件处理函数
    """
```

**参数**:

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| handler | Callable | 是 | 异步函数,接收 Event 参数 |

**返回值**: None

**示例**:

```python
@client.on_notice
async def handle_notice(event):
    """处理通知事件"""
    if event.notice_type == "group_increase":
        # 群成员增加
        await client.send_group_msg(
            group_id=event.group_id,
            message=f"欢迎新成员 {event.user_id}!"
        )
    elif event.notice_type == "group_decrease":
        # 群成员减少
        print(f"成员 {event.user_id} 离开了群 {event.group_id}")
```

---

### on_request()

**功能**: 注册请求事件处理器

**签名**:
```python
def on_request(self, handler: Callable[[Event], Awaitable[None]]) -> None:
    """注册请求事件处理器
    
    Args:
        handler: 请求事件处理函数
    """
```

**参数**:

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| handler | Callable | 是 | 异步函数,接收 Event 参数 |

**返回值**: None

**示例**:

```python
@client.on_request
async def handle_request(event):
    """处理请求事件"""
    if event.request_type == "friend":
        # 好友请求 - 自动同意
        await client.set_friend_add_request(
            flag=event.flag,
            approve=True,
            remark=f"新朋友_{event.user_id}"
        )
        print(f"已同意好友请求: {event.user_id}")
    
    elif event.request_type == "group":
        # 群请求 - 自动同意
        await client.set_group_add_request(
            flag=event.flag,
            sub_type=event.sub_type,
            approve=True
        )
        print(f"已同意加群请求: {event.user_id}")
```

---

### on_meta_event()

**功能**: 注册元事件处理器

**签名**:
```python
def on_meta_event(self, handler: Callable[[Event], Awaitable[None]]) -> None:
    """注册元事件处理器
    
    Args:
        handler: 元事件处理函数
    """
```

**参数**:

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| handler | Callable | 是 | 异步函数,接收 Event 参数 |

**返回值**: None

**示例**:

```python
@client.on_meta_event
async def handle_meta_event(event):
    """处理元事件"""
    if event.meta_event_type == "heartbeat":
        # 心跳事件
        print(f"心跳: {event.status}")
    elif event.meta_event_type == "lifecycle":
        # 生命周期事件
        print(f"生命周期事件: {event.sub_type}")
```

---

### on_event()

**功能**: 注册通用事件处理器

**签名**:
```python
def on_event(self, handler: Callable[[Event], Awaitable[None]]) -> None:
    """注册通用事件处理器
    
    Args:
        handler: 事件处理函数
    """
```

**参数**:

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| handler | Callable | 是 | 异步函数,接收 Event 参数 |

**返回值**: None

**示例**:

```python
@client.on_event
async def handle_all_events(event):
    """处理所有事件"""
    print(f"收到事件: {event.post_type}")
```

**注意事项**:
- 通用事件处理器会接收所有类型的事件
- 在具体类型的处理器之前调用

---

## Bot 管理

### get_bot()

**功能**: 获取 Bot 实例

**签名**:
```python
def get_bot(self, self_id: Optional[int] = None) -> Optional[OneBotBot]:
    """获取 Bot 实例
    
    Args:
        self_id: Bot ID,如果为 None 则返回第一个 Bot
        
    Returns:
        OneBotBot: Bot 实例,如果不存在则返回 None
    """
```

**参数**:

| 参数 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| self_id | int | 否 | None | Bot ID,为 None 时返回第一个 Bot |

**返回值**: OneBotBot 实例或 None

**示例**:

```python
# 获取默认 Bot (第一个 Bot)
bot = client.get_bot()

# 获取指定 ID 的 Bot
bot = client.get_bot(self_id=123456789)

# 使用 Bot 调用 API
if bot:
    await bot.send_private_msg(user_id=987654321, message="你好")
```

---

### get_bots()

**功能**: 获取所有 Bot 实例

**签名**:
```python
def get_bots(self) -> List[OneBotBot]:
    """获取所有 Bot 实例
    
    Returns:
        List[OneBotBot]: Bot 实例列表
    """
```

**返回值**: Bot 实例列表

**示例**:

```python
# 获取所有 Bot
bots = client.get_bots()

# 遍历所有 Bot
for bot in bots:
    login_info = await bot.get_login_info()
    print(f"Bot ID: {login_info['user_id']}")
```

---

## 消息发送

### send_private_msg()

**功能**: 发送私聊消息

**签名**:
```python
async def send_private_msg(
    self,
    user_id: int,
    message: Union[str, Message, List[MessageSegment]],
    bot_id: Optional[int] = None
) -> Dict[str, Any]:
    """发送私聊消息
    
    Args:
        user_id: 目标用户 ID
        message: 消息内容
        bot_id: Bot ID,为 None 时使用默认 Bot
        
    Returns:
        Dict: API 响应,包含 message_id
        
    Raises:
        OneBotException: 无可用 Bot 时抛出
    """
```

**参数**:

| 参数 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| user_id | int | 是 | - | 目标用户 ID |
| message | str/Message/List | 是 | - | 消息内容 |
| bot_id | int | 否 | None | Bot ID |

**返回值**: 包含 message_id 的字典

**示例**:

```python
from yunbot import MessageSegment

# 发送文本消息
result = await client.send_private_msg(
    user_id=123456789,
    message="你好"
)
print(f"消息 ID: {result['message_id']}")

# 发送复杂消息
result = await client.send_private_msg(
    user_id=123456789,
    message=[
        MessageSegment.text("你好!"),
        MessageSegment.face(178),
        MessageSegment.image(file="https://example.com/image.jpg")
    ]
)
```

---

### send_group_msg()

**功能**: 发送群消息

**签名**:
```python
async def send_group_msg(
    self,
    group_id: int,
    message: Union[str, Message, List[MessageSegment]],
    bot_id: Optional[int] = None
) -> Dict[str, Any]:
    """发送群消息
    
    Args:
        group_id: 目标群 ID
        message: 消息内容
        bot_id: Bot ID,为 None 时使用默认 Bot
        
    Returns:
        Dict: API 响应,包含 message_id
        
    Raises:
        OneBotException: 无可用 Bot 时抛出
    """
```

**参数**:

| 参数 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| group_id | int | 是 | - | 目标群 ID |
| message | str/Message/List | 是 | - | 消息内容 |
| bot_id | int | 否 | None | Bot ID |

**返回值**: 包含 message_id 的字典

**示例**:

```python
# 发送群消息
result = await client.send_group_msg(
    group_id=987654321,
    message="大家好"
)

# 发送带@的消息
result = await client.send_group_msg(
    group_id=987654321,
    message=[
        MessageSegment.at(123456789),
        MessageSegment.text(" 你好!")
    ]
)
```

---

### send_msg()

**功能**: 通用消息发送方法

**签名**:
```python
async def send_msg(
    self,
    message_type: str,
    message: Union[str, Message, List[MessageSegment]],
    user_id: Optional[int] = None,
    group_id: Optional[int] = None,
    bot_id: Optional[int] = None
) -> Dict[str, Any]:
    """发送消息
    
    Args:
        message_type: 消息类型 ("private" 或 "group")
        message: 消息内容
        user_id: 用户 ID (私聊时需要)
        group_id: 群 ID (群聊时需要)
        bot_id: Bot ID
        
    Returns:
        Dict: API 响应
    """
```

**示例**:

```python
# 发送私聊消息
await client.send_msg(
    message_type="private",
    user_id=123456789,
    message="你好"
)

# 发送群消息
await client.send_msg(
    message_type="group",
    group_id=987654321,
    message="大家好"
)
```

---

## 通用 API 调用

### call_api()

**功能**: 调用任意 OneBot API

**签名**:
```python
async def call_api(self, action: str, **params: Any) -> Dict[str, Any]:
    """调用 OneBot API
    
    Args:
        action: API 动作名称
        **params: API 参数
        
    Returns:
        Dict: API 响应数据
        
    Raises:
        OneBotException: 无可用 Bot 时抛出
    """
```

**参数**:

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| action | str | 是 | API 动作名称 |
| **params | Any | 否 | API 参数 |

**返回值**: API 响应数据字典

**示例**:

```python
# 调用任意 API
result = await client.call_api(
    "send_private_msg",
    user_id=123456789,
    message="你好"
)

# 调用群管理 API
await client.call_api(
    "set_group_ban",
    group_id=987654321,
    user_id=123456789,
    duration=600
)

# 获取信息
login_info = await client.call_api("get_login_info")
print(f"Bot ID: {login_info['user_id']}")
```

---

## 属性

### is_running

**功能**: 检查客户端是否正在运行

**类型**: bool (只读)

**示例**:

```python
if client.is_running:
    print("客户端正在运行")
else:
    print("客户端未运行")
```

---

## 完整示例

### 示例 1: 基础使用

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
        print(f"收到消息: {event.message}")
        
        # 回复消息
        reply = MessageSegment.text(f"收到你的消息: {event.message}")
        if hasattr(event, 'group_id'):
            await client.send_group_msg(event.group_id, reply)
        else:
            await client.send_private_msg(event.user_id, reply)
    
    # 启动并运行
    await client.start()
    await client.run_forever()

asyncio.run(main())
```

### 示例 2: 使用上下文管理器

```python
import asyncio
from yunbot import OneBotClient

async def main():
    async with OneBotClient.create_simple_client(
        connection_type="websocket",
        url="ws://localhost:3001"
    ) as client:
        await client.start()
        
        # 获取登录信息
        login_info = await client.get_login_info()
        print(f"Bot 昵称: {login_info['nickname']}")
        
        # 发送消息
        await client.send_private_msg(
            user_id=123456789,
            message="你好!"
        )
    
    # 退出上下文时自动停止

asyncio.run(main())
```

### 示例 3: 多事件处理

```python
import asyncio
from yunbot import OneBotClient, MessageSegment

async def main():
    client = OneBotClient.create_simple_client(
        connection_type="websocket",
        url="ws://localhost:3001"
    )
    
    # 消息事件
    @client.on_message
    async def handle_message(event):
        print(f"[消息] {event.user_id}: {event.message}")
    
    # 通知事件
    @client.on_notice
    async def handle_notice(event):
        if event.notice_type == "group_increase":
            welcome_msg = MessageSegment.at(event.user_id) + MessageSegment.text(" 欢迎!")
            await client.send_group_msg(event.group_id, welcome_msg)
    
    # 请求事件
    @client.on_request
    async def handle_request(event):
        if event.request_type == "friend":
            await client.set_friend_add_request(flag=event.flag, approve=True)
    
    # 元事件
    @client.on_meta_event
    async def handle_meta_event(event):
        if event.meta_event_type == "heartbeat":
            print(f"心跳: {event.status}")
    
    await client.start()
    await client.run_forever()

asyncio.run(main())
```

## 相关文档

- [API 概览](overview.md) - API 总览和调用约定
- [消息 API](message.md) - 消息相关 API
- [群组管理 API](group.md) - 群组管理 API
- [信息获取 API](info.md) - 信息查询 API
- [客户端使用指南](../guide/client.md) - 客户端使用详解
- [事件处理指南](../guide/events.md) - 事件处理机制
