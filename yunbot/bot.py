"""OneBot v11 bot implementation.

This module provides the bot class that represents a single bot instance
connected through a connection. It handles API calls and provides methods
for interacting with the OneBot v11 protocol.
"""

from typing import Any, Dict, List, Optional, Union
from .connection import WebSocketConnection
from .event import Event, MessageEvent, PrivateMessageEvent, GroupMessageEvent
from .message import Message, MessageSegment
from .exceptions import ActionFailed, ApiNotAvailable, OneBotException
from .logger import default_logger as logger


class OneBotBot:
    """OneBot v11 bot implementation."""
    
    def __init__(self, self_id: int, connection: WebSocketConnection):
        """Initialize bot."""
        self.self_id = self_id
        self.connection = connection
        self._ready = False
    
    async def initialize(self) -> None:
        """Initialize bot.
        
        This method initializes the bot by getting login information and
        setting the bot's self_id. It also marks the bot as ready.
        
        Raises:
            Exception: If initialization fails
        """
        try:
            login_info = await self.get_login_info()
            self.self_id = login_info.get("user_id", self.self_id)
            self._ready = True
            logger.info(f"Bot {self.self_id} initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize bot: {e}")
            raise
    
    @property
    def is_ready(self) -> bool:
        """Check if bot is ready."""
        return self._ready
    
    async def call_api(self, action: str, **params: Any) -> Dict[str, Any]:
        """Call OneBot API.
        
        This method sends an API request through the bot's connection and
        returns the response data.
        
        Args:
            action: The API action to call
            **params: Parameters for the API call
        
        Returns:
            Dict containing the API response data
        
        Raises:
            ApiNotAvailable: If the connection is not available
            ActionFailed: If the API call fails
        """
        if not self.connection.is_connected:
            raise ApiNotAvailable("Connection not available")
        
        try:
            result = await self.connection.send_request(action, params)
            # Extract data field from full response
            if isinstance(result, dict) and "data" in result:
                return result["data"]
            return result
        except Exception as e:
            logger.error(f"API调用失败: {action} - {e}")
            raise ActionFailed(f"API调用失败: {e}")
    
    # Message APIs
    async def send_private_msg(
        self,
        user_id: int,
        message: Union[str, Message, List[MessageSegment]],
        auto_escape: bool = False
    ) -> Dict[str, Any]:
        """Send private message.
        
        Args:
            user_id: User ID to send message to
            message: Message content (string, Message object, or list of MessageSegment)
            auto_escape: Whether to auto-escape special characters
        
        Returns:
            Dict containing the API response
        """
        # Convert message to appropriate format
        if isinstance(message, str):
            message_data = Message(message).to_dict()
        elif isinstance(message, Message):
            message_data = message.to_dict()
        elif isinstance(message, list):
            if message and isinstance(message[0], MessageSegment):
                message_data = [seg.model_dump() for seg in message]
            else:
                message_data = message
        else:
            message_data = message
        
        return await self.call_api(
            "send_private_msg",
            user_id=user_id,
            message=message_data,
            auto_escape=auto_escape
        )
    
    async def send_group_msg(
        self,
        group_id: int,
        message: Union[str, Message, List[MessageSegment]],
        auto_escape: bool = False
    ) -> Dict[str, Any]:
        """Send group message.
        
        Args:
            group_id: Group ID to send message to
            message: Message content (string, Message object, or list of MessageSegment)
            auto_escape: Whether to auto-escape special characters
        
        Returns:
            Dict containing the API response
        """
        # Convert message to appropriate format
        if isinstance(message, str):
            message_data = Message(message).to_dict()
        elif isinstance(message, Message):
            message_data = message.to_dict()
        elif isinstance(message, list):
            if message and isinstance(message[0], MessageSegment):
                message_data = [seg.model_dump() for seg in message]
            else:
                message_data = message
        else:
            message_data = message
        
        return await self.call_api(
            "send_group_msg",
            group_id=group_id,
            message=message_data,
            auto_escape=auto_escape
        )
    
    async def send_msg(
        self,
        message_type: str,
        user_id: Optional[int] = None,
        group_id: Optional[int] = None,
        message: Optional[Union[str, Message, List[MessageSegment]]] = None,
        auto_escape: bool = False
    ) -> Dict[str, Any]:
        """Send message.
        
        Args:
            message_type: Type of message ("private" or "group")
            user_id: User ID for private messages
            group_id: Group ID for group messages
            message: Message content
            auto_escape: Whether to auto-escape special characters
        
        Returns:
            Dict containing the API response
        
        Raises:
            ValueError: If required parameters are missing or message_type is invalid
        """
        if message_type == "private":
            if user_id is None:
                raise ValueError("user_id is required for private message")
            if message is None:
                raise ValueError("message is required")
            return await self.send_private_msg(user_id, message, auto_escape)
        elif message_type == "group":
            if group_id is None:
                raise ValueError("group_id is required for group message")
            if message is None:
                raise ValueError("message is required")
            return await self.send_group_msg(group_id, message, auto_escape)
        else:
            raise ValueError(f"Invalid message_type: {message_type}")
    
    async def delete_msg(self, message_id: int) -> Dict[str, Any]:
        """Delete message."""
        return await self.call_api("delete_msg", message_id=message_id)
    
    async def get_msg(self, message_id: int) -> Dict[str, Any]:
        """Get message."""
        return await self.call_api("get_msg", message_id=message_id)
    
    async def get_forward_msg(self, message_id: int) -> Dict[str, Any]:
        """Get forward message."""
        return await self.call_api("get_forward_msg", message_id=message_id)
    
    async def send_like(self, user_id: int, times: int = 1) -> Dict[str, Any]:
        """Send like."""
        return await self.call_api("send_like", user_id=user_id, times=times)
    
    # Group Management APIs
    async def set_group_kick(
        self,
        group_id: int,
        user_id: int,
        reject_add_request: bool = False
    ) -> Dict[str, Any]:
        """Kick group member."""
        return await self.call_api(
            "set_group_kick",
            group_id=group_id,
            user_id=user_id,
            reject_add_request=reject_add_request
        )
    
    async def set_group_ban(
        self,
        group_id: int,
        user_id: int,
        duration: int = 30 * 60
    ) -> Dict[str, Any]:
        """Ban group member."""
        return await self.call_api(
            "set_group_ban",
            group_id=group_id,
            user_id=user_id,
            duration=duration
        )
    
    async def set_group_anonymous_ban(
        self,
        group_id: int,
        anonymous: Optional[Dict[str, Any]] = None,
        anonymous_flag: Optional[str] = None,
        duration: int = 30 * 60
    ) -> Dict[str, Any]:
        """Ban anonymous user.
        
        Args:
            group_id: Group ID
            anonymous: Anonymous user info
            anonymous_flag: Anonymous flag
            duration: Ban duration in seconds
        
        Returns:
            Dict containing the API response
        """
        params: Dict[str, Union[int, str, Dict[str, Any]]] = {"group_id": group_id, "duration": duration}
        if anonymous is not None:
            params["anonymous"] = anonymous
        if anonymous_flag is not None:
            params["anonymous_flag"] = anonymous_flag
        return await self.call_api("set_group_anonymous_ban", **params)
    
    async def set_group_whole_ban(
        self,
        group_id: int,
        enable: bool = True
    ) -> Dict[str, Any]:
        """Set group whole ban."""
        return await self.call_api(
            "set_group_whole_ban",
            group_id=group_id,
            enable=enable
        )
    
    async def set_group_admin(
        self,
        group_id: int,
        user_id: int,
        enable: bool = True
    ) -> Dict[str, Any]:
        """Set group admin."""
        return await self.call_api(
            "set_group_admin",
            group_id=group_id,
            user_id=user_id,
            enable=enable
        )
    
    async def set_group_anonymous(
        self,
        group_id: int,
        enable: bool = True
    ) -> Dict[str, Any]:
        """Set group anonymous."""
        return await self.call_api(
            "set_group_anonymous",
            group_id=group_id,
            enable=enable
        )
    
    async def set_group_card(
        self,
        group_id: int,
        user_id: int,
        card: str = ""
    ) -> Dict[str, Any]:
        """Set group card."""
        return await self.call_api(
            "set_group_card",
            group_id=group_id,
            user_id=user_id,
            card=card
        )
    
    async def set_group_name(self, group_id: int, group_name: str) -> Dict[str, Any]:
        """Set group name."""
        return await self.call_api(
            "set_group_name",
            group_id=group_id,
            group_name=group_name
        )
    
    async def set_group_leave(
        self,
        group_id: int,
        is_dismiss: bool = False
    ) -> Dict[str, Any]:
        """Leave group."""
        return await self.call_api(
            "set_group_leave",
            group_id=group_id,
            is_dismiss=is_dismiss
        )
    
    async def set_group_special_title(
        self,
        group_id: int,
        user_id: int,
        special_title: str = "",
        duration: int = -1
    ) -> Dict[str, Any]:
        """Set group special title."""
        return await self.call_api(
            "set_group_special_title",
            group_id=group_id,
            user_id=user_id,
            special_title=special_title,
            duration=duration
        )
    
    # Request Handling APIs
    async def set_friend_add_request(
        self,
        flag: str,
        approve: bool = True,
        remark: str = ""
    ) -> Dict[str, Any]:
        """Handle friend add request."""
        return await self.call_api(
            "set_friend_add_request",
            flag=flag,
            approve=approve,
            remark=remark
        )
    
    async def set_group_add_request(
        self,
        flag: str,
        sub_type: str,
        approve: bool = True,
        reason: str = ""
    ) -> Dict[str, Any]:
        """Handle group add request."""
        return await self.call_api(
            "set_group_add_request",
            flag=flag,
            sub_type=sub_type,
            approve=approve,
            reason=reason
        )
    
    # Information APIs
    async def get_login_info(self) -> Dict[str, Any]:
        """Get login info."""
        return await self.call_api("get_login_info")
    
    async def get_stranger_info(
        self,
        user_id: int,
        no_cache: bool = False
    ) -> Dict[str, Any]:
        """Get stranger info."""
        return await self.call_api(
            "get_stranger_info",
            user_id=user_id,
            no_cache=no_cache
        )
    
    async def get_friend_list(self) -> List[Dict[str, Any]]:
        """Get friend list."""
        result = await self.call_api("get_friend_list")
        return result if isinstance(result, list) else []
    
    async def get_group_info(
        self,
        group_id: int,
        no_cache: bool = False
    ) -> Dict[str, Any]:
        """Get group info."""
        return await self.call_api(
            "get_group_info",
            group_id=group_id,
            no_cache=no_cache
        )
    
    async def get_group_list(self) -> List[Dict[str, Any]]:
        """Get group list."""
        result = await self.call_api("get_group_list")
        return result if isinstance(result, list) else []
    
    async def get_group_member_info(
        self,
        group_id: int,
        user_id: int,
        no_cache: bool = False
    ) -> Dict[str, Any]:
        """Get group member info."""
        return await self.call_api(
            "get_group_member_info",
            group_id=group_id,
            user_id=user_id,
            no_cache=no_cache
        )
    
    async def get_group_member_list(
        self,
        group_id: int
    ) -> List[Dict[str, Any]]:
        """Get group member list."""
        result = await self.call_api("get_group_member_list", group_id=group_id)
        return result if isinstance(result, list) else []
    
    async def get_group_honor_info(
        self,
        group_id: int,
        type_: str
    ) -> Dict[str, Any]:
        """Get group honor info."""
        return await self.call_api(
            "get_group_honor_info",
            group_id=group_id,
            type=type_
        )
    
    async def get_cookies(self, domain: str) -> Dict[str, Any]:
        """Get cookies."""
        return await self.call_api("get_cookies", domain=domain)
    
    async def get_csrf_token(self) -> Dict[str, Any]:
        """Get CSRF token."""
        return await self.call_api("get_csrf_token")
    
    async def get_credentials(self, domain: str) -> Dict[str, Any]:
        """Get credentials."""
        return await self.call_api("get_credentials", domain=domain)
    
    async def get_record(
        self,
        file: str,
        out_format: str
    ) -> Dict[str, Any]:
        """Get record."""
        return await self.call_api(
            "get_record",
            file=file,
            out_format=out_format
        )
    
    async def get_image(self, file: str) -> Dict[str, Any]:
        """Get image."""
        return await self.call_api("get_image", file=file)
    
    async def can_send_image(self) -> Dict[str, Any]:
        """Check if can send image."""
        return await self.call_api("can_send_image")
    
    async def can_send_record(self) -> Dict[str, Any]:
        """Check if can send record."""
        return await self.call_api("can_send_record")
    
    async def get_status(self) -> Dict[str, Any]:
        """Get status."""
        return await self.call_api("get_status")
    
    async def get_version_info(self) -> Dict[str, Any]:
        """Get version info."""
        return await self.call_api("get_version_info")
    
    async def set_restart(self, delay: int = 0) -> Dict[str, Any]:
        """Set restart."""
        return await self.call_api("set_restart", delay=delay)
    
    async def clean_cache(self) -> Dict[str, Any]:
        """Clean cache."""
        return await self.call_api("clean_cache")
    
    # Helper methods
    async def send(self, event: Event, message: Union[str, Message, List[MessageSegment]]) -> Dict[str, Any]:
        """Reply to event."""
        if isinstance(event, PrivateMessageEvent):
            return await self.send_private_msg(event.user_id, message)
        elif isinstance(event, GroupMessageEvent):
            return await self.send_group_msg(event.group_id, message)
        else:
            raise ValueError("Cannot send message to this event type")
    
    async def reply(self, event: MessageEvent, message: Union[str, Message, List[MessageSegment]]) -> Dict[str, Any]:
        """Reply to message event."""
        return await self.send(event, message)