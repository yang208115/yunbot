# 基础机器人示例

## 功能说明

这是一个最简单的机器人示例,展示了 YunBot 的基本功能:
- 连接到 OneBot 服务器
- 接收消息事件
- 发送消息回复
- 处理不同类型的消息 (私聊/群聊)

## 完整代码

```python
import asyncio
from yunbot import OneBotClient, Message, MessageSegment

async def main():
    # 创建客户端
    client = OneBotClient.create_simple_client(
        connection_type="websocket",
        url="ws://localhost:3001",     # WebSocket 服务器地址
        access_token="your_token"       # 访问令牌 (如果需要)
    )
    
    # 注册消息事件处理器
    @client.on_message
    async def handle_message(event):
        """处理所有消息事件"""
        # 提取消息内容
        msg = Message(event.message)
        text = msg.extract_plain_text()
        
        print(f"收到消息: {text}")
        
        # 构建回复消息
        reply = Message([
            MessageSegment.text("你好!我收到了你的消息:\n"),
            MessageSegment.text(f"「{text}」\n\n"),
            MessageSegment.text("这是一个基础的回复示例"),
            MessageSegment.face(178)  # 添加表情
        ])
        
        # 根据消息来源发送回复
        if hasattr(event, 'group_id'):
            # 群消息
            await client.send_group_msg(event.group_id, reply)
        else:
            # 私聊消息
            await client.send_private_msg(event.user_id, reply)
    
    # 启动客户端
    await client.start()
    print("机器人已启动!")
    
    # 持续运行
    await client.run_forever()

if __name__ == "__main__":
    asyncio.run(main())
```

## 代码解析

### 1. 创建客户端

```python
client = OneBotClient.create_simple_client(
    connection_type="websocket",
    url="ws://localhost:3001",
    access_token="your_token"
)
```

- `connection_type`: 连接类型,当前支持 "websocket"
- `url`: WebSocket 服务器地址
- `access_token`: 访问令牌,用于身份验证 (可选)

### 2. 注册消息处理器

```python
@client.on_message
async def handle_message(event):
    # 处理消息
    pass
```

使用装饰器注册消息事件处理器,当收到消息时自动调用。

### 3. 提取消息内容

```python
msg = Message(event.message)
text = msg.extract_plain_text()
```

将事件中的消息转换为 Message 对象,然后提取纯文本内容。

### 4. 构建回复消息

```python
reply = Message([
    MessageSegment.text("文本内容"),
    MessageSegment.face(178)
])
```

使用 MessageSegment 构建包含多种元素的消息。

### 5. 发送消息

```python
if hasattr(event, 'group_id'):
    await client.send_group_msg(event.group_id, reply)
else:
    await client.send_private_msg(event.user_id, reply)
```

根据消息来源 (群聊或私聊) 选择合适的发送方法。

## 运行方法

### 1. 准备环境

```bash
# 安装 YunBot
pip install yunbot

# 或从源码安装
git clone https://github.com/YunBot/onebot-adapter-client.git
cd onebot-adapter-client
pip install -r requirements.txt
```

### 2. 配置 OneBot 服务

确保你有一个运行中的 OneBot v11 服务,如 go-cqhttp、shamrock 等。

### 3. 修改配置

修改代码中的连接参数:
```python
url="ws://localhost:3001",  # 改为你的服务地址
access_token="your_token"    # 改为你的访问令牌
```

### 4. 运行机器人

```bash
python basic_bot.py
```

## 运行效果

当机器人启动后:

**用户发送**: 你好

**机器人回复**:
```
你好!我收到了你的消息:
「你好」

这是一个基础的回复示例 😊
```

## 扩展建议

### 1. 添加欢迎消息

```python
@client.on_notice
async def handle_notice(event):
    if event.notice_type == "group_increase":
        welcome_msg = MessageSegment.at(event.user_id) + MessageSegment.text(" 欢迎加入!")
        await client.send_group_msg(event.group_id, welcome_msg)
```

### 2. 添加简单命令

```python
@client.on_message
async def handle_message(event):
    msg = Message(event.message)
    text = msg.extract_plain_text().strip()
    
    if text == "/help":
        help_msg = "可用命令:\n/help - 显示帮助\n/ping - 测试响应"
        await send_reply(event, help_msg)
    elif text == "/ping":
        await send_reply(event, "Pong!")
    else:
        await send_reply(event, f"收到: {text}")

async def send_reply(event, message):
    if hasattr(event, 'group_id'):
        await client.send_group_msg(event.group_id, message)
    else:
        await client.send_private_msg(event.user_id, message)
```

### 3. 添加日志

```python
from yunbot.logger import get_logger

logger = get_logger("BasicBot").setup(
    level="INFO",
    log_to_file=True
)

@client.on_message
async def handle_message(event):
    logger.info(f"收到消息: {event.message}")
    # 处理消息...
    logger.success("消息处理完成")
```

## 相关文档

- [快速开始](../quickstart.md) - 更详细的入门教程
- [消息构建](../guide/messages.md) - 消息构建和发送
- [事件处理](../guide/events.md) - 事件处理详解
