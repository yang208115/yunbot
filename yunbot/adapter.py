"""OneBot v11 client adapter.

This module provides the main adapter class that manages connections and events
for the OneBot v11 protocol client. It handles multiple connection types and
provides a unified interface for event handling and bot management.
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
    """OneBot v11 client adapter."""
    
    def __init__(self, config: Config):
        """Initialize adapter.
        
        Args:
            config: Configuration object containing connection settings
        """
        self.config = config
        self.connections: Dict[str, WebSocketConnection] = {}
        self.bots: Dict[int, OneBotBot] = {}
        self._event_emitter = EventEmitter()
        self._running = False
        self._tasks: List[asyncio.Task] = []
    
    async def start(self) -> None:
        """Start the adapter.
        
        This method initializes all configured connections and creates bot instances
        for each connection. It also sets up event handlers and starts the connection
        processes.
        
        Raises:
            Exception: If any error occurs during the startup process
        """
        if self._running:
            logger.warning("Adapter is already running")
            return
        
        logger.info("启动OneBot v11适配器...")
        
        try:
            # Create and start connections
            for conn_config in self.config.connections:
                connection = create_connection(conn_config)
                
                # Add event handler to connection
                connection.add_event_handler(self._handle_event)
                
                # Start connection
                await connection.connect()
                
                self.connections[conn_config.type] = connection
                
                # Create bot instance for this connection
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
                            logger.info(f"Bot {actual_self_id} initialized successfully via get_login_info")
                        else:
                            logger.warning("Failed to get valid self_id from get_login_info")
                    except Exception as e:
                        logger.error(f"Failed to initialize bot via get_login_info: {e}")
            
            self._running = True
            logger.info("OneBot v11 adapter started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start adapter: {e}")
            await self.stop()
            raise
    
    async def stop(self) -> None:
        """Stop the adapter.
        
        This method gracefully shuts down all connections and cleans up resources.
        It cancels all running tasks and disconnects all active connections.
        """
        logger.info("Stopping OneBot v11 adapter...")
        self._running = False
        
        # Cancel all tasks
        for task in self._tasks:
            if not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        
        self._tasks.clear()
        
        # Disconnect all connections
        for connection in self.connections.values():
            try:
                await connection.disconnect()
            except Exception as e:
                logger.error(f"Error disconnecting connection: {e}")
        
        self.connections.clear()
        self.bots.clear()
        
        logger.info("OneBot v11 adapter stopped")
    
    async def _handle_event(self, event: Event) -> None:
        """Handle incoming event.
        
        This method processes incoming events, registers new bots if needed,
        and emits the event to registered handlers.
        
        Args:
            event: The incoming event to handle
        """
        try:
            logger.debug(f"已接收事件: {event.post_type}")
            
            # Update bot self_id if not set
            if event.self_id not in self.bots and event.self_id != 0:
                # Try to find a connection that can handle this bot
                for connection in self.connections.values():
                    if connection.is_connected:
                        # Create bot directly without re-initialization
                        # (already initialized during startup)
                        bot = OneBotBot(event.self_id, connection)
                        self.bots[event.self_id] = bot
                        logger.info(f"Auto-registered bot {event.self_id}")
                        break
            
            # Emit event to handlers using create_task to avoid blocking
            asyncio.create_task(self._event_emitter.emit("event", event))
            asyncio.create_task(self._event_emitter.emit(f"event.{event.post_type}", event))
            
        except Exception as e:
            logger.error(f"Error handling event: {e}")
    
    def on_event(self, handler: Callable[[Event], Awaitable[None]]) -> None:
        """Register event handler."""
        self._event_emitter.on("event", handler)
    
    def on_message(self, handler: Callable[[Event], Awaitable[None]]) -> None:
        """Register message event handler."""
        self._event_emitter.on("event.message", handler)
    
    def on_notice(self, handler: Callable[[Event], Awaitable[None]]) -> None:
        """Register notice event handler."""
        self._event_emitter.on("event.notice", handler)

    def on_request(self, handler: Callable[[Event], Awaitable[None]]) -> None:
        """Register request event handler."""
        self._event_emitter.on("event.request", handler)

    def on_meta_event(self, handler: Callable[[Event], Awaitable[None]]) -> None:
        """Register meta event handler."""
        self._event_emitter.on("event.meta_event", handler)
    
    def get_bot(self, self_id: Optional[int] = None) -> Optional[OneBotBot]:
        """Get bot instance."""
        if self_id is None:
            # Return first available bot
            return next(iter(self.bots.values()), None)
        return self.bots.get(self_id)
    
    def get_bots(self) -> List[OneBotBot]:
        """Get all bot instances."""
        return list(self.bots.values())
    
    def get_connection(self, connection_type: str) -> Optional[WebSocketConnection]:
        """Get connection by type."""
        return self.connections.get(connection_type)
    
    def get_connections(self) -> List[WebSocketConnection]:
        """Get all connections."""
        return list(self.connections.values())
    
    @property
    def is_running(self) -> bool:
        """Check if adapter is running."""
        return self._running
    
    async def wait_for_stop(self) -> None:
        """Wait until adapter stops."""
        try:
            while self._running:
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            pass