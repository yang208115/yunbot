# 群管理机器人示例

## 功能说明

这个示例展示如何构建一个功能完整的群管理机器人:
- 新成员欢迎
- 关键词检测和警告
- 违规成员处理 (禁言/踢出)
- 管理员命令
- 自动审批加群请求

## 完整代码

```python
import asyncio
from yunbot import OneBotClient, Message, MessageSegment
from yunbot.logger import get_logger

logger = get_logger("GroupManager").setup(level="INFO", log_to_file=True)

# ========== 配置 ==========

# 管理员 QQ 号列表
ADMIN_IDS = {123456789, 987654321}

# 违禁词列表
BANNED_WORDS = {"广告", "刷屏", "违规词"}

# 警告记录 {user_id: warning_count}
warnings = {}

async def main():
    client = OneBotClient.create_simple_client(
        connection_type="websocket",
        url="ws://localhost:3001",
        access_token="your_token"
    )
    
    # ========== 消息事件 ==========
    
    @client.on_message
    async def handle_message(event):
        """处理群消息"""
        # 只处理群消息
        if not hasattr(event, 'group_id'):
            return
        
        msg = Message(event.message)
        text = msg.extract_plain_text().strip()
        
        # 检查违禁词
        await check_banned_words(client, event, text)
        
        # 处理管理员命令
        if text.startswith("/") and event.user_id in ADMIN_IDS:
            await handle_admin_command(client, event, text)
    
    # ========== 通知事件 ==========
    
    @client.on_notice
    async def handle_notice(event):
        """处理群通知"""
        # 新成员加入
        if event.notice_type == "group_increase":
            await welcome_new_member(client, event)
        
        # 成员离开
        elif event.notice_type == "group_decrease":
            logger.info(f"成员 {event.user_id} 离开了群 {event.group_id}")
    
    # ========== 请求事件 ==========
    
    @client.on_request
    async def handle_request(event):
        """处理加群请求"""
        if event.request_type == "group":
            await handle_group_request(client, event)
    
    await client.start()
    logger.info("群管理机器人已启动")
    await client.run_forever()

# ========== 功能函数 ==========

async def welcome_new_member(client, event):
    """欢迎新成员"""
    try:
        # 获取新成员信息
        member_info = await client.get_group_member_info(
            group_id=event.group_id,
            user_id=event.user_id
        )
        
        nickname = member_info.get('nickname', '新朋友')
        
        # 发送欢迎消息
        welcome_msg = Message([
            MessageSegment.text("🎉 欢迎 "),
            MessageSegment.at(event.user_id),
            MessageSegment.text(f" ({nickname}) 加入本群!\n\n"),
            MessageSegment.text("📖 请遵守群规,文明发言\n"),
            MessageSegment.text("💡 输入 /help 查看群功能")
        ])
        
        await client.send_group_msg(event.group_id, welcome_msg)
        logger.info(f"欢迎新成员 {nickname} ({event.user_id})")
        
    except Exception as e:
        logger.error(f"发送欢迎消息失败: {e}")

async def check_banned_words(client, event, text):
    """检查违禁词"""
    for word in BANNED_WORDS:
        if word in text:
            logger.warning(f"检测到违禁词: {word}, 用户: {event.user_id}")
            
            # 增加警告次数
            user_id = event.user_id
            warnings[user_id] = warnings.get(user_id, 0) + 1
            
            # 撤回消息
            try:
                await client.delete_msg(message_id=event.message_id)
            except:
                pass
            
            # 根据警告次数处理
            if warnings[user_id] >= 3:
                # 第3次警告: 禁言 10 分钟
                await client.set_group_ban(
                    group_id=event.group_id,
                    user_id=user_id,
                    duration=600
                )
                warning_msg = f"⚠️ 用户 {user_id} 因多次违规已被禁言 10 分钟"
                warnings[user_id] = 0  # 重置警告
            elif warnings[user_id] == 2:
                warning_msg = f"⚠️ 警告: 请勿发送违禁内容! (第2次警告,再次违规将被禁言)"
            else:
                warning_msg = f"⚠️ 警告: 请勿发送违禁内容! (第1次警告)"
            
            await client.send_group_msg(event.group_id, warning_msg)
            break

async def handle_admin_command(client, event, text):
    """处理管理员命令"""
    parts = text[1:].split()
    command = parts[0].lower() if parts else ""
    
    try:
        if command == "ban":
            # /ban @用户 [时长(分钟)]
            if len(event.message) < 2:
                await client.send_group_msg(event.group_id, "用法: /ban @用户 [时长(分钟)]")
                return
            
            msg = Message(event.message)
            at_segments = msg.get_segments("at")
            if not at_segments:
                await client.send_group_msg(event.group_id, "请@要禁言的用户")
                return
            
            target_id = int(at_segments[0].data['qq'])
            duration = int(parts[1]) * 60 if len(parts) > 1 else 600  # 默认 10 分钟
            
            await client.set_group_ban(
                group_id=event.group_id,
                user_id=target_id,
                duration=duration
            )
            
            await client.send_group_msg(
                event.group_id,
                f"✅ 已禁言用户 {target_id}, 时长: {duration//60} 分钟"
            )
            logger.info(f"管理员 {event.user_id} 禁言了用户 {target_id}")
        
        elif command == "unban":
            # /unban @用户
            msg = Message(event.message)
            at_segments = msg.get_segments("at")
            if not at_segments:
                await client.send_group_msg(event.group_id, "请@要解除禁言的用户")
                return
            
            target_id = int(at_segments[0].data['qq'])
            
            await client.set_group_ban(
                group_id=event.group_id,
                user_id=target_id,
                duration=0
            )
            
            await client.send_group_msg(event.group_id, f"✅ 已解除用户 {target_id} 的禁言")
            logger.info(f"管理员 {event.user_id} 解除了用户 {target_id} 的禁言")
        
        elif command == "kick":
            # /kick @用户
            msg = Message(event.message)
            at_segments = msg.get_segments("at")
            if not at_segments:
                await client.send_group_msg(event.group_id, "请@要踢出的用户")
                return
            
            target_id = int(at_segments[0].data['qq'])
            
            await client.set_group_kick(
                group_id=event.group_id,
                user_id=target_id
            )
            
            await client.send_group_msg(event.group_id, f"✅ 已踢出用户 {target_id}")
            logger.info(f"管理员 {event.user_id} 踢出了用户 {target_id}")
        
        elif command == "mute":
            # /mute - 全员禁言
            await client.set_group_whole_ban(event.group_id, enable=True)
            await client.send_group_msg(event.group_id, "✅ 已开启全员禁言")
            logger.info(f"管理员 {event.user_id} 开启了全员禁言")
        
        elif command == "unmute":
            # /unmute - 解除全员禁言
            await client.set_group_whole_ban(event.group_id, enable=False)
            await client.send_group_msg(event.group_id, "✅ 已解除全员禁言")
            logger.info(f"管理员 {event.user_id} 解除了全员禁言")
    
    except Exception as e:
        logger.error(f"执行管理员命令失败: {e}")
        await client.send_group_msg(event.group_id, f"❌ 命令执行失败: {e}")

async def handle_group_request(client, event):
    """处理加群请求"""
    try:
        # 这里可以添加审批逻辑,比如检查用户信息等
        # 简单示例: 自动同意所有请求
        await client.set_group_add_request(
            flag=event.flag,
            sub_type=event.sub_type,
            approve=True
        )
        
        logger.info(f"自动同意用户 {event.user_id} 的加群请求")
    except Exception as e:
        logger.error(f"处理加群请求失败: {e}")

if __name__ == "__main__":
    asyncio.run(main())
```

## 功能模块解析

### 1. 新成员欢迎

```python
async def welcome_new_member(client, event):
    # 获取成员信息
    member_info = await client.get_group_member_info(
        group_id=event.group_id,
        user_id=event.user_id
    )
    
    # 发送欢迎消息
    welcome_msg = Message([
        MessageSegment.text("欢迎 "),
        MessageSegment.at(event.user_id),
        MessageSegment.text(" 加入本群!")
    ])
    await client.send_group_msg(event.group_id, welcome_msg)
```

### 2. 违禁词检测

```python
async def check_banned_words(client, event, text):
    for word in BANNED_WORDS:
        if word in text:
            # 撤回消息
            await client.delete_msg(message_id=event.message_id)
            
            # 记录警告
            warnings[event.user_id] = warnings.get(event.user_id, 0) + 1
            
            # 达到阈值禁言
            if warnings[event.user_id] >= 3:
                await client.set_group_ban(
                    group_id=event.group_id,
                    user_id=event.user_id,
                    duration=600
                )
```

### 3. 管理员命令

支持的命令:
- `/ban @用户 [分钟]` - 禁言用户
- `/unban @用户` - 解除禁言
- `/kick @用户` - 踢出用户
- `/mute` - 全员禁言
- `/unmute` - 解除全员禁言

### 4. 自动审批

```python
async def handle_group_request(client, event):
    await client.set_group_add_request(
        flag=event.flag,
        sub_type=event.sub_type,
        approve=True  # 自动同意
    )
```

## 配置和部署

### 1. 修改配置

```python
# 设置管理员
ADMIN_IDS = {123456789, 987654321}  # 改为实际管理员 QQ 号

# 设置违禁词
BANNED_WORDS = {"广告", "刷屏", "违规词"}

# 设置连接信息
url="ws://localhost:3001",
access_token="your_token"
```

### 2. 运行机器人

```bash
python group_manager.py
```

### 3. 测试功能

1. 邀请机器人加入测试群
2. 测试新成员欢迎: 邀请新成员入群
3. 测试违禁词: 发送包含违禁词的消息
4. 测试管理命令: 使用 `/ban @用户` 等命令

## 扩展功能

### 1. 自定义审批规则

```python
async def handle_group_request(client, event):
    # 获取用户信息
    user_info = await client.get_stranger_info(user_id=event.user_id)
    
    # 检查条件 (例如: QQ 等级)
    if user_info.get('level', 0) < 10:
        # 拒绝
        await client.set_group_add_request(
            flag=event.flag,
            sub_type=event.sub_type,
            approve=False,
            reason="QQ 等级过低"
        )
    else:
        # 同意
        await client.set_group_add_request(
            flag=event.flag,
            sub_type=event.sub_type,
            approve=True
        )
```

### 2. 积分系统

```python
# 用户积分
points = {}

@client.on_message
async def handle_message(event):
    if not hasattr(event, 'group_id'):
        return
    
    # 签到命令
    msg = Message(event.message)
    text = msg.extract_plain_text().strip()
    
    if text == "/签到":
        user_id = event.user_id
        points[user_id] = points.get(user_id, 0) + 10
        
        await client.send_group_msg(
            event.group_id,
            f"✅ 签到成功! 当前积分: {points[user_id]}"
        )
```

## 相关文档

- [群组管理 API](../api/group.md) - 群组管理 API 详解
- [事件处理](../guide/events.md) - 事件处理机制
- [错误处理](../advanced/error-handling.md) - 异常处理
