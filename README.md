# YunBot - OneBot v11 客户端

[![Python](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

YunBot 是一个简洁易用的 OneBot v11 协议 Python 客户端库。提供完整的 API 支持、多种连接方式、强大的事件处理系统和自动重连机制。

## 核心特性

- ✨ **多种连接方式**:WebSocket、HTTP、反向 WebSocket、Webhook
- 📡 **完整 API 支持**:消息发送、群组管理、信息获取等 OneBot v11 标准接口
- 🎯 **强大事件系统**:消息、通知、请求、元事件等完整事件类型支持
- 💬 **灵活消息构建**:支持文本、图片、语音、视频、@、转发等多种消息段
- 🔄 **自动重连机制**:连接稳定性保证,完善的异常处理
- ⚙️ **配置验证**:基于 Pydantic 的强类型配置验证和管理
- 📝 **配置文件支持**:支持从 JSON/YAML 文件加载配置,环境变量覆盖
- 🔗 **链式消息构建**:MessageBuilder 提供便捷的链式 API
- 🎲 **规则组合**:事件匹配器支持 AND/OR 逻辑组合

## 快速开始

### 安装

```bash
# 从源码安装
git clone https://github.com/yang208115/YunBot.git
cd YunBot
pip install -r requirements.txt
```

### 基本使用

#### 方式 1:直接创建客户端

```python
import asyncio
from yunbot import OneBotClient, MessageSegment

async def main():
    # 创建 WebSocket 客户端
    client = OneBotClient.create_simple_client(
        connection_type="websocket",
        url="ws://localhost:3001",
        access_token="your_token"
    )

    # 注册消息事件处理器
    @client.on_message
    async def handle_message(event):
        print(f"收到消息: {event.message}")
        if hasattr(event, 'group_id'):
            await client.send_group_msg(
                group_id=event.group_id,
                message="收到消息!"
            )
        else:
            await client.send_private_msg(
                user_id=event.user_id,
                message="收到消息!"
            )

    # 启动客户端
    await client.start()
    await client.run_forever()

if __name__ == "__main__":
    asyncio.run(main())
```

#### 方式 2:从配置文件加载

```python
import asyncio
from yunbot import OneBotClient, Config

async def main():
    # 从 JSON 或 YAML 文件加载配置
    config = Config.from_file("config.yaml")
    client = OneBotClient(config=config)
    
    @client.on_message
    async def handle_message(event):
        print(f"收到消息: {event.message}")
    
    await client.start()
    await client.run_forever()

if __name__ == "__main__":
    asyncio.run(main())
```

配置文件示例 (`config.yaml`):

```yaml
connections:
  - type: websocket
    url: ws://127.0.0.1:6700
    access_token: your_token_here
    heartbeat_interval: 30.0

api_timeout: 30.0
max_concurrent_requests: 100
enable_heartbeat: true
```

#### 方式 3:使用 MessageBuilder 构建消息

```python
from yunbot import MessageBuilder

# 链式构建复杂消息
msg = (MessageBuilder()
    .text("你好!")
    .at(123456)
    .text(" ")
    .image("http://example.com/pic.jpg")
    .build())

await client.send_group_msg(group_id=123456, message=msg)
```

## 核心模块

| 模块 | 功能 |
|------|------|
| `client.py` | 高级客户端接口,简化配置和事件处理 |
| `adapter.py` | 适配器核心,管理连接和事件分发 |
| `bot.py` | Bot 实例,封装 OneBot v11 API 调用 |
| `config.py` | 配置管理,支持 JSON/YAML 文件加载 |
| `connection.py` | WebSocket 连接,消息收发和心跳 |
| `event.py` | 事件模型,定义所有事件类型 |
| `message.py` | 消息模型,消息段构建和 MessageBuilder |
| `matcher.py` | 事件匹配器,支持规则组合 |
| `exceptions.py` | 异常定义,细粒度错误处理 |
| `logger.py` | 日志系统,彩色输出和文件轮转 |
| `store.py` | 数据存储,API 响应管理 |
| `utils.py` | 工具函数,性能监控和装饰器 |

## 开发规范

- 所有代码注释必须使用中文
- 遵循 Google-Style Docstring 规范
- 使用异步编程模式（async/await）
- 遵循 PEP 8 代码规范
- 使用类型注解提高代码可读性
- 基于 Pydantic 进行配置验证

## 贡献指南

欢迎提交 Pull Request 和 Issue！请遵循以下规范：

```bash
# 开发环境搭建
git clone https://github.com/yang208115/YunBot.git
cd YunBot
pip install -r requirements.txt

# 运行测试
pytest tests/
```

### 提交规范

- `feat`: 新功能
- `fix`: 修复 bug
- `docs`: 文档更新
- `refactor`: 代码重构

## 许可证

MIT License © 2025 Yang208115