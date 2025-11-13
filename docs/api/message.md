# 消息 API

## 概述

消息 API 提供了发送、获取、撤回消息等功能。本文档详细介绍所有与消息相关的 API 方法。

## 方法列表

| 方法 | 说明 |
|------|------|
| send_private_msg() | 发送私聊消息 |
| send_group_msg() | 发送群消息 |
| send_msg() | 通用消息发送 |
| delete_msg() | 撤回消息 |
| get_msg() | 获取消息 |
| get_forward_msg() | 获取合并转发消息 |
| send_like() | 发送点赞 |

## 方法详解

### send_private_msg()

**功能**: 发送私聊消息

**签名**:
```python
async def send_private_msg(
    self,
    user_id: int,
    message: Union[str, Message, List[MessageSegment]],
    auto_escape: bool = False
) -> Dict[str, Any]:
    """发送私聊消息"""
```

**参数**:

| 参数 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| user_id | int | 是 | - | 目标用户 ID |
| message | str/Message/List | 是 | - | 消息内容 |
| auto_escape | bool | 否 | False | 是否自动转义特殊字符 |

**返回值**:
```python
{
    "message_id": 123456  # 消息 ID
}
```

**示例**:
```python
# 发送文本消息
result = await client.send_private_msg(
    user_id=123456789,
    message="你好"
)

# 发送复杂消息
from yunbot import Message, MessageSegment
msg = Message([
    MessageSegment.text("你好!"),
    MessageSegment.face(178)
])
await client.send_private_msg(user_id=123456789, message=msg)
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
    auto_escape: bool = False
) -> Dict[str, Any]:
    """发送群消息"""
```

**参数**:

| 参数 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| group_id | int | 是 | - | 目标群 ID |
| message | str/Message/List | 是 | - | 消息内容 |
| auto_escape | bool | 否 | False | 是否自动转义特殊字符 |

**返回值**:
```python
{
    "message_id": 123456  # 消息 ID
}
```

**示例**:
```python
# 发送群消息
await client.send_group_msg(
    group_id=987654321,
    message="大家好"
)

# 发送@消息
await client.send_group_msg(
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
    user_id: Optional[int] = None,
    group_id: Optional[int] = None,
    message: Optional[Union[str, Message, List[MessageSegment]]] = None,
    auto_escape: bool = False
) -> Dict[str, Any]:
    """发送消息"""
```

**参数**:

| 参数 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| message_type | str | 是 | - | 消息类型 ("private" 或 "group") |
| user_id | int | 条件 | None | 用户 ID (private 时必需) |
| group_id | int | 条件 | None | 群 ID (group 时必需) |
| message | str/Message/List | 是 | None | 消息内容 |
| auto_escape | bool | 否 | False | 是否自动转义 |

**返回值**:
```python
{
    "message_id": 123456
}
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

### delete_msg()

**功能**: 撤回消息

**签名**:
```python
async def delete_msg(self, message_id: int) -> Dict[str, Any]:
    """撤回消息"""
```

**参数**:

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| message_id | int | 是 | 要撤回的消息 ID |

**返回值**: 空字典

**示例**:
```python
# 发送消息并撤回
result = await client.send_private_msg(
    user_id=123456789,
    message="这条消息将被撤回"
)

# 等待 3 秒后撤回
import asyncio
await asyncio.sleep(3)
await client.delete_msg(message_id=result['message_id'])
```

**注意事项**:
- 撤回消息有时间限制 (通常为 2 分钟)
- 只能撤回自己发送的消息

---

### get_msg()

**功能**: 获取消息详情

**签名**:
```python
async def get_msg(self, message_id: int) -> Dict[str, Any]:
    """获取消息"""
```

**参数**:

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| message_id | int | 是 | 消息 ID |

**返回值**:
```python
{
    "time": 1234567890,
    "message_type": "private",
    "message_id": 123456,
    "real_id": 123456,
    "sender": {
        "user_id": 123456789,
        "nickname": "昵称"
    },
    "message": [...]  # 消息段列表
}
```

**示例**:
```python
msg_info = await client.get_msg(message_id=123456)
print(f"消息来自: {msg_info['sender']['nickname']}")
```

---

### get_forward_msg()

**功能**: 获取合并转发消息内容

**签名**:
```python
async def get_forward_msg(self, message_id: int) -> Dict[str, Any]:
    """获取合并转发消息"""
```

**参数**:

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| message_id | int | 是 | 合并转发消息 ID |

**返回值**: 包含转发消息列表的字典

**示例**:
```python
forward_msg = await client.get_forward_msg(message_id=123456)
```

---

### send_like()

**功能**: 发送点赞 (赞)

**签名**:
```python
async def send_like(self, user_id: int, times: int = 1) -> Dict[str, Any]:
    """发送点赞"""
```

**参数**:

| 参数 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| user_id | int | 是 | - | 目标用户 ID |
| times | int | 否 | 1 | 点赞次数 (1-10) |

**返回值**: 空字典

**示例**:
```python
# 给用户点赞 10 次
await client.send_like(user_id=123456789, times=10)
```

**注意事项**:
- 每天点赞次数有上限
- times 参数范围为 1-10

---

## 完整示例

### 示例 1: 消息发送和撤回

```python
import asyncio
from yunbot import OneBotClient, MessageSegment

async def main():
    client = OneBotClient.create_simple_client(
        connection_type="websocket",
        url="ws://localhost:3001"
    )
    
    await client.start()
    
    # 发送消息
    result = await client.send_private_msg(
        user_id=123456789,
        message="这是一条测试消息,5秒后将被撤回"
    )
    
    message_id = result['message_id']
    print(f"消息已发送,ID: {message_id}")
    
    # 等待 5 秒
    await asyncio.sleep(5)
    
    # 撤回消息
    await client.delete_msg(message_id=message_id)
    print("消息已撤回")
    
    await client.stop()

asyncio.run(main())
```

### 示例 2: 消息回显

```python
from yunbot import OneBotClient, Message

async def main():
    client = OneBotClient.create_simple_client(
        connection_type="websocket",
        url="ws://localhost:3001"
    )
    
    @client.on_message
    async def handle_message(event):
        # 获取消息内容
        msg = Message(event.message)
        text = msg.extract_plain_text()
        
        # 回显消息
        reply = f"你发送的消息是: {text}"
        
        if hasattr(event, 'group_id'):
            await client.send_group_msg(event.group_id, reply)
        else:
            await client.send_private_msg(event.user_id, reply)
    
    await client.start()
    await client.run_forever()

asyncio.run(main())
```

## 相关文档

- [API 概览](overview.md) - API 总览
- [客户端 API](client.md) - 客户端 API
- [消息构建指南](../guide/messages.md) - 消息构建和发送
