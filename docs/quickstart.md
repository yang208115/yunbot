# 快速开始

本文档将帮助您在 5-10 分钟内创建并运行第一个 YunBot 机器人。

## 前置准备

在开始之前,请确保:

- ✅ 已完成 [安装指南](installation.md) 中的安装步骤
- ✅ 拥有一个可用的 OneBot v11 实现 (如 go-cqhttp, Lagrange 等)
- ✅ 知道 OneBot 服务的 WebSocket 地址和访问令牌 (如果需要)

## 第一个机器人

### 步骤 1: 创建 Python 文件

创建一个新文件 `my_first_bot.py`:

```python
import asyncio
from yunbot import OneBotClient, MessageSegment

async def main():
    # 创建客户端
    client = OneBotClient.create_simple_client(
        connection_type="websocket",
        url="ws://localhost:3001",      # WebSocket 服务器地址
        access_token="your_token",      # 访问令牌（可选）
        heartbeat_interval=30.0         # 心跳间隔（秒）
    )

    # 注册消息事件处理器
    @client.on_message
    async def handle_message(event):
        # 打印收到的消息
        print(f"收到消息: {event.message}")
        
        # 构建回复消息
        reply_msg = MessageSegment.text("你好!我收到了你的消息: ") + MessageSegment.text(str(event.message))
        
        # 判断消息类型并回复
        if hasattr(event, 'group_id'):
            # 群消息回复
            await client.send_group_msg(group_id=event.group_id, message=reply_msg)
        else:
            # 私聊消息回复
            await client.send_private_msg(user_id=event.user_id, message=reply_msg)

    # 启动客户端
    try:
        await client.start()
        print("✅ 客户端启动成功!")
        await client.run_forever()
    except KeyboardInterrupt:
        print("⏹️ 正在停止客户端...")
    finally:
        await client.stop()
        print("👋 客户端已停止")

if __name__ == "__main__":
    asyncio.run(main())
```

### 步骤 2: 修改配置

将代码中的连接信息修改为您的实际配置:

```python
client = OneBotClient.create_simple_client(
    connection_type="websocket",
    url="ws://localhost:3001",      # 修改为您的 WebSocket 地址
    access_token="your_token",      # 修改为您的访问令牌,如无则删除此行
    heartbeat_interval=30.0
)
```

### 步骤 3: 运行机器人

在终端中运行:

```bash
python my_first_bot.py
```

您应该看到类似以下输出:

```
✅ 客户端启动成功!
```

### 步骤 4: 测试机器人

向您的机器人发送任意消息,机器人将会回复相同的内容!

**私聊测试**:
- 发送: `你好`
- 机器人回复: `你好!我收到了你的消息: 你好`

**群聊测试**:
- 在群聊中发送: `测试`
- 机器人回复: `你好!我收到了你的消息: 测试`

### 步骤 5: 停止机器人

在运行机器人的终端中按 `Ctrl+C` 停止机器人。

## 代码解析

让我们逐步理解这段代码:

### 1. 导入必要的模块

```python
import asyncio
from yunbot import OneBotClient, MessageSegment
```

- `asyncio`: Python 的异步 I/O 库
- `OneBotClient`: YunBot 的客户端类
- `MessageSegment`: 消息段构建类

### 2. 创建客户端

```python
client = OneBotClient.create_simple_client(
    connection_type="websocket",    # 连接类型
    url="ws://localhost:3001",      # WebSocket 地址
    access_token="your_token",      # 访问令牌（可选）
    heartbeat_interval=30.0         # 心跳间隔
)
```

使用 `create_simple_client()` 工厂方法创建客户端,这是最简单的创建方式。

### 3. 注册事件处理器

```python
@client.on_message
async def handle_message(event):
    # 处理消息事件
    ...
```

使用装饰器 `@client.on_message` 注册消息事件处理器。每当收到消息时,这个函数就会被调用。

### 4. 构建和发送消息

```python
# 构建消息
reply_msg = MessageSegment.text("你好!") + MessageSegment.text("消息内容")

# 发送私聊消息
await client.send_private_msg(user_id=event.user_id, message=reply_msg)

# 发送群消息
await client.send_group_msg(group_id=event.group_id, message=reply_msg)
```

使用 `MessageSegment` 构建消息,使用 `send_private_msg()` 或 `send_group_msg()` 发送消息。

### 5. 启动和运行客户端

```python
await client.start()            # 启动客户端
await client.run_forever()      # 持续运行
```

`start()` 方法初始化连接,`run_forever()` 方法保持程序运行。

## 添加更多功能

### 处理多种事件

```python
# 处理通知事件
@client.on_notice
async def handle_notice(event):
    print(f"收到通知: {event.notice_type}")

# 处理请求事件
@client.on_request
async def handle_request(event):
    print(f"收到请求: {event.request_type}")
```

### 构建丰富的消息

```python
# 发送带表情的消息
msg = MessageSegment.text("你好!") + MessageSegment.face(178)

# 发送 @ 某人的消息
msg = MessageSegment.at(user_id) + MessageSegment.text(" 你好!")

# 发送图片
msg = MessageSegment.image(file="https://example.com/image.jpg")
```

### 添加简单的命令处理

```python
@client.on_message
async def handle_message(event):
    # 获取消息文本
    message_text = str(event.message)
    
    # 处理命令
    if message_text == "/help":
        help_msg = MessageSegment.text("可用命令:\n/help - 显示帮助\n/ping - 测试连接")
        await client.send_private_msg(user_id=event.user_id, message=help_msg)
    elif message_text == "/ping":
        await client.send_private_msg(user_id=event.user_id, message="pong!")
```

## 常见问题

### Q: 如何获取 WebSocket 地址?

A: WebSocket 地址由您使用的 OneBot 实现提供。例如:
- go-cqhttp: 默认为 `ws://localhost:5700`
- Lagrange: 根据配置文件中的设置

查看您的 OneBot 实现的配置文件或文档。

### Q: 访问令牌是什么?

A: 访问令牌 (access_token) 是一个安全措施,用于验证客户端身份。如果您的 OneBot 实现设置了访问令牌,您需要在创建客户端时提供相同的令牌。如果未设置,可以不提供。

### Q: 如何区分私聊和群聊消息?

A: 检查事件对象的属性:

```python
@client.on_message
async def handle_message(event):
    if hasattr(event, 'group_id'):
        # 这是群消息
        print(f"群消息: 群号 {event.group_id}")
    else:
        # 这是私聊消息
        print(f"私聊消息: 用户 {event.user_id}")
```

### Q: 机器人不回复消息怎么办?

A: 检查以下几点:
1. WebSocket 地址和端口是否正确
2. OneBot 实现是否正常运行
3. 是否设置了访问令牌,且令牌正确
4. 查看控制台是否有错误信息

### Q: 如何让机器人只响应特定用户或群组?

A: 在事件处理器中添加条件判断:

```python
@client.on_message
async def handle_message(event):
    # 只响应特定用户
    if event.user_id != 123456789:
        return
    
    # 只响应特定群组
    if hasattr(event, 'group_id') and event.group_id != 987654321:
        return
    
    # 处理消息
    ...
```

## 下一步学习

现在您已经创建了第一个机器人!接下来可以:

- 📖 学习 [客户端使用](guide/client.md) 了解客户端的更多功能
- 📬 学习 [事件处理](guide/events.md) 处理更多类型的事件
- 💬 学习 [消息构建](guide/messages.md) 发送更复杂的消息
- 📚 查看 [API 参考](api/overview.md) 了解所有可用的 API
- 🎯 查看 [命令处理机器人示例](examples/command-bot.md) 学习更高级的功能

## 相关文档

- [安装指南](installation.md)
- [客户端使用](guide/client.md)
- [事件处理](guide/events.md)
- [基础机器人示例](examples/basic-bot.md)
