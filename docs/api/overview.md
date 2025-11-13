# API 概览

## 概述

YunBot 实现了完整的 OneBot v11 协议 API,提供了丰富的方法来与聊天平台进行交互。本文档提供 API 的总体概览,帮助您快速了解可用的功能和调用方式。

## API 分类

YunBot 的 API 按功能分为以下几类:

### 1. 消息 API

用于发送、获取和管理消息。

| 分类 | 说明 | 详细文档 |
|------|------|---------|
| 消息发送 | 发送私聊消息、群消息 | [消息 API](message.md) |
| 消息操作 | 撤回消息、获取消息、点赞 | [消息 API](message.md) |

**主要方法**:
- `send_private_msg()` - 发送私聊消息
- `send_group_msg()` - 发送群消息
- `send_msg()` - 通用消息发送
- `delete_msg()` - 撤回消息
- `get_msg()` - 获取消息
- `send_like()` - 发送点赞

### 2. 群组管理 API

用于管理群组和群成员。

| 分类 | 说明 | 详细文档 |
|------|------|---------|
| 成员管理 | 踢人、禁言、设置管理员 | [群组 API](group.md) |
| 群设置 | 修改群名称、全员禁言、退群 | [群组 API](group.md) |
| 群信息 | 获取群信息、群列表、成员列表 | [群组 API](group.md) |

**主要方法**:
- `set_group_kick()` - 踢出群成员
- `set_group_ban()` - 禁言群成员
- `set_group_admin()` - 设置管理员
- `set_group_card()` - 设置群名片
- `set_group_name()` - 设置群名称
- `get_group_info()` - 获取群信息
- `get_group_member_list()` - 获取群成员列表

### 3. 信息获取 API

用于获取账号、好友、群组等信息。

| 分类 | 说明 | 详细文档 |
|------|------|---------|
| 账号信息 | 获取登录信息、状态、版本 | [信息 API](info.md) |
| 用户信息 | 获取陌生人信息、好友列表 | [信息 API](info.md) |
| 群组信息 | 获取群信息、群列表、成员信息 | [群组 API](group.md) |

**主要方法**:
- `get_login_info()` - 获取登录信息
- `get_stranger_info()` - 获取陌生人信息
- `get_friend_list()` - 获取好友列表
- `get_status()` - 获取运行状态
- `get_version_info()` - 获取版本信息

### 4. 请求处理 API

用于处理好友请求和群邀请。

| 分类 | 说明 | 详细文档 |
|------|------|---------|
| 好友请求 | 同意/拒绝好友请求 | [客户端 API](client.md) |
| 群请求 | 同意/拒绝加群请求 | [群组 API](group.md) |

**主要方法**:
- `set_friend_add_request()` - 处理好友请求
- `set_group_add_request()` - 处理加群请求

### 5. 客户端 API

客户端生命周期管理和配置。

| 分类 | 说明 | 详细文档 |
|------|------|---------|
| 生命周期 | 启动、停止、运行 | [客户端 API](client.md) |
| Bot 管理 | 获取 Bot 实例 | [客户端 API](client.md) |
| 事件处理 | 注册事件处理器 | [客户端 API](client.md) |

**主要方法**:
- `start()` - 启动客户端
- `stop()` - 停止客户端
- `run_forever()` - 持续运行
- `get_bot()` - 获取 Bot 实例
- `on_message()` - 注册消息处理器
- `on_notice()` - 注册通知处理器
- `on_request()` - 注册请求处理器

## API 调用约定

### 异步调用

YunBot 的所有 API 方法都是异步的,必须使用 `await` 关键字调用。

```python
import asyncio
from yunbot import OneBotClient

async def main():
    client = OneBotClient.create_simple_client(
        connection_type="websocket",
        url="ws://localhost:3001"
    )
    
    await client.start()
    
    # ✅ 正确: 使用 await 调用异步方法
    result = await client.send_private_msg(user_id=123456789, message="你好")
    
    # ❌ 错误: 忘记使用 await
    # result = client.send_private_msg(user_id=123456789, message="你好")
    
    await client.stop()

asyncio.run(main())
```

### 返回值格式

所有 API 调用成功后都会返回一个字典 (Dict),包含 API 的返回数据。

```python
# 发送消息返回消息 ID
result = await client.send_private_msg(user_id=123456789, message="你好")
print(result)
# 输出: {"message_id": 123456}

# 获取登录信息返回用户信息
login_info = await client.get_login_info()
print(login_info)
# 输出: {"user_id": 123456789, "nickname": "机器人昵称"}

# 获取列表返回列表数据
friend_list = await client.get_friend_list()
print(friend_list)
# 输出: [{"user_id": 111, "nickname": "好友1"}, {"user_id": 222, "nickname": "好友2"}]
```

### 错误处理

API 调用可能会抛出异常,建议使用 try-except 捕获错误。

```python
from yunbot import ActionFailed, NetworkException, ApiNotAvailable

async def send_message_safely():
    try:
        # 尝试发送消息
        result = await client.send_private_msg(
            user_id=123456789,
            message="你好"
        )
        print(f"消息发送成功,消息 ID: {result['message_id']}")
        
    except ActionFailed as e:
        # API 调用失败 (如目标不存在、权限不足等)
        print(f"API 调用失败: {e}")
        
    except NetworkException as e:
        # 网络连接错误
        print(f"网络错误: {e}")
        
    except ApiNotAvailable as e:
        # API 不可用 (连接未建立)
        print(f"API 不可用: {e}")
        
    except Exception as e:
        # 其他未知错误
        print(f"未知错误: {e}")
```

## API 调用方式

YunBot 提供了多种 API 调用方式,您可以根据需要选择最方便的方式。

### 方式一: 通过 Client 调用

最常用的方式,直接通过客户端实例调用 API 方法。

```python
from yunbot import OneBotClient

async def main():
    client = OneBotClient.create_simple_client(
        connection_type="websocket",
        url="ws://localhost:3001"
    )
    
    await client.start()
    
    # 通过 client 直接调用
    await client.send_private_msg(user_id=123456789, message="你好")
    await client.send_group_msg(group_id=987654321, message="大家好")
    
    login_info = await client.get_login_info()
    print(f"Bot ID: {login_info['user_id']}")
    
    await client.stop()

asyncio.run(main())
```

### 方式二: 通过 Bot 实例调用

获取 Bot 实例后调用,适用于多 Bot 场景。

```python
async def main():
    client = OneBotClient.create_simple_client(
        connection_type="websocket",
        url="ws://localhost:3001"
    )
    
    await client.start()
    
    # 获取 Bot 实例
    bot = client.get_bot()
    
    # 通过 bot 调用 API
    await bot.send_private_msg(user_id=123456789, message="你好")
    await bot.send_group_msg(group_id=987654321, message="大家好")
    
    await client.stop()
```

### 方式三: 使用 call_api 通用方法

使用通用的 call_api 方法调用任意 API。

```python
async def main():
    client = OneBotClient.create_simple_client(
        connection_type="websocket",
        url="ws://localhost:3001"
    )
    
    await client.start()
    
    # 使用 call_api 调用
    result = await client.call_api(
        "send_private_msg",
        user_id=123456789,
        message="你好"
    )
    
    await client.stop()
```

### 方式四: 动态方法调用

YunBot 支持动态调用未显式定义的 API 方法。

```python
async def main():
    client = OneBotClient.create_simple_client(
        connection_type="websocket",
        url="ws://localhost:3001"
    )
    
    await client.start()
    
    # 动态调用 API (任何 OneBot v11 标准 API)
    await client.send_private_msg(user_id=123456789, message="你好")
    
    # 即使某个方法未在代码中显式定义,也可以调用
    await client.some_custom_api(param1="value1", param2="value2")
    
    await client.stop()
```

## 参数说明

### 必需参数 vs 可选参数

API 方法的参数分为必需参数和可选参数:

```python
# send_private_msg() 方法
await client.send_private_msg(
    user_id=123456789,        # 必需: 目标用户 ID
    message="你好",            # 必需: 消息内容
    auto_escape=False         # 可选: 是否自动转义,默认 False
)

# set_group_ban() 方法
await client.set_group_ban(
    group_id=987654321,       # 必需: 群号
    user_id=123456789,        # 必需: 要禁言的用户 ID
    duration=30 * 60          # 可选: 禁言时长(秒),默认 30 分钟
)
```

### 参数类型

API 参数需要遵循正确的类型:

```python
# int 类型参数
await client.send_private_msg(
    user_id=123456789,  # int: 用户 ID
    message="你好"
)

# bool 类型参数
await client.get_stranger_info(
    user_id=123456789,
    no_cache=True  # bool: 是否不使用缓存
)

# str 类型参数
await client.set_group_card(
    group_id=987654321,
    user_id=123456789,
    card="新群名片"  # str: 群名片内容
)

# Union 类型参数 (多种类型)
from yunbot import Message, MessageSegment

await client.send_private_msg(
    user_id=123456789,
    message="字符串消息"  # str
)

await client.send_private_msg(
    user_id=123456789,
    message=Message([MessageSegment.text("Message 对象")])  # Message
)

await client.send_private_msg(
    user_id=123456789,
    message=[MessageSegment.text("消息段列表")]  # List[MessageSegment]
)
```

## 常用 API 快速参考

### 消息相关

```python
# 发送私聊消息
await client.send_private_msg(user_id=123456789, message="你好")

# 发送群消息
await client.send_group_msg(group_id=987654321, message="大家好")

# 撤回消息
await client.delete_msg(message_id=12345678)

# 获取消息
msg_info = await client.get_msg(message_id=12345678)

# 发送点赞
await client.send_like(user_id=123456789, times=10)
```

### 群组管理

```python
# 踢出群成员
await client.set_group_kick(group_id=987654321, user_id=123456789)

# 禁言群成员 (30 分钟)
await client.set_group_ban(group_id=987654321, user_id=123456789, duration=30*60)

# 解除禁言
await client.set_group_ban(group_id=987654321, user_id=123456789, duration=0)

# 设置管理员
await client.set_group_admin(group_id=987654321, user_id=123456789, enable=True)

# 设置群名片
await client.set_group_card(group_id=987654321, user_id=123456789, card="新名片")

# 修改群名称
await client.set_group_name(group_id=987654321, group_name="新群名")

# 退出群聊
await client.set_group_leave(group_id=987654321)
```

### 信息获取

```python
# 获取登录信息
login_info = await client.get_login_info()
print(f"Bot ID: {login_info['user_id']}, 昵称: {login_info['nickname']}")

# 获取陌生人信息
stranger_info = await client.get_stranger_info(user_id=123456789)
print(f"昵称: {stranger_info['nickname']}")

# 获取好友列表
friend_list = await client.get_friend_list()
for friend in friend_list:
    print(f"好友: {friend['nickname']} ({friend['user_id']})")

# 获取群列表
group_list = await client.get_group_list()
for group in group_list:
    print(f"群: {group['group_name']} ({group['group_id']})")

# 获取群成员信息
member_info = await client.get_group_member_info(
    group_id=987654321,
    user_id=123456789
)

# 获取运行状态
status = await client.get_status()
print(f"在线: {status['online']}, 状态良好: {status['good']}")

# 获取版本信息
version_info = await client.get_version_info()
print(f"应用: {version_info['app_name']} v{version_info['app_version']}")
```

### 请求处理

```python
# 在请求事件处理器中处理好友请求
@client.on_request
async def handle_request(event):
    if event.request_type == "friend":
        # 同意好友请求
        await client.set_friend_add_request(
            flag=event.flag,
            approve=True,
            remark="新朋友"
        )
    elif event.request_type == "group":
        # 同意加群请求
        await client.set_group_add_request(
            flag=event.flag,
            sub_type=event.sub_type,
            approve=True
        )
```

## 最佳实践

### 1. 错误处理

```python
# ✅ 推荐: 捕获具体的异常类型
from yunbot import ActionFailed, NetworkException

try:
    result = await client.send_private_msg(user_id=123456789, message="你好")
except ActionFailed as e:
    logger.error(f"消息发送失败: {e}")
except NetworkException as e:
    logger.error(f"网络错误: {e}")
```

### 2. 参数验证

```python
# ✅ 推荐: 在调用 API 前验证参数
def validate_user_id(user_id: int) -> bool:
    """验证用户 ID"""
    return isinstance(user_id, int) and user_id > 0

if validate_user_id(user_id):
    await client.send_private_msg(user_id=user_id, message="你好")
else:
    logger.error("无效的用户 ID")
```

### 3. 批量操作

```python
# ✅ 推荐: 批量操作时添加延迟
async def send_to_multiple_users(user_ids: list, message: str):
    """向多个用户发送消息"""
    for user_id in user_ids:
        try:
            await client.send_private_msg(user_id=user_id, message=message)
            await asyncio.sleep(1)  # 避免频繁调用
        except Exception as e:
            logger.error(f"发送给 {user_id} 失败: {e}")
```

### 4. 结果缓存

```python
# ✅ 推荐: 缓存不常变化的数据
from functools import lru_cache

@lru_cache(maxsize=100)
async def get_cached_group_info(group_id: int):
    """获取缓存的群信息"""
    return await client.get_group_info(group_id=group_id, no_cache=False)
```

## 注意事项

1. **API 可用性**: 某些 API 可能在特定的 OneBot 实现中不可用,调用前需注意异常处理
2. **权限要求**: 部分群管理 API 需要机器人具有管理员或群主权限
3. **频率限制**: 频繁调用 API 可能触发 QQ 的风控机制,建议添加适当延迟
4. **参数格式**: 确保参数类型正确,错误的参数类型会导致 API 调用失败
5. **异步执行**: 所有 API 必须在异步环境中调用,使用 `await` 关键字

## 相关文档

- [客户端 API](client.md) - OneBotClient 类的完整 API
- [消息 API](message.md) - 消息发送和管理相关 API
- [群组管理 API](group.md) - 群组和成员管理 API
- [信息获取 API](info.md) - 信息查询相关 API
- [客户端使用指南](../guide/client.md) - 客户端的基本使用
- [事件处理指南](../guide/events.md) - 事件处理机制
