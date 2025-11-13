"""OneBot v11 适配器的高级客户端接口。

该模块提供了一个高级客户端接口，简化了 OneBot v11 适配器的使用。
它处理配置、连接管理和事件分发。
"""

import asyncio
from typing import Any, Awaitable, Callable, Dict, List, Optional, Union
from functools import partial

from .adapter import OneBotAdapter
from .bot import OneBotBot
from .config import Config, ConnectionConfig
from .event import Event, MessageEvent
from .matcher import handle_event
from .message import Message, MessageSegment
from .exceptions import OneBotException
from .logger import default_logger as logger


class OneBotClient:
    """OneBot v11 高级客户端接口。"""
    
    def __init__(self, config: Optional[Config] = None):
        """初始化客户端。
        
        Args:
            config: 客户端的配置对象
        """
        self.config = config
        self.adapter: Optional[OneBotAdapter] = None
        self._event_handlers: Dict[str, List[Callable]] = {}
        self._running = False
    
    async def start(self, config: Optional[Config] = None) -> None:
        """启动客户端。
        
        该方法初始化适配器，注册事件处理程序，
        并启动连接进程。
        
        Args:
            config: 可选配置，用于替代 __init__ 中提供的配置
        
        Raises:
            OneBotException: 如果未提供配置则抛出
        """
        if self._running:
            logger.warning("客户端已在运行")
            return
        
        if config:
            self.config = config
        
        if not self.config:
            raise OneBotException("未提供配置")
        
        self.adapter = OneBotAdapter(self.config)

        # 注册统一事件处理程序，将分发给用户处理程序
        self.adapter.on_event(self._handle_and_dispatch_event)
        
        # 启动适配器
        await self.adapter.start()
        self._running = True
        
        logger.info("OneBot 客户端已启动")
    
    async def stop(self) -> None:
        """停止客户端。
        
        该方法优雅地关闭适配器并清理资源。
        """
        if not self._running:
            return
        
        self._running = False
        
        if self.adapter:
            await self.adapter.stop()
        
        logger.info("OneBot 客户端已停止")
    
    async def __aenter__(self):
        """异步上下文管理器入口。"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口。"""
        await self.stop()
    
    # 事件处理程序
    async def _handle_event(self, event: Event) -> None:
        """处理通用事件。"""
        await self._call_handlers("event", event)
    
    async def _handle_message(self, event: Event) -> None:
        """处理消息事件。"""
        await self._call_handlers("message", event)
    
    async def _handle_notice(self, event: Event) -> None:
        """处理通知事件。"""
        await self._call_handlers("notice", event)
    
    async def _handle_request(self, event: Event) -> None:
        """处理请求事件。"""
        await self._call_handlers("request", event)
    
    async def _handle_meta_event(self, event: Event) -> None:
        """处理元事件。"""
        await self._call_handlers("meta_event", event)

    async def _handle_and_dispatch_event(self, event: Event) -> None:
        """处理事件并分发给适当的处理程序。"""
        # 调用通用事件处理程序
        await self._call_handlers("event", event)

        # 分发给特定事件类型处理程序
        if hasattr(event, 'post_type'):
            post_type = event.post_type
            if post_type == "message":
                await self._call_handlers("message", event)
            elif post_type == "notice":
                await self._call_handlers("notice", event)
            elif post_type == "request":
                await self._call_handlers("request", event)
            elif post_type == "meta_event":
                await self._call_handlers("meta_event", event)
        
        # 处理匹配器事件
        await handle_event(event)
    
    async def _call_handlers(self, event_type: str, event: Event) -> None:
        """调用已注册的事件处理程序。"""
        handlers = self._event_handlers.get(event_type, [])
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(event)
                else:
                    handler(event)
            except Exception as e:
                logger.error(f"{event_type} 处理程序中出错: {e}")
    
    # 事件注册方法
    def on_event(self, handler: Callable[[Event], Awaitable[None]]) -> None:
        """注册通用事件处理程序。"""
        self._add_handler("event", handler)
    
    def on_message(self, handler: Callable[[MessageEvent], Awaitable[None]]) -> None:
        """注册消息事件处理程序。"""
        self._add_handler("message", handler)
    
    def on_notice(self, handler: Callable[[Event], Awaitable[None]]) -> None:
        """注册通知事件处理程序。"""
        self._add_handler("notice", handler)
    
    def on_request(self, handler: Callable[[Event], Awaitable[None]]) -> None:
        """注册请求事件处理程序。"""
        self._add_handler("request", handler)
    
    def on_meta_event(self, handler: Callable[[Event], Awaitable[None]]) -> None:
        """注册元事件处理程序。"""
        self._add_handler("meta_event", handler)
    
    def _add_handler(self, event_type: str, handler: Callable) -> None:
        """添加事件处理程序。"""
        if event_type not in self._event_handlers:
            self._event_handlers[event_type] = []
        self._event_handlers[event_type].append(handler)
    
    # 机器人方法
    def get_bot(self, self_id: Optional[int] = None) -> Optional[OneBotBot]:
        """获取机器人实例。"""
        if not self.adapter:
            return None
        return self.adapter.get_bot(self_id)
    
    def get_bots(self) -> List[OneBotBot]:
        """获取所有机器人实例。"""
        if not self.adapter:
            return []
        return self.adapter.get_bots()
    
    # 便利方法
    async def send_private_msg(
        self,
        user_id: int,
        message: Union[str, Message, List[MessageSegment]],
        bot_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """发送私聊消息。"""
        bot = self.get_bot(bot_id)
        if not bot:
            raise OneBotException("无可用机器人")
        return await bot.send_private_msg(user_id, message)
    
    async def send_group_msg(
        self,
        group_id: int,
        message: Union[str, Message, List[MessageSegment]],
        bot_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """发送群消息。"""
        bot = self.get_bot(bot_id)
        if not bot:
            raise OneBotException("无可用机器人")
        return await bot.send_group_msg(group_id, message)
    
    async def send_msg(
        self,
        message_type: str,
        message: Union[str, Message, List[MessageSegment]],
        user_id: Optional[int] = None,
        group_id: Optional[int] = None,
        bot_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """发送消息。"""
        bot = self.get_bot(bot_id)
        if not bot:
            raise OneBotException("No available bot")
        return await bot.send_msg(
            message_type=message_type,
            user_id=user_id,
            group_id=group_id,
            message=message
        )
    
    # 实用方法
    @classmethod
    def from_config_file(cls, config_path: str) -> "OneBotClient":
        """从配置文件创建客户端。"""
        import json
        import yaml
        
        with open(config_path, "r", encoding="utf-8") as f:
            if config_path.endswith(".json"):
                data = json.load(f)
            elif config_path.endswith((".yaml", ".yml")):
                data = yaml.safe_load(f)
            else:
                raise OneBotException("不支持的配置文件格式")
        
        config = Config.model_validate(data)
        return cls(config)
    
    @classmethod
    def create_simple_client(
        cls,
        connection_type: str,
        **kwargs
    ) -> "OneBotClient":
        """创建具有单个连接的简单客户端。"""
        from .config import (
            HttpConfig,
            WebSocketConfig,
            ReverseWebSocketConfig,
            WebhookConfig
        )
        
       
        kwargs.pop("self_id", None)
        
        if connection_type == "http":
            config = HttpConfig(**kwargs)
        elif connection_type == "websocket":
            config = WebSocketConfig(**kwargs)
        elif connection_type == "reverse_ws":
            config = ReverseWebSocketConfig(**kwargs)
        elif connection_type == "webhook":
            config = WebhookConfig(**kwargs)
        else:
            raise OneBotException(f"未知连接类型: {connection_type}")
        
        return cls(Config(
            connections=[config],
            api_timeout=30.0,
            max_concurrent_requests=100,
            enable_heartbeat=True,
            heartbeat_interval=30.0,
            reconnect_interval=5.0,
            max_reconnect_attempts=10
        ))
    
    async def run_forever(self) -> None:
        """永久运行客户端。"""
        try:
            while self._running:
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            pass
        except KeyboardInterrupt:
            logger.info("收到中断信号")
        finally:
            await self.stop()
    
    @property
    def is_running(self) -> bool:
        """检查客户端是否正在运行。"""
        return self._running

    async def call_api(self, action: str, **params: Any) -> Dict[str, Any]:
        """通过机器人调用 OneBot API。
        
        Args:
            action: 要调用的 API 操作
            **params: API 调用的参数
        
        Returns:
            包含 API 响应数据的字典
        
        Raises:
            OneBotException: 如果无可用机器人则抛出
        """
        bot = self.get_bot()
        if not bot:
            raise OneBotException("无可用机器人")
        return await bot.call_api(action, **params)
    
    def __getattr__(self, name: str) -> Any:
        """允许动态调用 API 方法。
        
        该方法允许直接在客户端实例上调用 API 方法，
        而无需显式定义每个方法。例如：
        
        # 代替：
        # await client.call_api("send_private_msg", user_id=123456, message="Hello")
        
        # 您可以使用：
        # await client.send_private_msg(user_id=123456, message="Hello")
        
        Args:
            name: 正在访问的属性名称
            
        Returns:
            一个在调用时将调用 API 的偏函数
            
        Raises:
            AttributeError: 如果名称是特殊属性（以 __ 开头和结尾）则抛出
        """
        if name.startswith("__") and name.endswith("__"):
            raise AttributeError(
                f"'{self.__class__.__name__}' 对象没有属性 '{name}'"
            )
        return partial(self.call_api, name)
