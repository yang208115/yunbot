"""OneBot v11 客户端适配器。

该模块提供主适配器类，用于管理 OneBot v11 协议客户端的连接和事件。
它处理多种连接类型，并为事件处理和机器人管理提供统一接口。
"""

import asyncio
from typing import Any, Awaitable, Callable, Dict, List, Optional

from .config import Config
from .connection import WebSocketConnection, create_connection
from .bot import OneBotBot
from .event import Event, parse_event
from .exceptions import OneBotException, ConfigurationError
from .utils import EventEmitter
from .logger import default_logger as logger


class OneBotAdapter:
    """OneBot v11 客户端适配器。"""
    
    def __init__(self, config: Config):
        """初始化适配器。
        
        Args:
            config: 包含连接设置的配置对象
        """
        self.config = config
        self.connections: Dict[str, WebSocketConnection] = {}
        self.bots: Dict[int, OneBotBot] = {}
        self._event_emitter = EventEmitter()
        self._running = False
        self._tasks: List[asyncio.Task] = []
    
    async def start(self) -> None:
        """启动适配器。
        
        该方法初始化所有已配置的连接，并为每个连接创建机器人实例。
        它还设置事件处理程序并启动连接进程。
        
        Raises:
            Exception: 启动过程中发生任何错误时抛出
        """
        if self._running:
            logger.warning("适配器已在运行")
            return
        
        logger.info("启动OneBot v11适配器...")
        
        try:
            # 创建并启动连接
            for conn_config in self.config.connections:
                connection = create_connection(conn_config)
                
                # 为连接添加事件处理程序
                connection.add_event_handler(self._handle_event)
                
                # 启动连接
                await connection.connect()
                
                self.connections[conn_config.type] = connection
                
                # 为该连接创建机器人实例
                # 如果没有指定 self_id，则稍后通过 get_login_info 获取
                if conn_config.self_id:
                    bot = OneBotBot(int(conn_config.self_id), connection)
                    await bot.initialize()
                    self.bots[bot.self_id] = bot
                else:
                    # 先创建一个临时的 bot 实例，稍后通过 get_login_info 初始化
                    bot = OneBotBot(0, connection)  # 临时 ID 为 0
                    # 调用 get_login_info 获取实际的 self_id
                    try:
                        login_info = await bot.get_login_info()
                        actual_self_id = login_info.get("user_id", 0)
                        if actual_self_id != 0:
                            bot.self_id = actual_self_id
                            await bot.initialize()
                            self.bots[bot.self_id] = bot
                            logger.info(f"机器人 {actual_self_id} 通过 get_login_info 初始化成功")
                        else:
                            logger.warning("未能从 get_login_info 获取有效的 self_id")
                    except Exception as e:
                        logger.error(f"通过 get_login_info 初始化机器人失败: {e}")
            
            self._running = True
            logger.info("OneBot v11 适配器启动成功")
            
        except Exception as e:
            logger.error(f"启动适配器失败: {e}")
            await self.stop()
            raise
    
    async def stop(self) -> None:
        """停止适配器。
        
        该方法优雅地关闭所有连接并清理资源。
        它取消所有运行任务并断开所有活动连接。
        """
        logger.info("停止 OneBot v11 适配器...")
        self._running = False
        
        # 取消所有任务
        for task in self._tasks:
            if not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        
        self._tasks.clear()
        
        # 断开所有连接
        for connection in self.connections.values():
            try:
                await connection.disconnect()
            except Exception as e:
                logger.error(f"断开连接时出错: {e}")
        
        self.connections.clear()
        self.bots.clear()
        
        logger.info("OneBot v11 适配器已停止")
    
    async def _handle_event(self, event: Event) -> None:
        """处理传入事件。
        
        该方法处理传入事件，在需要时注册新机器人，
        并将事件发送给已注册的处理程序。
        
        Args:
            event: 要处理的传入事件
        """
        try:
            logger.debug(f"已接收事件: {event.post_type}")
            
            # 如果未设置，更新机器人的 self_id
            if event.self_id not in self.bots and event.self_id != 0:
                # 尝试查找可以处理该机器人的连接
                for connection in self.connections.values():
                    if connection.is_connected:
                        # 直接创建机器人，无需重新初始化
                        # (已在启动期间初始化)
                        bot = OneBotBot(event.self_id, connection)
                        self.bots[event.self_id] = bot
                        logger.info(f"自动注册机器人 {event.self_id}")
                        break
            
            # 使用 create_task 向处理程序发送事件以避免阻塞
            asyncio.create_task(self._event_emitter.emit("event", event))
            asyncio.create_task(self._event_emitter.emit(f"event.{event.post_type}", event))
            
        except Exception as e:
            logger.error(f"处理事件时出错: {e}")
    
    def on_event(self, handler: Callable[[Event], Awaitable[None]]) -> None:
        """注册事件处理程序。"""
        self._event_emitter.on("event", handler)
    
    def on_message(self, handler: Callable[[Event], Awaitable[None]]) -> None:
        """注册消息事件处理程序。"""
        self._event_emitter.on("event.message", handler)
    
    def on_notice(self, handler: Callable[[Event], Awaitable[None]]) -> None:
        """注册通知事件处理程序。"""
        self._event_emitter.on("event.notice", handler)

    def on_request(self, handler: Callable[[Event], Awaitable[None]]) -> None:
        """注册请求事件处理程序。"""
        self._event_emitter.on("event.request", handler)

    def on_meta_event(self, handler: Callable[[Event], Awaitable[None]]) -> None:
        """注册元事件处理程序。"""
        self._event_emitter.on("event.meta_event", handler)
    
    def get_bot(self, self_id: Optional[int] = None) -> Optional[OneBotBot]:
        """获取机器人实例。"""
        if self_id is None:
            # 返回第一个可用的机器人
            return next(iter(self.bots.values()), None)
        return self.bots.get(self_id)
    
    def get_bots(self) -> List[OneBotBot]:
        """获取所有机器人实例。"""
        return list(self.bots.values())
    
    def get_connection(self, connection_type: str) -> Optional[WebSocketConnection]:
        """按类型获取连接。"""
        return self.connections.get(connection_type)
    
    def get_connections(self) -> List[WebSocketConnection]:
        """获取所有连接。"""
        return list(self.connections.values())
    
    @property
    def is_running(self) -> bool:
        """检查适配器是否正在运行。"""
        return self._running
    
    async def wait_for_stop(self) -> None:
        """等待适配器停止。"""
        try:
            while self._running:
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            pass