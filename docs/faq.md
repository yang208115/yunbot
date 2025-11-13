# 常见问题 (FAQ)

本文档收集了 YunBot 使用过程中的常见问题和解决方案。

## 安装和环境

### Q: 支持哪些 Python 版本?

**A**: YunBot 支持 Python 3.7 及以上版本。推荐使用 Python 3.8+。

```bash
python --version  # 检查 Python 版本
```

### Q: 如何安装 YunBot?

**A**: 从源码安装:

```bash
git clone https://github.com/yang208115/YunBot.git
cd yunbot
pip install -r requirements.txt
```

### Q: 安装时遇到依赖问题怎么办?

**A**: 尝试升级 pip 并重新安装:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

如果仍有问题,安装指定版本的依赖:

```bash
pip install aiohttp==3.8.0 pydantic==2.0.0
```

## 连接和配置

### Q: 如何连接到 OneBot 服务器?

**A**: 使用 `create_simple_client` 方法:

```python
from yunbot import OneBotClient

client = OneBotClient.create_simple_client(
    connection_type="websocket",
    url="ws://localhost:3001",  # 修改为你的服务器地址
    access_token="your_token"    # 如果需要
)
```

### Q: WebSocket 连接失败怎么办?

**A**: 检查以下几点:

1. **服务器地址**: 确认 URL 正确,格式为 `ws://host:port` 或 `wss://host:port`
2. **服务器运行**: 确认 OneBot 服务 (如 go-cqhttp) 正在运行
3. **端口占用**: 检查端口是否被占用或被防火墙阻止
4. **访问令牌**: 如果服务器设置了 access_token,确保配置正确

```python
# 查看详细错误信息
from yunbot.logger import get_logger

logger = get_logger("YunBot").setup(level="DEBUG")
await client.start()  # 错误信息会输出到日志
```

### Q: 如何设置心跳间隔?

**A**: 在创建客户端时配置:

```python
client = OneBotClient.create_simple_client(
    connection_type="websocket",
    url="ws://localhost:3001",
    heartbeat_interval=30.0  # 30 秒心跳
)
```

### Q: 如何使用配置文件?

**A**: 创建 YAML 或 JSON 配置文件:

```yaml
# config.yaml
connections:
  - type: websocket
    url: ws://localhost:3001
    access_token: your_token
```

然后加载:

```python
client = OneBotClient.from_config_file("config.yaml")
```

## 消息发送

### Q: 如何发送私聊消息?

**A**: 使用 `send_private_msg`:

```python
await client.send_private_msg(
    user_id=123456789,
    message="你好"
)
```

### Q: 如何发送群消息?

**A**: 使用 `send_group_msg`:

```python
await client.send_group_msg(
    group_id=987654321,
    message="大家好"
)
```

### Q: 如何发送图片?

**A**: 使用 MessageSegment.image:

```python
from yunbot import MessageSegment

await client.send_private_msg(
    user_id=123456789,
    message=[
        MessageSegment.text("这是一张图片:"),
        MessageSegment.image(file="https://example.com/image.jpg")
    ]
)
```

### Q: 如何@某人?

**A**: 使用 MessageSegment.at:

```python
await client.send_group_msg(
    group_id=987654321,
    message=[
        MessageSegment.at(123456789),
        MessageSegment.text(" 你好!")
    ]
)
```

### Q: 消息发送失败怎么办?

**A**: 捕获异常并查看错误信息:

```python
from yunbot.exceptions import ActionFailed

try:
    await client.send_private_msg(user_id=123, message="test")
except ActionFailed as e:
    print(f"发送失败: {e}")
    print(f"返回码: {e.retcode}")
    print(f"详情: {e.data}")
```

常见原因:
- 用户不存在或未添加好友
- 群号不存在或机器人不在群中
- 消息内容违规
- 被限流

## 事件处理

### Q: 如何接收消息?

**A**: 注册消息处理器:

```python
@client.on_message
async def handle_message(event):
    print(f"收到消息: {event.message}")
```

### Q: 如何区分私聊和群聊消息?

**A**: 检查事件是否有 `group_id` 属性:

```python
@client.on_message
async def handle_message(event):
    if hasattr(event, 'group_id'):
        print("群消息")
    else:
        print("私聊消息")
```

### Q: 如何提取消息文本内容?

**A**: 使用 Message 对象:

```python
from yunbot import Message

@client.on_message
async def handle_message(event):
    msg = Message(event.message)
    text = msg.extract_plain_text()
    print(f"文本内容: {text}")
```

### Q: 如何处理新成员加群事件?

**A**: 注册通知处理器:

```python
@client.on_notice
async def handle_notice(event):
    if event.notice_type == "group_increase":
        await client.send_group_msg(
            event.group_id,
            f"欢迎新成员 {event.user_id}!"
        )
```

## 错误和调试

### Q: 如何启用调试日志?

**A**: 设置日志级别为 DEBUG:

```python
from yunbot.logger import get_logger

logger = get_logger("YunBot").setup(
    level="DEBUG",
    log_to_file=True,
    log_dir="logs"
)
```

### Q: 程序崩溃怎么办?

**A**: 
1. 查看日志文件找出错误原因
2. 添加异常处理:

```python
try:
    await client.start()
    await client.run_forever()
except Exception as e:
    logger.exception(f"程序崩溃: {e}")
```

3. 实现自动重连:

```python
while True:
    try:
        await client.start()
        await client.run_forever()
    except Exception as e:
        logger.error(f"错误: {e}, 5秒后重试")
        await asyncio.sleep(5)
```

### Q: API 调用超时怎么办?

**A**: 增加超时时间:

```python
from yunbot.config import Config, WebSocketConfig

config = Config(
    connections=[WebSocketConfig(url="ws://localhost:3001", timeout=60.0)],
    api_timeout=60.0
)
```

### Q: 如何查看 Bot 的 ID?

**A**: 获取登录信息:

```python
login_info = await client.get_login_info()
print(f"Bot ID: {login_info['user_id']}")
```

## 高级功能

### Q: 如何使用事件匹配器?

**A**: 导入并使用匹配器:

```python
from yunbot.matcher import on_command

help_cmd = on_command("help")

@help_cmd
async def handle_help(event):
    await client.send_private_msg(event.user_id, "帮助信息")
```

### Q: 如何限制命令调用频率?

**A**: 实现冷却机制:

```python
import time

last_use = {}

def check_cooldown(user_id, seconds=5):
    now = time.time()
    if user_id in last_use and now - last_use[user_id] < seconds:
        return False
    last_use[user_id] = now
    return True
```

### Q: 如何实现权限控制?

**A**: 维护管理员列表:

```python
ADMIN_IDS = {123456789, 987654321}

@client.on_message
async def handle_message(event):
    if event.user_id not in ADMIN_IDS:
        await client.send_private_msg(event.user_id, "权限不足")
        return
    # 执行管理员操作...
```

### Q: 如何管理多个机器人实例?

**A**: 配置多个连接:

```python
from yunbot.config import Config, WebSocketConfig

config = Config(
    connections=[
        WebSocketConfig(url="ws://localhost:3001"),
        WebSocketConfig(url="ws://localhost:3002"),
    ]
)

client = OneBotClient(config)
bots = client.get_bots()  # 获取所有 Bot 实例
```

## 性能和优化

### Q: 如何提高消息处理速度?

**A**: 
1. 使用异步操作
2. 避免阻塞操作
3. 合理使用并发限制

```python
# ✅ 好的做法
@client.on_message
async def handle_message(event):
    await process_async(event)

# ❌ 避免
@client.on_message
async def handle_message(event):
    time.sleep(5)  # 阻塞操作
```

### Q: 如何避免被限流?

**A**: 
1. 添加发送延迟
2. 限制并发请求数
3. 使用批量操作

```python
# 批量发送时添加延迟
for user_id in user_list:
    await client.send_private_msg(user_id, message)
    await asyncio.sleep(1)  # 延迟 1 秒
```

## 部署和运维

### Q: 如何在后台运行?

**A**: Linux 使用 nohup 或 systemd:

```bash
# nohup
nohup python bot.py > bot.log 2>&1 &

# 或使用 screen
screen -S bot
python bot.py
# Ctrl+A+D 分离
```

### Q: 如何设置开机自启?

**A**: 创建 systemd 服务 (Linux):

```ini
# /etc/systemd/system/yunbot.service
[Unit]
Description=YunBot Service
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/path/to/bot
ExecStart=/usr/bin/python3 /path/to/bot/bot.py
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable yunbot
sudo systemctl start yunbot
```

### Q: 如何监控机器人运行状态?

**A**: 
1. 启用文件日志
2. 定期检查日志
3. 实现健康检查

```python
from yunbot.logger import get_logger

logger = get_logger("YunBot").setup(
    level="INFO",
    log_to_file=True,
    log_dir="/var/log/yunbot"
)

# 定期输出状态
async def health_check():
    while True:
        status = await client.get_status()
        logger.info(f"健康检查: {status}")
        await asyncio.sleep(300)  # 5 分钟
```

## 获取帮助

如果以上内容无法解决你的问题:

1. **查看文档**: 阅读完整的[使用文档](index.md)
2. **查看示例**: 参考[示例代码](examples/)
3. **提交 Issue**: 在 [GitHub](https://github.com/YunBot/onebot-adapter-client/issues) 提交问题
4. **加入社区**: 加入 QQ 群交流

## 相关文档

- [快速开始](quickstart.md) - 快速上手教程
- [客户端使用](guide/client.md) - 客户端详细使用
- [API 参考](api/overview.md) - 完整 API 文档
- [错误处理](advanced/error-handling.md) - 异常处理指南
