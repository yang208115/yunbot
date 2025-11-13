# 事件匹配器

## 概述

事件匹配器(Event Matcher)是 YunBot 提供的高级事件处理机制,类似于 NoneBot2 的匹配器系统。它允许你通过装饰器方式定义更精确的事件处理规则,如匹配特定命令、关键词、正则表达式等。

## 基本概念

事件匹配器通过规则(Rule)来筛选事件,只有满足规则的事件才会触发处理器。

### 匹配器类型

| 匹配器 | 说明 | 示例 |
|--------|------|------|
| on_startswith() | 匹配消息开头 | "/help", "/命令" |
| on_endswith() | 匹配消息结尾 | "吗", "?" |
| on_fullmatch() | 完全匹配 | "你好", "签到" |
| on_keyword() | 关键词匹配 | {"帮助", "救命"} |
| on_command() | 命令匹配 | "/help", "/签到" |
| on_regex() | 正则表达式匹配 | r"\d{6,10}" |

## 使用方法

### on_startswith() - 匹配开头

匹配以指定字符串开头的消息。

```python
from yunbot.matcher import on_startswith

# 匹配以 "/help" 开头的消息
matcher = on_startswith("/help")

@matcher
async def handle_help(event):
    from yunbot import Message, MessageSegment
    help_text = "可用命令:\n/help - 显示帮助\n/status - 查看状态"
    
    # 根据消息来源回复
    if hasattr(event, 'group_id'):
        await event.bot.send_group_msg(event.group_id, help_text)
    else:
        await event.bot.send_private_msg(event.user_id, help_text)
```

**匹配多个前缀**:
```python
matcher = on_startswith(("/help", "/帮助", "帮助"))
```

### on_command() - 命令匹配

专门用于匹配命令格式的消息,自动处理 `/` 前缀。

```python
from yunbot.matcher import on_command

# 匹配 /echo 命令
echo_matcher = on_command("echo")

@echo_matcher
async def handle_echo(event):
    from yunbot import Message
    
    # 提取消息文本
    msg = Message(event.message)
    text = msg.extract_plain_text()
    
    # 提取命令参数 (去掉 "/echo " 部分)
    if text.startswith("/"):
        parts = text.split(maxsplit=1)
        content = parts[1] if len(parts) > 1 else ""
    else:
        content = ""
    
    # 回显内容
    if hasattr(event, 'group_id'):
        await event.bot.send_group_msg(event.group_id, f"回显: {content}")
    else:
        await event.bot.send_private_msg(event.user_id, f"回显: {content}")
```

**匹配多个命令**:
```python
matcher = on_command(("ping", "pong", "test"))
```

### on_keyword() - 关键词匹配

匹配包含特定关键词的消息。

```python
from yunbot.matcher import on_keyword

# 匹配包含 "帮助" 或 "救命" 的消息
help_matcher = on_keyword({"帮助", "救命", "怎么办"})

@help_matcher
async def handle_help_keyword(event):
    reply = "看起来你需要帮助,请输入 /help 查看帮助信息"
    
    if hasattr(event, 'group_id'):
        await event.bot.send_group_msg(event.group_id, reply)
    else:
        await event.bot.send_private_msg(event.user_id, reply)
```

### on_fullmatch() - 完全匹配

只匹配完全相同的消息。

```python
from yunbot.matcher import on_fullmatch

# 匹配 "你好"
greeting_matcher = on_fullmatch("你好")

@greeting_matcher
async def handle_greeting(event):
    reply = "你好!很高兴见到你!"
    
    if hasattr(event, 'group_id'):
        await event.bot.send_group_msg(event.group_id, reply)
    else:
        await event.bot.send_private_msg(event.user_id, reply)
```

**匹配多个完整消息**:
```python
matcher = on_fullmatch(("你好", "hello", "hi"))
```

### on_regex() - 正则表达式匹配

使用正则表达式匹配消息。

```python
import re
from yunbot.matcher import on_regex

# 匹配 QQ 号 (5-11 位数字)
qq_matcher = on_regex(r"\d{5,11}")

@qq_matcher
async def handle_qq_number(event):
    from yunbot import Message
    msg = Message(event.message)
    text = msg.extract_plain_text()
    
    # 提取 QQ 号
    match = re.search(r"\d{5,11}", text)
    if match:
        qq = match.group()
        reply = f"检测到 QQ 号: {qq}"
        
        if hasattr(event, 'group_id'):
            await event.bot.send_group_msg(event.group_id, reply)
        else:
            await event.bot.send_private_msg(event.user_id, reply)
```

**使用正则标志**:
```python
# 不区分大小写
matcher = on_regex(r"hello", flags=re.IGNORECASE)
```

### on_endswith() - 匹配结尾

匹配以指定字符串结尾的消息。

```python
from yunbot.matcher import on_endswith

# 匹配以 "吗" 结尾的消息
question_matcher = on_endswith("吗")

@question_matcher
async def handle_question(event):
    reply = "这是一个问题吗?我来帮你解答!"
    
    if hasattr(event, 'group_id'):
        await event.bot.send_group_msg(event.group_id, reply)
    else:
        await event.bot.send_private_msg(event.user_id, reply)
```

## 匹配器参数

所有匹配器都支持以下参数:

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| priority | int | 1 | 优先级,数字越小优先级越高 |
| block | bool | True | 是否阻止事件继续传播 |

### priority - 优先级

数字越小优先级越高,优先级高的匹配器先执行。

```python
from yunbot.matcher import on_command

# 高优先级 (priority=1, 先执行)
admin_cmd = on_command("admin", priority=1)

# 低优先级 (priority=10, 后执行)
user_cmd = on_command("user", priority=10)
```

### block - 阻止传播

设置为 True 时,匹配成功后阻止事件继续传播到其他匹配器。

```python
# 阻止传播
matcher1 = on_command("test", block=True)

@matcher1
async def handler1(event):
    print("Handler 1 执行")
    # 其他匹配器不会再处理此事件

# 不阻止传播
matcher2 = on_keyword({"test"}, block=False)

@matcher2
async def handler2(event):
    print("Handler 2 执行")
    # 其他匹配器仍会处理此事件
```

## 完整示例

### 示例 1: 命令机器人

```python
import asyncio
from yunbot import OneBotClient
from yunbot.matcher import on_command, on_keyword, on_fullmatch

async def main():
    client = OneBotClient.create_simple_client(
        connection_type="websocket",
        url="ws://localhost:3001"
    )
    
    # /help 命令
    help_cmd = on_command("help")
    
    @help_cmd
    async def handle_help(event):
        help_text = """可用命令:
/help - 显示此帮助
/ping - 测试响应
/time - 显示当前时间"""
        
        if hasattr(event, 'group_id'):
            await client.send_group_msg(event.group_id, help_text)
        else:
            await client.send_private_msg(event.user_id, help_text)
    
    # /ping 命令
    ping_cmd = on_command("ping")
    
    @ping_cmd
    async def handle_ping(event):
        if hasattr(event, 'group_id'):
            await client.send_group_msg(event.group_id, "Pong!")
        else:
            await client.send_private_msg(event.user_id, "Pong!")
    
    # /time 命令
    time_cmd = on_command("time")
    
    @time_cmd
    async def handle_time(event):
        import datetime
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if hasattr(event, 'group_id'):
            await client.send_group_msg(event.group_id, f"当前时间: {now}")
        else:
            await client.send_private_msg(event.user_id, f"当前时间: {now}")
    
    # 关键词匹配
    help_keywords = on_keyword({"帮助", "救命"})
    
    @help_keywords
    async def handle_help_keyword(event):
        reply = "需要帮助?请输入 /help 查看命令列表"
        
        if hasattr(event, 'group_id'):
            await client.send_group_msg(event.group_id, reply)
        else:
            await client.send_private_msg(event.user_id, reply)
    
    await client.start()
    await client.run_forever()

asyncio.run(main())
```

### 示例 2: 优先级和阻止传播

```python
from yunbot.matcher import on_command, on_keyword

# 高优先级,阻止传播
admin_only = on_command("admin", priority=1, block=True)

@admin_only
async def handle_admin(event):
    # 检查是否是管理员
    # 这里简化处理
    print("管理员命令")
    # 阻止其他处理器处理

# 低优先级
normal_cmd = on_command("admin", priority=10, block=False)

@normal_cmd
async def handle_normal(event):
    # 如果上面的处理器阻止了传播,这里不会执行
    print("普通用户尝试执行管理员命令")
```

## 最佳实践

### 1. 合理设置优先级

```python
# ✅ 推荐: 按重要性设置优先级
critical_cmd = on_command("stop", priority=1)     # 最高优先级
admin_cmd = on_command("admin", priority=5)       # 中等优先级
normal_cmd = on_command("help", priority=10)      # 低优先级
```

### 2. 避免过度使用阻止传播

```python
# ✅ 推荐: 只在必要时阻止传播
specific_cmd = on_command("special", block=True)  # 特殊命令,阻止传播
general_cmd = on_keyword({"hello"}, block=False)  # 通用匹配,不阻止
```

### 3. 组合使用多个匹配器

```python
# 命令匹配
on_command("help")
on_command("ping")

# 关键词匹配
on_keyword({"帮助", "救命"})

# 正则匹配
on_regex(r"\d{5,11}")  # QQ 号
```

## 注意事项

1. **匹配顺序**: 按 priority 从小到大执行
2. **阻止传播**: block=True 会阻止后续匹配器执行
3. **性能考虑**: 正则表达式匹配较慢,避免过于复杂的正则
4. **异常处理**: 匹配器中的异常不会影响其他匹配器
5. **事件对象**: 确保在处理器中访问正确的事件属性

## 相关文档

- [事件处理](../guide/events.md) - 基础事件处理
- [客户端使用](../guide/client.md) - 客户端的创建和管理
