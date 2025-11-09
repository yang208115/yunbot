"""High-level client interface for OneBot v11 adapter.

This module provides a high-level client interface that simplifies the usage
of the OneBot v11 adapter. It handles configuration, connection management,
and event dispatching.
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
    """High-level OneBot v11 client interface."""
    
    def __init__(self, config: Optional[Config] = None):
        """Initialize client.
        
        Args:
            config: Configuration object for the client
        """
        self.config = config
        self.adapter: Optional[OneBotAdapter] = None
        self._event_handlers: Dict[str, List[Callable]] = {}
        self._running = False
    
    async def start(self, config: Optional[Config] = None) -> None:
        """Start the client.
        
        This method initializes the adapter, registers event handlers,
        and starts the connection processes.
        
        Args:
            config: Optional configuration to use instead of the one provided in __init__
        
        Raises:
            OneBotException: If no configuration is provided
        """
        if self._running:
            logger.warning("Client is already running")
            return
        
        if config:
            self.config = config
        
        if not self.config:
            raise OneBotException("No configuration provided")
        
        self.adapter = OneBotAdapter(self.config)

        # Register unified event handler that will dispatch to user handlers
        self.adapter.on_event(self._handle_and_dispatch_event)
        
        # Start adapter
        await self.adapter.start()
        self._running = True
        
        logger.info("OneBot client started")
    
    async def stop(self) -> None:
        """Stop the client.
        
        This method gracefully shuts down the adapter and cleans up resources.
        """
        if not self._running:
            return
        
        self._running = False
        
        if self.adapter:
            await self.adapter.stop()
        
        logger.info("OneBot client stopped")
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.stop()
    
    # Event handlers
    async def _handle_event(self, event: Event) -> None:
        """Handle generic event."""
        await self._call_handlers("event", event)
    
    async def _handle_message(self, event: Event) -> None:
        """Handle message event."""
        await self._call_handlers("message", event)
    
    async def _handle_notice(self, event: Event) -> None:
        """Handle notice event."""
        await self._call_handlers("notice", event)
    
    async def _handle_request(self, event: Event) -> None:
        """Handle request event."""
        await self._call_handlers("request", event)
    
    async def _handle_meta_event(self, event: Event) -> None:
        """Handle meta event."""
        await self._call_handlers("meta_event", event)

    async def _handle_and_dispatch_event(self, event: Event) -> None:
        """Handle event and dispatch to appropriate handlers."""
        # Call generic event handlers
        await self._call_handlers("event", event)

        # Dispatch to specific event type handlers
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
        
        # Handle matcher events
        await handle_event(event)
    
    async def _call_handlers(self, event_type: str, event: Event) -> None:
        """Call registered event handlers."""
        handlers = self._event_handlers.get(event_type, [])
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(event)
                else:
                    handler(event)
            except Exception as e:
                logger.error(f"Error in {event_type} handler: {e}")
    
    # Event registration methods
    def on_event(self, handler: Callable[[Event], Awaitable[None]]) -> None:
        """Register generic event handler."""
        self._add_handler("event", handler)
    
    def on_message(self, handler: Callable[[MessageEvent], Awaitable[None]]) -> None:
        """Register message event handler."""
        self._add_handler("message", handler)
    
    def on_notice(self, handler: Callable[[Event], Awaitable[None]]) -> None:
        """Register notice event handler."""
        self._add_handler("notice", handler)
    
    def on_request(self, handler: Callable[[Event], Awaitable[None]]) -> None:
        """Register request event handler."""
        self._add_handler("request", handler)
    
    def on_meta_event(self, handler: Callable[[Event], Awaitable[None]]) -> None:
        """Register meta event handler."""
        self._add_handler("meta_event", handler)
    
    def _add_handler(self, event_type: str, handler: Callable) -> None:
        """Add event handler."""
        if event_type not in self._event_handlers:
            self._event_handlers[event_type] = []
        self._event_handlers[event_type].append(handler)
    
    # Bot methods
    def get_bot(self, self_id: Optional[int] = None) -> Optional[OneBotBot]:
        """Get bot instance."""
        if not self.adapter:
            return None
        return self.adapter.get_bot(self_id)
    
    def get_bots(self) -> List[OneBotBot]:
        """Get all bot instances."""
        if not self.adapter:
            return []
        return self.adapter.get_bots()
    
    # Convenience methods
    async def send_private_msg(
        self,
        user_id: int,
        message: Union[str, Message, List[MessageSegment]],
        bot_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Send private message."""
        bot = self.get_bot(bot_id)
        if not bot:
            raise OneBotException("No available bot")
        return await bot.send_private_msg(user_id, message)
    
    async def send_group_msg(
        self,
        group_id: int,
        message: Union[str, Message, List[MessageSegment]],
        bot_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Send group message."""
        bot = self.get_bot(bot_id)
        if not bot:
            raise OneBotException("No available bot")
        return await bot.send_group_msg(group_id, message)
    
    async def send_msg(
        self,
        message_type: str,
        message: Union[str, Message, List[MessageSegment]],
        user_id: Optional[int] = None,
        group_id: Optional[int] = None,
        bot_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Send message."""
        bot = self.get_bot(bot_id)
        if not bot:
            raise OneBotException("No available bot")
        return await bot.send_msg(
            message_type=message_type,
            user_id=user_id,
            group_id=group_id,
            message=message
        )
    
    # Utility methods
    @classmethod
    def from_config_file(cls, config_path: str) -> "OneBotClient":
        """Create client from configuration file."""
        import json
        import yaml
        
        with open(config_path, "r", encoding="utf-8") as f:
            if config_path.endswith(".json"):
                data = json.load(f)
            elif config_path.endswith((".yaml", ".yml")):
                data = yaml.safe_load(f)
            else:
                raise OneBotException("Unsupported config file format")
        
        config = Config.model_validate(data)
        return cls(config)
    
    @classmethod
    def create_simple_client(
        cls,
        connection_type: str,
        **kwargs
    ) -> "OneBotClient":
        """Create simple client with single connection."""
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
            raise OneBotException(f"Unknown connection type: {connection_type}")
        
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
        """Run client forever."""
        try:
            while self._running:
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            pass
        except KeyboardInterrupt:
            logger.info("Received interrupt signal")
        finally:
            await self.stop()
    
    @property
    def is_running(self) -> bool:
        """Check if client is running."""
        return self._running

    async def call_api(self, action: str, **params: Any) -> Dict[str, Any]:
        """Call OneBot API through bot.
        
        Args:
            action: The API action to call
            **params: Parameters for the API call
        
        Returns:
            Dict containing the API response data
        
        Raises:
            OneBotException: If no bot is available
        """
        bot = self.get_bot()
        if not bot:
            raise OneBotException("No available bot")
        return await bot.call_api(action, **params)
    
    def __getattr__(self, name: str) -> Any:
        """Allow calling API methods dynamically.
        
        This method allows calling API methods directly on the client instance
        without explicitly defining each method. For example:
        
        # Instead of:
        # await client.call_api("send_private_msg", user_id=123456, message="Hello")
        
        # You can use:
        # await client.send_private_msg(user_id=123456, message="Hello")
        
        Args:
            name: The name of the attribute being accessed
            
        Returns:
            A partial function that will call the API when invoked
            
        Raises:
            AttributeError: If the name is a special attribute (starts and ends with __)
        """
        if name.startswith("__") and name.endswith("__"):
            raise AttributeError(
                f"'{self.__class__.__name__}' object has no attribute '{name}'"
            )
        return partial(self.call_api, name)
