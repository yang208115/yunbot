"""OneBot v11 机器人实现。

该模块提供表示通过连接的单个机器人实例的机器人类。
它处理 API 调用并提供与 OneBot v11 协议交互的方法。
"""

from typing import Any, Dict, List, Optional, Union
from .connection import WebSocketConnection
from .event import Event, MessageEvent, PrivateMessageEvent, GroupMessageEvent
from .message import Message, MessageSegment
from .exceptions import ActionFailed, ApiNotAvailable, OneBotException
from .logger import default_logger as logger


class OneBotBot:
    """OneBot v11 机器人实现。"""
    
    def __init__(self, self_id: int, connection: WebSocketConnection):
        """初始化机器人。"""
        self.self_id = self_id
        self.connection = connection
        self._ready = False
    
    async def initialize(self) -> None:
        """初始化机器人。
        
        该方法通过获取登录信息并设置机器人的 self_id 来初始化机器人。
        它还将机器人标记为就绪状态。
        
        Raises:
            Exception: 初始化失败时抛出
        """
        try:
            login_info = await self.get_login_info()
            self.self_id = login_info.get("user_id", self.self_id)
            self._ready = True
            logger.info(f"机器人 {self.self_id} 初始化成功")
        except Exception as e:
            logger.error(f"初始化机器人失败: {e}")
            raise
    
    @property
    def is_ready(self) -> bool:
        """检查机器人是否就绪。"""
        return self._ready
    
    async def call_api(self, action: str, **params: Any) -> Dict[str, Any]:
        """调用 OneBot API。
        
        该方法通过机器人的连接发送 API 请求并返回响应数据。
        
        Args:
            action: 要调用的 API 操作
            **params: API 调用的参数
        
        Returns:
            包含 API 响应数据的字典
        
        Raises:
            ApiNotAvailable: 连接不可用时抛出
            ActionFailed: API 调用失败时抛出
        """
        if not self.connection.is_connected:
            raise ApiNotAvailable("连接不可用")
        
        try:
            result = await self.connection.send_request(action, params)
            # 从完整响应中提取数据字段
            if isinstance(result, dict) and "data" in result:
                return result["data"]
            return result
        except Exception as e:
            logger.error(f"API调用失败: {action} - {e}")
            raise ActionFailed(f"API调用失败: {e}")
    
    # 消息 API
    async def send_private_msg(
        self,
        user_id: int,
        message: Union[str, Message, List[MessageSegment]],
        auto_escape: bool = False
    ) -> Dict[str, Any]:
        """发送私聊消息。
        
        Args:
            user_id: 要发送消息的用户 ID
            message: 消息内容（字符串、Message 对象或 MessageSegment 列表）
            auto_escape: 是否自动转义特殊字符
        
        Returns:
            包含 API 响应的字典
        """
        # 将消息转换为适当的格式
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
        """发送群消息。
        
        Args:
            group_id: 要发送消息的群 ID
            message: 消息内容（字符串、Message 对象或 MessageSegment 列表）
            auto_escape: 是否自动转义特殊字符
        
        Returns:
            包含 API 响应的字典
        """
        # 将消息转换为适当的格式
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
        """发送消息。
        
        Args:
            message_type: 消息类型 ("private" 或 "group")
            user_id: 私聊消息的用户 ID
            group_id: 群消息的群 ID
            message: 消息内容
            auto_escape: 是否自动转义特殊字符
        
        Returns:
            包含 API 响应的字典
        
        Raises:
            ValueError: 缺少必需参数或 message_type 无效时抛出
        """
        if message_type == "private":
            if user_id is None:
                raise ValueError("私聊消息需要 user_id")
            if message is None:
                raise ValueError("消息是必需的")
            return await self.send_private_msg(user_id, message, auto_escape)
        elif message_type == "group":
            if group_id is None:
                raise ValueError("群消息需要 group_id")
            if message is None:
                raise ValueError("消息是必需的")
            return await self.send_group_msg(group_id, message, auto_escape)
        else:
            raise ValueError(f"无效的消息类型: {message_type}")
    
    async def delete_msg(self, message_id: int) -> Dict[str, Any]:
        """删除消息。"""
        return await self.call_api("delete_msg", message_id=message_id)
    
    async def get_msg(self, message_id: int) -> Dict[str, Any]:
        """获取消息。"""
        return await self.call_api("get_msg", message_id=message_id)
    
    async def get_forward_msg(self, message_id: int) -> Dict[str, Any]:
        """获取转发消息。"""
        return await self.call_api("get_forward_msg", message_id=message_id)
    
    async def send_like(self, user_id: int, times: int = 1) -> Dict[str, Any]:
        """发送赞。"""
        return await self.call_api("send_like", user_id=user_id, times=times)
    
    # 群管理 API
    async def set_group_kick(
        self,
        group_id: int,
        user_id: int,
        reject_add_request: bool = False
    ) -> Dict[str, Any]:
        """踢出群成员。"""
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
        """禁言群成员。"""
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
        """禁言匿名用户。
        
        Args:
            group_id: 群 ID
            anonymous: 匿名用户信息
            anonymous_flag: 匿名标记
            duration: 禁言时长（秒）
        
        Returns:
            包含 API 响应的字典
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
        """设置全员禁言。"""
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
        """设置群管理员。"""
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
        """设置群匿名。"""
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
        """设置群名片。"""
        return await self.call_api(
            "set_group_card",
            group_id=group_id,
            user_id=user_id,
            card=card
        )
    
    async def set_group_name(self, group_id: int, group_name: str) -> Dict[str, Any]:
        """设置群名称。"""
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
        """退出群。"""
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
        """设置群专属头衔。"""
        return await self.call_api(
            "set_group_special_title",
            group_id=group_id,
            user_id=user_id,
            special_title=special_title,
            duration=duration
        )
    
    # 请求处理 API
    async def set_friend_add_request(
        self,
        flag: str,
        approve: bool = True,
        remark: str = ""
    ) -> Dict[str, Any]:
        """处理好友添加请求。"""
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
        """处理群添加请求。"""
        return await self.call_api(
            "set_group_add_request",
            flag=flag,
            sub_type=sub_type,
            approve=approve,
            reason=reason
        )
    
    # 信息 API
    async def get_login_info(self) -> Dict[str, Any]:
        """获取登录信息。"""
        return await self.call_api("get_login_info")
    
    async def get_stranger_info(
        self,
        user_id: int,
        no_cache: bool = False
    ) -> Dict[str, Any]:
        """获取陌生人信息。"""
        return await self.call_api(
            "get_stranger_info",
            user_id=user_id,
            no_cache=no_cache
        )
    
    async def get_friend_list(self) -> List[Dict[str, Any]]:
        """获取好友列表。"""
        result = await self.call_api("get_friend_list")
        return result if isinstance(result, list) else []
    
    async def get_group_info(
        self,
        group_id: int,
        no_cache: bool = False
    ) -> Dict[str, Any]:
        """获取群信息。"""
        return await self.call_api(
            "get_group_info",
            group_id=group_id,
            no_cache=no_cache
        )
    
    async def get_group_list(self) -> List[Dict[str, Any]]:
        """获取群列表。"""
        result = await self.call_api("get_group_list")
        return result if isinstance(result, list) else []
    
    async def get_group_member_info(
        self,
        group_id: int,
        user_id: int,
        no_cache: bool = False
    ) -> Dict[str, Any]:
        """获取群成员信息。"""
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
        """获取群成员列表。"""
        result = await self.call_api("get_group_member_list", group_id=group_id)
        return result if isinstance(result, list) else []
    
    async def get_group_honor_info(
        self,
        group_id: int,
        type_: str
    ) -> Dict[str, Any]:
        """获取群荣誉信息。"""
        return await self.call_api(
            "get_group_honor_info",
            group_id=group_id,
            type=type_
        )
    
    async def get_cookies(self, domain: str) -> Dict[str, Any]:
        """获取 cookies。"""
        return await self.call_api("get_cookies", domain=domain)
    
    async def get_csrf_token(self) -> Dict[str, Any]:
        """获取 CSRF token。"""
        return await self.call_api("get_csrf_token")
    
    async def get_credentials(self, domain: str) -> Dict[str, Any]:
        """获取凭证。"""
        return await self.call_api("get_credentials", domain=domain)
    
    async def get_record(
        self,
        file: str,
        out_format: str
    ) -> Dict[str, Any]:
        """获取语音。"""
        return await self.call_api(
            "get_record",
            file=file,
            out_format=out_format
        )
    
    async def get_image(self, file: str) -> Dict[str, Any]:
        """获取图片。"""
        return await self.call_api("get_image", file=file)
    
    async def can_send_image(self) -> Dict[str, Any]:
        """检查是否可以发送图片。"""
        return await self.call_api("can_send_image")
    
    async def can_send_record(self) -> Dict[str, Any]:
        """检查是否可以发送语音。"""
        return await self.call_api("can_send_record")
    
    async def get_status(self) -> Dict[str, Any]:
        """获取状态。"""
        return await self.call_api("get_status")
    
    async def get_version_info(self) -> Dict[str, Any]:
        """获取版本信息。"""
        return await self.call_api("get_version_info")
    
    async def set_restart(self, delay: int = 0) -> Dict[str, Any]:
        """设置重启。"""
        return await self.call_api("set_restart", delay=delay)
    
    async def clean_cache(self) -> Dict[str, Any]:
        """清理缓存。"""
        return await self.call_api("clean_cache")
    
    # 辅助方法
    async def send(self, event: Event, message: Union[str, Message, List[MessageSegment]]) -> Dict[str, Any]:
        """回复事件。"""
        if isinstance(event, PrivateMessageEvent):
            return await self.send_private_msg(event.user_id, message)
        elif isinstance(event, GroupMessageEvent):
            return await self.send_group_msg(event.group_id, message)
        else:
            raise ValueError("无法向此事件类型发送消息")
    
    async def reply(self, event: MessageEvent, message: Union[str, Message, List[MessageSegment]]) -> Dict[str, Any]:
        """回复消息事件。"""
        return await self.send(event, message)