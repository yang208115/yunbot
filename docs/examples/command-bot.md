# 命令处理机器人示例

## 功能说明

这个示例展示如何构建一个支持多种命令的机器人:
- 命令解析和参数提取
- 多命令处理
- 权限控制
- 错误处理

支持的命令:
- `/help` - 显示帮助信息
- `/echo <内容>` - 回显消息
- `/time` - 显示当前时间
- `/ping` - 测试响应
- `/info` - 显示机器人信息

## 完整代码

```python
import asyncio
import datetime
from yunbot import OneBotClient, Message, MessageSegment
from yunbot.logger import get_logger

# 创建日志器
logger = get_logger("CommandBot").setup(level="INFO")

# 命令前缀
CMD_PREFIX = "/"

async def main():
    client = OneBotClient.create_simple_client(
        connection_type="websocket",
        url="ws://localhost:3001",
        access_token="your_token"
    )
    
    @client.on_message
    async def handle_message(event):
        """处理消息事件"""
        try:
            # 提取消息文本
            msg = Message(event.message)
            text = msg.extract_plain_text().strip()
            
            # 检查是否是命令
            if not text.startswith(CMD_PREFIX):
                return
            
            # 解析命令
            parts = text[1:].split(maxsplit=1)
            command = parts[0].lower()
            args = parts[1] if len(parts) > 1 else ""
            
            logger.info(f"收到命令: {command}, 参数: {args}")
            
            # 路由命令
            if command == "help":
                await cmd_help(client, event)
            elif command == "echo":
                await cmd_echo(client, event, args)
            elif command == "time":
                await cmd_time(client, event)
            elif command == "ping":
                await cmd_ping(client, event)
            elif command == "info":
                await cmd_info(client, event)
            else:
                await send_reply(client, event, f"未知命令: {command}\n使用 /help 查看帮助")
                
        except Exception as e:
            logger.error(f"命令处理失败: {e}")
            await send_reply(client, event, "命令执行失败,请稍后重试")
    
    await client.start()
    logger.info("命令机器人已启动")
    await client.run_forever()

# ========== 命令处理函数 ==========

async def cmd_help(client, event):
    """显示帮助信息"""
    help_text = """📖 命令帮助

基础命令:
/help - 显示此帮助信息
/ping - 测试响应
/time - 显示当前时间
/info - 显示机器人信息

实用命令:
/echo <内容> - 回显消息

💡 使用示例: /echo 你好世界"""
    
    await send_reply(client, event, help_text)

async def cmd_echo(client, event, args):
    """回显命令"""
    if not args:
        await send_reply(client, event, "❌ 用法: /echo <内容>")
        return
    
    reply = Message([
        MessageSegment.text("🔁 回显:\n"),
        MessageSegment.text(args)
    ])
    await send_reply(client, event, reply)

async def cmd_time(client, event):
    """显示当前时间"""
    now = datetime.datetime.now()
    time_str = now.strftime("%Y年%m月%d日 %H:%M:%S")
    
    reply = f"⏰ 当前时间: {time_str}"
    await send_reply(client, event, reply)

async def cmd_ping(client, event):
    """测试响应"""
    reply = "🏓 Pong! 机器人运行正常"
    await send_reply(client, event, reply)

async def cmd_info(client, event):
    """显示机器人信息"""
    try:
        login_info = await client.get_login_info()
        status = await client.get_status()
        
        info_text = f"""🤖 机器人信息

ID: {login_info.get('user_id', '未知')}
昵称: {login_info.get('nickname', '未知')}
在线状态: {'在线' if status.get('online') else '离线'}
运行状态: {'良好' if status.get('good') else '异常'}"""
        
        await send_reply(client, event, info_text)
    except Exception as e:
        logger.error(f"获取机器人信息失败: {e}")
        await send_reply(client, event, "❌ 获取信息失败")

# ========== 工具函数 ==========

async def send_reply(client, event, message):
    """统一的消息发送函数"""
    try:
        if hasattr(event, 'group_id'):
            await client.send_group_msg(event.group_id, message)
        else:
            await client.send_private_msg(event.user_id, message)
    except Exception as e:
        logger.error(f"发送消息失败: {e}")

if __name__ == "__main__":
    asyncio.run(main())
```

## 代码解析

### 1. 命令解析

```python
# 解析命令和参数
parts = text[1:].split(maxsplit=1)
command = parts[0].lower()
args = parts[1] if len(parts) > 1 else ""
```

- 去掉命令前缀 `/`
- 按空格分割,第一部分是命令,其余是参数
- 转换为小写以支持大小写不敏感

### 2. 命令路由

```python
if command == "help":
    await cmd_help(client, event)
elif command == "echo":
    await cmd_echo(client, event, args)
# ...
```

根据命令名称调用对应的处理函数。

### 3. 参数验证

```python
async def cmd_echo(client, event, args):
    if not args:
        await send_reply(client, event, "用法: /echo <内容>")
        return
    # 处理命令...
```

检查必需参数是否存在。

### 4. 错误处理

```python
try:
    # 命令处理
    pass
except Exception as e:
    logger.error(f"命令处理失败: {e}")
    await send_reply(client, event, "命令执行失败")
```

捕获异常并返回友好的错误信息。

## 运行和测试

### 1. 启动机器人

```bash
python command_bot.py
```

### 2. 测试命令

在 QQ 中发送:

- `/help` - 查看帮助
- `/ping` - 测试响应
- `/time` - 查看时间
- `/echo 你好世界` - 回显消息
- `/info` - 查看机器人信息

## 扩展功能

### 1. 添加权限控制

```python
# 管理员列表
ADMIN_IDS = {123456789, 987654321}

def is_admin(user_id):
    """检查是否是管理员"""
    return user_id in ADMIN_IDS

@client.on_message
async def handle_message(event):
    # ...
    if command == "admin":
        if not is_admin(event.user_id):
            await send_reply(client, event, "❌ 权限不足")
            return
        await cmd_admin(client, event, args)
```

### 2. 添加命令冷却

```python
import time

# 用户最后使用命令的时间
last_use = {}

def check_cooldown(user_id, seconds=5):
    """检查冷却时间"""
    now = time.time()
    if user_id in last_use:
        if now - last_use[user_id] < seconds:
            return False
    last_use[user_id] = now
    return True

@client.on_message
async def handle_message(event):
    if not check_cooldown(event.user_id):
        await send_reply(client, event, "❌ 命令使用过于频繁,请稍后再试")
        return
    # 处理命令...
```

### 3. 使用事件匹配器

```python
from yunbot.matcher import on_command

# 使用匹配器注册命令
help_cmd = on_command("help")

@help_cmd
async def handle_help(event):
    await cmd_help(client, event)

echo_cmd = on_command("echo")

@echo_cmd
async def handle_echo(event):
    msg = Message(event.message)
    text = msg.extract_plain_text()
    args = text.split(maxsplit=1)[1] if len(text.split()) > 1 else ""
    await cmd_echo(client, event, args)
```

## 相关文档

- [事件匹配器](../advanced/event-matcher.md) - 使用匹配器简化命令处理
- [消息构建](../guide/messages.md) - 消息构建和发送
- [错误处理](../advanced/error-handling.md) - 异常处理最佳实践
