# 信息获取 API

## 概述

信息获取 API 提供了获取账号信息、用户信息、系统状态等功能。本文档详细介绍所有与信息查询相关的 API 方法。

## 方法列表

### 账号信息

| 方法 | 说明 |
|------|------|
| get_login_info() | 获取登录账号信息 |
| get_status() | 获取运行状态 |
| get_version_info() | 获取版本信息 |

### 用户信息

| 方法 | 说明 |
|------|------|
| get_stranger_info() | 获取陌生人信息 |
| get_friend_list() | 获取好友列表 |

### 文件和资源

| 方法 | 说明 |
|------|------|
| get_image() | 获取图片信息 |
| get_record() | 获取语音信息 |
| can_send_image() | 检查是否可以发送图片 |
| can_send_record() | 检查是否可以发送语音 |

### Cookie 和凭证

| 方法 | 说明 |
|------|------|
| get_cookies() | 获取 Cookies |
| get_csrf_token() | 获取 CSRF Token |
| get_credentials() | 获取凭证 |

### 系统控制

| 方法 | 说明 |
|------|------|
| set_restart() | 重启 OneBot 实现 |
| clean_cache() | 清理缓存 |

## 账号信息 API

### get_login_info()

**功能**: 获取登录账号信息

**签名**:
```python
async def get_login_info(self) -> Dict[str, Any]:
    """获取登录信息"""
```

**返回值**:
```python
{
    "user_id": 123456789,
    "nickname": "机器人昵称"
}
```

**示例**:
```python
login_info = await client.get_login_info()
print(f"Bot ID: {login_info['user_id']}")
print(f"Bot 昵称: {login_info['nickname']}")
```

---

### get_status()

**功能**: 获取运行状态

**签名**:
```python
async def get_status(self) -> Dict[str, Any]:
    """获取运行状态"""
```

**返回值**:
```python
{
    "online": True,       # 是否在线
    "good": True          # 状态是否良好
}
```

**示例**:
```python
status = await client.get_status()
print(f"在线状态: {status['online']}")
print(f"运行良好: {status['good']}")

if status['online'] and status['good']:
    print("Bot 运行正常")
else:
    print("Bot 运行异常")
```

---

### get_version_info()

**功能**: 获取 OneBot 实现的版本信息

**签名**:
```python
async def get_version_info(self) -> Dict[str, Any]:
    """获取版本信息"""
```

**返回值**:
```python
{
    "app_name": "应用名称",
    "app_version": "版本号",
    "protocol_version": "v11"
}
```

**示例**:
```python
version_info = await client.get_version_info()
print(f"应用: {version_info['app_name']}")
print(f"版本: {version_info['app_version']}")
print(f"协议版本: {version_info['protocol_version']}")
```

---

## 用户信息 API

### get_stranger_info()

**功能**: 获取陌生人信息

**签名**:
```python
async def get_stranger_info(
    self,
    user_id: int,
    no_cache: bool = False
) -> Dict[str, Any]:
    """获取陌生人信息"""
```

**参数**:

| 参数 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| user_id | int | 是 | - | 用户 ID |
| no_cache | bool | 否 | False | 是否不使用缓存 |

**返回值**:
```python
{
    "user_id": 123456789,
    "nickname": "用户昵称",
    "sex": "male",        # male/female/unknown
    "age": 18
}
```

**示例**:
```python
# 获取用户信息
user_info = await client.get_stranger_info(user_id=123456789)
print(f"昵称: {user_info['nickname']}")
print(f"性别: {user_info['sex']}")
print(f"年龄: {user_info['age']}")

# 不使用缓存,获取最新信息
user_info = await client.get_stranger_info(
    user_id=123456789,
    no_cache=True
)
```

---

### get_friend_list()

**功能**: 获取好友列表

**签名**:
```python
async def get_friend_list(self) -> List[Dict[str, Any]]:
    """获取好友列表"""
```

**返回值**: 好友信息列表
```python
[
    {
        "user_id": 123456789,
        "nickname": "好友1",
        "remark": "备注1"
    },
    {
        "user_id": 987654321,
        "nickname": "好友2",
        "remark": "备注2"
    }
]
```

**示例**:
```python
# 获取好友列表
friend_list = await client.get_friend_list()

# 遍历好友
for friend in friend_list:
    print(f"好友: {friend['nickname']} ({friend['user_id']})")
    if 'remark' in friend and friend['remark']:
        print(f"  备注: {friend['remark']}")

# 统计好友数量
print(f"好友总数: {len(friend_list)}")
```

---

## 文件和资源 API

### get_image()

**功能**: 获取图片信息

**签名**:
```python
async def get_image(self, file: str) -> Dict[str, Any]:
    """获取图片信息"""
```

**参数**:

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| file | str | 是 | 图片文件名 |

**返回值**:
```python
{
    "file": "文件名",
    "url": "图片URL"
}
```

**示例**:
```python
image_info = await client.get_image(file="xxxxx.image")
print(f"图片 URL: {image_info['url']}")
```

---

### get_record()

**功能**: 获取语音信息

**签名**:
```python
async def get_record(
    self,
    file: str,
    out_format: str
) -> Dict[str, Any]:
    """获取语音信息"""
```

**参数**:

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| file | str | 是 | 语音文件名 |
| out_format | str | 是 | 输出格式 (mp3/amr/wma/m4a/spx/ogg/wav/flac) |

**返回值**:
```python
{
    "file": "文件路径"
}
```

**示例**:
```python
record_info = await client.get_record(
    file="xxxxx.record",
    out_format="mp3"
)
print(f"语音文件: {record_info['file']}")
```

---

### can_send_image()

**功能**: 检查是否可以发送图片

**签名**:
```python
async def can_send_image(self) -> Dict[str, Any]:
    """检查是否可以发送图片"""
```

**返回值**:
```python
{
    "yes": True  # 是否可以发送
}
```

**示例**:
```python
result = await client.can_send_image()
if result['yes']:
    print("可以发送图片")
else:
    print("不能发送图片")
```

---

### can_send_record()

**功能**: 检查是否可以发送语音

**签名**:
```python
async def can_send_record(self) -> Dict[str, Any]:
    """检查是否可以发送语音"""
```

**返回值**:
```python
{
    "yes": True  # 是否可以发送
}
```

**示例**:
```python
result = await client.can_send_record()
if result['yes']:
    print("可以发送语音")
else:
    print("不能发送语音")
```

---

## Cookie 和凭证 API

### get_cookies()

**功能**: 获取 Cookies

**签名**:
```python
async def get_cookies(self, domain: str) -> Dict[str, Any]:
    """获取 Cookies"""
```

**参数**:

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| domain | str | 是 | 域名 |

**返回值**:
```python
{
    "cookies": "cookie字符串"
}
```

**示例**:
```python
cookies = await client.get_cookies(domain="qun.qq.com")
print(f"Cookies: {cookies['cookies']}")
```

---

### get_csrf_token()

**功能**: 获取 CSRF Token

**签名**:
```python
async def get_csrf_token(self) -> Dict[str, Any]:
    """获取 CSRF Token"""
```

**返回值**:
```python
{
    "token": 123456789
}
```

**示例**:
```python
result = await client.get_csrf_token()
print(f"CSRF Token: {result['token']}")
```

---

### get_credentials()

**功能**: 获取 QQ 相关接口凭证

**签名**:
```python
async def get_credentials(self, domain: str) -> Dict[str, Any]:
    """获取凭证"""
```

**参数**:

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| domain | str | 是 | 域名 |

**返回值**:
```python
{
    "cookies": "cookie字符串",
    "csrf_token": 123456789
}
```

**示例**:
```python
credentials = await client.get_credentials(domain="qun.qq.com")
print(f"Cookies: {credentials['cookies']}")
print(f"CSRF Token: {credentials['csrf_token']}")
```

---

## 系统控制 API

### set_restart()

**功能**: 重启 OneBot 实现

**签名**:
```python
async def set_restart(self, delay: int = 0) -> Dict[str, Any]:
    """重启"""
```

**参数**:

| 参数 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| delay | int | 否 | 0 | 延迟重启时间(毫秒) |

**返回值**: 空字典

**示例**:
```python
# 立即重启
await client.set_restart()

# 延迟 5 秒后重启
await client.set_restart(delay=5000)
```

**注意事项**:
- 此操作会重启整个 OneBot 实现,而不仅仅是断开连接

---

### clean_cache()

**功能**: 清理缓存

**签名**:
```python
async def clean_cache(self) -> Dict[str, Any]:
    """清理缓存"""
```

**返回值**: 空字典

**示例**:
```python
await client.clean_cache()
print("缓存已清理")
```

---

## 完整示例

### 示例 1: 获取机器人信息

```python
import asyncio
from yunbot import OneBotClient

async def main():
    client = OneBotClient.create_simple_client(
        connection_type="websocket",
        url="ws://localhost:3001"
    )
    
    await client.start()
    
    # 获取登录信息
    login_info = await client.get_login_info()
    print(f"Bot ID: {login_info['user_id']}")
    print(f"Bot 昵称: {login_info['nickname']}")
    
    # 获取运行状态
    status = await client.get_status()
    print(f"在线: {status['online']}")
    print(f"状态良好: {status['good']}")
    
    # 获取版本信息
    version = await client.get_version_info()
    print(f"应用: {version['app_name']} v{version['app_version']}")
    
    await client.stop()

asyncio.run(main())
```

### 示例 2: 好友列表管理

```python
async def main():
    client = OneBotClient.create_simple_client(
        connection_type="websocket",
        url="ws://localhost:3001"
    )
    
    await client.start()
    
    # 获取好友列表
    friend_list = await client.get_friend_list()
    print(f"好友总数: {len(friend_list)}")
    
    # 遍历好友并获取详细信息
    for friend in friend_list[:5]:  # 只显示前 5 个
        user_id = friend['user_id']
        
        # 获取陌生人信息(包含更多详情)
        info = await client.get_stranger_info(user_id=user_id)
        
        print(f"\n好友: {friend['nickname']}")
        print(f"  ID: {user_id}")
        print(f"  备注: {friend.get('remark', '无')}")
        print(f"  性别: {info.get('sex', '未知')}")
        print(f"  年龄: {info.get('age', '未知')}")
    
    await client.stop()
```

### 示例 3: 状态监控

```python
async def main():
    client = OneBotClient.create_simple_client(
        connection_type="websocket",
        url="ws://localhost:3001"
    )
    
    await client.start()
    
    # 定期检查状态
    while True:
        try:
            status = await client.get_status()
            
            if status['online'] and status['good']:
                print("✓ Bot 运行正常")
            else:
                print("✗ Bot 运行异常")
                print(f"  在线: {status['online']}")
                print(f"  良好: {status['good']}")
            
            # 每 60 秒检查一次
            await asyncio.sleep(60)
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"状态检查失败: {e}")
            await asyncio.sleep(60)
    
    await client.stop()
```

### 示例 4: 信息展示机器人

```python
from yunbot import OneBotClient, MessageSegment

async def main():
    client = OneBotClient.create_simple_client(
        connection_type="websocket",
        url="ws://localhost:3001"
    )
    
    @client.on_message
    async def handle_message(event):
        from yunbot import Message
        msg = Message(event.message)
        text = msg.extract_plain_text().strip()
        
        # /info 命令 - 显示 Bot 信息
        if text == "/info":
            login_info = await client.get_login_info()
            status = await client.get_status()
            version = await client.get_version_info()
            
            info_msg = f"""🤖 Bot 信息
ID: {login_info['user_id']}
昵称: {login_info['nickname']}
在线: {'是' if status['online'] else '否'}
状态: {'良好' if status['good'] else '异常'}
应用: {version['app_name']}
版本: {version['app_version']}"""
            
            if hasattr(event, 'group_id'):
                await client.send_group_msg(event.group_id, info_msg)
            else:
                await client.send_private_msg(event.user_id, info_msg)
        
        # /userinfo 命令 - 显示用户信息
        elif text == "/userinfo":
            try:
                user_info = await client.get_stranger_info(user_id=event.user_id)
                
                info_msg = f"""👤 用户信息
ID: {user_info['user_id']}
昵称: {user_info['nickname']}
性别: {user_info.get('sex', '未知')}
年龄: {user_info.get('age', '未知')}"""
                
                if hasattr(event, 'group_id'):
                    await client.send_group_msg(event.group_id, info_msg)
                else:
                    await client.send_private_msg(event.user_id, info_msg)
            except Exception as e:
                print(f"获取用户信息失败: {e}")
    
    await client.start()
    await client.run_forever()

asyncio.run(main())
```

## 注意事项

1. **缓存机制**: 部分 API 支持 `no_cache` 参数,设置为 True 可获取最新数据,但会增加响应时间
2. **权限要求**: 某些 API 可能需要特定权限,调用失败时检查权限设置
3. **频率限制**: 频繁调用信息获取 API 可能触发风控,建议添加缓存和延迟
4. **异常处理**: 建议使用 try-except 捕获可能的异常

## 相关文档

- [API 概览](overview.md) - API 总览
- [客户端 API](client.md) - 客户端 API
- [群组管理 API](group.md) - 群组管理 API
- [消息 API](message.md) - 消息相关 API
