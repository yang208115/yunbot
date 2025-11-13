"""OneBot v11 客户端适配器

这是一个用于 OneBot v11 协议的 Python 客户端库，提供多种连接方式和丰富的功能。

## 主要功能

- 支持多种连接方式：HTTP、WebSocket、反向 WebSocket、Webhook
- 完整的 OneBot v11 API 支持
- 事件处理系统
- 消息构建和解析
- 自动重连和错误处理
- 详细的日志记录

## 快速开始

```python
from onebot_adapter_client import OneBotClient, MessageSegment

# 创建客户端
client = OneBotClient.create_simple_client(
    connection_type="http",
    base_url="http://localhost:5700",
    access_token="your_token",
    self_id="123456789"
)

# 注册消息处理器
@client.on_message
async def handle_message(event):
    print(f"收到消息: {event.message}")
    
    # 回复消息
    if hasattr(event, 'user_id'):
        await client.send_private_msg(
            user_id=event.user_id,
            message=f"回复: {event.message}"
        )

# 启动客户端
async def main():
    await client.start()
    await client.run_forever()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

## 连接方式

- HTTP: `connection_type="http"`
- WebSocket: `connection_type="ws"`
- 反向 WebSocket: `connection_type="reverse_ws"`
- Webhook: `connection_type="webhook"`

## 详细文档

更多详细信息，请参考项目文档和示例代码。
"""

from .adapter import OneBotAdapter
from .bot import OneBotBot
from .client import OneBotClient
from .config import Config
from .event import Event, MessageEvent, NoticeEvent, RequestEvent, MetaEvent
from .exceptions import (
    OneBotException,
    NetworkException,
    ActionFailed,
    ApiNotAvailable,
    RateLimitError,
    PermissionError,
    RetryableError,
    ResourceNotFound,
    ServerError,
    TimeoutException,
    AuthenticationFailed,
    ConnectionClosed,
    InvalidEvent,
    ConfigurationError,
)
from .matcher import (
    on,
    on_message,
    on_notice,
    on_request,
    on_metaevent,
    on_startswith,
    on_endswith,
    on_fullmatch,
    on_keyword,
    on_command,
    on_regex,
    startswith,
    endswith,
    fullmatch,
    keyword,
    command,
    regex,
)
from .logger import YunBotLogger, get_logger, setup_logging, default_logger
from .message import Message, MessageSegment, MessageBuilder
from .utils import logger

__all__ = [
    "OneBotAdapter",
    "OneBotBot", 
    "OneBotClient",
    "Config",
    "Event",
    "MessageEvent",
    "NoticeEvent", 
    "RequestEvent",
    "MetaEvent",
    "OneBotException",
    "NetworkException",
    "ActionFailed",
    "ApiNotAvailable",
    "RateLimitError",
    "PermissionError",
    "RetryableError",
    "ResourceNotFound",
    "ServerError",
    "TimeoutException",
    "AuthenticationFailed",
    "ConnectionClosed",
    "InvalidEvent",
    "ConfigurationError",
    "Message",
    "MessageSegment",
    "MessageBuilder",
    "on",
    "on_message",
    "on_notice",
    "on_request",
    "on_metaevent",
    "on_startswith",
    "on_endswith",
    "on_fullmatch",
    "on_keyword",
    "on_command",
    "on_regex",
    "startswith",
    "endswith",
    "fullmatch",
    "keyword",
    "command",
    "regex",
    "YunBotLogger",
    "get_logger",
    "setup_logging",
    "default_logger",
    "logger",
]

try:
    from ._version import version as __version__
except ImportError:
    __version__ = "unknown"

__author__ = "yang208115"
__email__ = "yang208115@lyuy.top"
__license__ = "MIT"
__copyright__ = "Copyright 2025 yang208115"