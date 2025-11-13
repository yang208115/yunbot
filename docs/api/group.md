# 群组管理 API

## 概述

群组管理 API 提供了群成员管理、群设置和群信息获取等功能。本文档详细介绍所有与群组相关的 API 方法。

## 方法列表

### 成员管理

| 方法 | 说明 |
|------|------|
| set_group_kick() | 踢出群成员 |
| set_group_ban() | 禁言群成员 |
| set_group_admin() | 设置/取消管理员 |
| set_group_card() | 设置群名片 |
| set_group_special_title() | 设置专属头衔 |

### 群设置

| 方法 | 说明 |
|------|------|
| set_group_name() | 设置群名称 |
| set_group_whole_ban() | 全员禁言 |
| set_group_anonymous() | 设置匿名聊天 |
| set_group_leave() | 退出群聊 |

### 信息获取

| 方法 | 说明 |
|------|------|
| get_group_info() | 获取群信息 |
| get_group_list() | 获取群列表 |
| get_group_member_info() | 获取群成员信息 |
| get_group_member_list() | 获取群成员列表 |
| get_group_honor_info() | 获取群荣誉信息 |

### 请求处理

| 方法 | 说明 |
|------|------|
| set_group_add_request() | 处理加群请求 |

## 成员管理 API

### set_group_kick()

**功能**: 踢出群成员

**签名**:
```python
async def set_group_kick(
    self,
    group_id: int,
    user_id: int,
    reject_add_request: bool = False
) -> Dict[str, Any]:
    """踢出群成员"""
```

**参数**:

| 参数 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| group_id | int | 是 | - | 群号 |
| user_id | int | 是 | - | 要踢出的用户 ID |
| reject_add_request | bool | 否 | False | 是否拒绝再次加群请求 |

**返回值**: 空字典

**示例**:
```python
# 踢出群成员
await client.set_group_kick(
    group_id=987654321,
    user_id=123456789
)

# 踢出并拒绝再次加群
await client.set_group_kick(
    group_id=987654321,
    user_id=123456789,
    reject_add_request=True
)
```

**注意事项**:
- 需要管理员或群主权限
- 不能踢出管理员或群主

---

### set_group_ban()

**功能**: 禁言群成员

**签名**:
```python
async def set_group_ban(
    self,
    group_id: int,
    user_id: int,
    duration: int = 30 * 60
) -> Dict[str, Any]:
    """禁言群成员"""
```

**参数**:

| 参数 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| group_id | int | 是 | - | 群号 |
| user_id | int | 是 | - | 要禁言的用户 ID |
| duration | int | 否 | 1800 | 禁言时长(秒),0 表示解除禁言 |

**返回值**: 空字典

**示例**:
```python
# 禁言 30 分钟
await client.set_group_ban(
    group_id=987654321,
    user_id=123456789,
    duration=30 * 60
)

# 禁言 1 小时
await client.set_group_ban(
    group_id=987654321,
    user_id=123456789,
    duration=3600
)

# 解除禁言
await client.set_group_ban(
    group_id=987654321,
    user_id=123456789,
    duration=0
)
```

**注意事项**:
- 需要管理员或群主权限
- 不能禁言管理员或群主
- duration 为 0 时解除禁言

---

### set_group_admin()

**功能**: 设置/取消群管理员

**签名**:
```python
async def set_group_admin(
    self,
    group_id: int,
    user_id: int,
    enable: bool = True
) -> Dict[str, Any]:
    """设置群管理员"""
```

**参数**:

| 参数 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| group_id | int | 是 | - | 群号 |
| user_id | int | 是 | - | 用户 ID |
| enable | bool | 否 | True | True 设置管理员,False 取消管理员 |

**返回值**: 空字典

**示例**:
```python
# 设置管理员
await client.set_group_admin(
    group_id=987654321,
    user_id=123456789,
    enable=True
)

# 取消管理员
await client.set_group_admin(
    group_id=987654321,
    user_id=123456789,
    enable=False
)
```

**注意事项**:
- 只有群主可以设置管理员

---

### set_group_card()

**功能**: 设置群名片

**签名**:
```python
async def set_group_card(
    self,
    group_id: int,
    user_id: int,
    card: str = ""
) -> Dict[str, Any]:
    """设置群名片"""
```

**参数**:

| 参数 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| group_id | int | 是 | - | 群号 |
| user_id | int | 是 | - | 用户 ID |
| card | str | 否 | "" | 群名片,空字符串表示删除群名片 |

**返回值**: 空字典

**示例**:
```python
# 设置群名片
await client.set_group_card(
    group_id=987654321,
    user_id=123456789,
    card="管理员"
)

# 删除群名片
await client.set_group_card(
    group_id=987654321,
    user_id=123456789,
    card=""
)
```

---

### set_group_special_title()

**功能**: 设置群成员专属头衔

**签名**:
```python
async def set_group_special_title(
    self,
    group_id: int,
    user_id: int,
    special_title: str = "",
    duration: int = -1
) -> Dict[str, Any]:
    """设置专属头衔"""
```

**参数**:

| 参数 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| group_id | int | 是 | - | 群号 |
| user_id | int | 是 | - | 用户 ID |
| special_title | str | 否 | "" | 专属头衔,空字符串表示删除 |
| duration | int | 否 | -1 | 有效期(秒),-1 表示永久 |

**返回值**: 空字典

**示例**:
```python
# 设置专属头衔
await client.set_group_special_title(
    group_id=987654321,
    user_id=123456789,
    special_title="优秀成员",
    duration=-1  # 永久
)
```

**注意事项**:
- 只有群主可以设置专属头衔

---

## 群设置 API

### set_group_name()

**功能**: 设置群名称

**签名**:
```python
async def set_group_name(self, group_id: int, group_name: str) -> Dict[str, Any]:
    """设置群名称"""
```

**参数**:

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| group_id | int | 是 | 群号 |
| group_name | str | 是 | 新群名称 |

**返回值**: 空字典

**示例**:
```python
await client.set_group_name(
    group_id=987654321,
    group_name="新群名称"
)
```

**注意事项**:
- 需要管理员或群主权限

---

### set_group_whole_ban()

**功能**: 设置全员禁言

**签名**:
```python
async def set_group_whole_ban(
    self,
    group_id: int,
    enable: bool = True
) -> Dict[str, Any]:
    """设置全员禁言"""
```

**参数**:

| 参数 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| group_id | int | 是 | - | 群号 |
| enable | bool | 否 | True | True 开启全员禁言,False 解除 |

**返回值**: 空字典

**示例**:
```python
# 开启全员禁言
await client.set_group_whole_ban(
    group_id=987654321,
    enable=True
)

# 解除全员禁言
await client.set_group_whole_ban(
    group_id=987654321,
    enable=False
)
```

**注意事项**:
- 需要管理员或群主权限
- 全员禁言不影响管理员

---

### set_group_anonymous()

**功能**: 设置群匿名聊天

**签名**:
```python
async def set_group_anonymous(
    self,
    group_id: int,
    enable: bool = True
) -> Dict[str, Any]:
    """设置群匿名聊天"""
```

**参数**:

| 参数 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| group_id | int | 是 | - | 群号 |
| enable | bool | 否 | True | True 开启匿名,False 关闭 |

**返回值**: 空字典

**示例**:
```python
# 开启匿名聊天
await client.set_group_anonymous(group_id=987654321, enable=True)

# 关闭匿名聊天
await client.set_group_anonymous(group_id=987654321, enable=False)
```

---

### set_group_leave()

**功能**: 退出群聊

**签名**:
```python
async def set_group_leave(
    self,
    group_id: int,
    is_dismiss: bool = False
) -> Dict[str, Any]:
    """退出群聊"""
```

**参数**:

| 参数 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| group_id | int | 是 | - | 群号 |
| is_dismiss | bool | 否 | False | 是否解散群(仅群主可用) |

**返回值**: 空字典

**示例**:
```python
# 退出群聊
await client.set_group_leave(group_id=987654321)

# 解散群(仅群主)
await client.set_group_leave(group_id=987654321, is_dismiss=True)
```

---

## 信息获取 API

### get_group_info()

**功能**: 获取群信息

**签名**:
```python
async def get_group_info(
    self,
    group_id: int,
    no_cache: bool = False
) -> Dict[str, Any]:
    """获取群信息"""
```

**参数**:

| 参数 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| group_id | int | 是 | - | 群号 |
| no_cache | bool | 否 | False | 是否不使用缓存 |

**返回值**:
```python
{
    "group_id": 987654321,
    "group_name": "群名称",
    "member_count": 100,
    "max_member_count": 500
}
```

**示例**:
```python
group_info = await client.get_group_info(group_id=987654321)
print(f"群名: {group_info['group_name']}")
print(f"成员数: {group_info['member_count']}")
```

---

### get_group_list()

**功能**: 获取群列表

**签名**:
```python
async def get_group_list(self) -> List[Dict[str, Any]]:
    """获取群列表"""
```

**返回值**: 群信息列表

**示例**:
```python
group_list = await client.get_group_list()
for group in group_list:
    print(f"群: {group['group_name']} ({group['group_id']})")
```

---

### get_group_member_info()

**功能**: 获取群成员信息

**签名**:
```python
async def get_group_member_info(
    self,
    group_id: int,
    user_id: int,
    no_cache: bool = False
) -> Dict[str, Any]:
    """获取群成员信息"""
```

**参数**:

| 参数 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| group_id | int | 是 | - | 群号 |
| user_id | int | 是 | - | 用户 ID |
| no_cache | bool | 否 | False | 是否不使用缓存 |

**返回值**:
```python
{
    "group_id": 987654321,
    "user_id": 123456789,
    "nickname": "昵称",
    "card": "群名片",
    "role": "member"  # owner/admin/member
}
```

**示例**:
```python
member_info = await client.get_group_member_info(
    group_id=987654321,
    user_id=123456789
)
print(f"群名片: {member_info['card']}")
print(f"角色: {member_info['role']}")
```

---

### get_group_member_list()

**功能**: 获取群成员列表

**签名**:
```python
async def get_group_member_list(
    self,
    group_id: int
) -> List[Dict[str, Any]]:
    """获取群成员列表"""
```

**参数**:

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| group_id | int | 是 | 群号 |

**返回值**: 成员信息列表

**示例**:
```python
member_list = await client.get_group_member_list(group_id=987654321)
for member in member_list:
    print(f"{member['nickname']} ({member['user_id']})")
```

---

### get_group_honor_info()

**功能**: 获取群荣誉信息

**签名**:
```python
async def get_group_honor_info(
    self,
    group_id: int,
    type_: str
) -> Dict[str, Any]:
    """获取群荣誉信息"""
```

**参数**:

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| group_id | int | 是 | 群号 |
| type_ | str | 是 | 荣誉类型 (talkative/performer/legend/strong_newbie/emotion/all) |

**返回值**: 荣誉信息

**示例**:
```python
# 获取龙王信息
honor = await client.get_group_honor_info(
    group_id=987654321,
    type_="talkative"
)
```

---

## 请求处理 API

### set_group_add_request()

**功能**: 处理加群请求

**签名**:
```python
async def set_group_add_request(
    self,
    flag: str,
    sub_type: str,
    approve: bool = True,
    reason: str = ""
) -> Dict[str, Any]:
    """处理加群请求"""
```

**参数**:

| 参数 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| flag | str | 是 | - | 请求标识(从事件中获取) |
| sub_type | str | 是 | - | 请求类型(add/invite) |
| approve | bool | 否 | True | 是否同意请求 |
| reason | str | 否 | "" | 拒绝理由 |

**返回值**: 空字典

**示例**:
```python
@client.on_request
async def handle_request(event):
    if event.request_type == "group":
        # 同意加群请求
        await client.set_group_add_request(
            flag=event.flag,
            sub_type=event.sub_type,
            approve=True
        )
```

---

## 完整示例

### 示例 1: 群管理机器人

```python
from yunbot import OneBotClient, MessageSegment

async def main():
    client = OneBotClient.create_simple_client(
        connection_type="websocket",
        url="ws://localhost:3001"
    )
    
    @client.on_message
    async def handle_message(event):
        if not hasattr(event, 'group_id'):
            return  # 只处理群消息
        
        from yunbot import Message
        msg = Message(event.message)
        text = msg.extract_plain_text().strip()
        
        # 禁言命令
        if text.startswith("/ban"):
            if msg.has_segment("at"):
                at_seg = msg.get_segments("at")[0]
                target_id = int(at_seg.data['qq'])
                
                await client.set_group_ban(
                    group_id=event.group_id,
                    user_id=target_id,
                    duration=600  # 10 分钟
                )
        
        # 踢人命令
        elif text.startswith("/kick"):
            if msg.has_segment("at"):
                at_seg = msg.get_segments("at")[0]
                target_id = int(at_seg.data['qq'])
                
                await client.set_group_kick(
                    group_id=event.group_id,
                    user_id=target_id
                )
    
    await client.start()
    await client.run_forever()
```

## 相关文档

- [API 概览](overview.md) - API 总览
- [客户端 API](client.md) - 客户端 API
- [信息获取 API](info.md) - 信息查询 API
