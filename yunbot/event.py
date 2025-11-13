"""OneBot v11 协议的事件模型。

该模块为所有 OneBot v11 事件类型提供 Pydantic 模型。
它包括基础事件类和特定的事件类型，包括消息、通知、请求和元事件。
"""

from typing import Any, Dict, List, Optional, Union, Literal, TYPE_CHECKING
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, field_validator, ConfigDict

if TYPE_CHECKING:
    from .bot import OneBotBot


class PostType(str, Enum):
    """帖子类型枚举。"""
    MESSAGE = "message"
    NOTICE = "notice"
    REQUEST = "request"
    META_EVENT = "meta_event"


class MessageType(str, Enum):
    """消息类型枚举。"""
    PRIVATE = "private"
    GROUP = "group"


class NoticeType(str, Enum):
    """通知类型枚举。"""
    GROUP_UPLOAD = "group_upload"
    GROUP_ADMIN = "group_admin"
    GROUP_DECREASE = "group_decrease"
    GROUP_INCREASE = "group_increase"
    GROUP_BAN = "group_ban"
    FRIEND_ADD = "friend_add"
    GROUP_RECALL = "group_recall"
    FRIEND_RECALL = "friend_recall"
    NOTIFY = "notify"
    GROUP_CARD = "group_card"
    OFFLINE_FILE = "offline_file"
    ESSENCE = "essence"


class RequestType(str, Enum):
    """请求类型枚举。"""
    FRIEND = "friend"
    GROUP = "group"


class MetaEventType(str, Enum):
    """元事件类型枚举。"""
    LIFECYCLE = "lifecycle"
    HEARTBEAT = "heartbeat"


class Sender(BaseModel):
    """消息发送者信息。"""
    
    user_id: int = Field(..., description="用户 ID")
    nickname: Optional[str] = Field(None, description="昵称")
    sex: Optional[str] = Field(None, description="性别")
    age: Optional[int] = Field(None, description="年龄")
    card: Optional[str] = Field(None, description="群名片")
    area: Optional[str] = Field(None, description="地区")
    level: Optional[str] = Field(None, description="等级")
    role: Optional[str] = Field(None, description="群内角色")
    title: Optional[str] = Field(None, description="群头衔")


class Anonymous(BaseModel):
    """匿名用户信息。"""
    
    id: int = Field(..., description="匿名 ID")
    name: str = Field(..., description="匿名名称")
    flag: str = Field(..., description="匿名标识")


class File(BaseModel):
    """文件信息。"""
    
    id: str = Field(..., description="文件 ID")
    name: str = Field(..., description="文件名")
    size: int = Field(..., description="文件大小（字节）")
    busid: int = Field(..., description="总线 ID")


class Event(BaseModel):
    """基础事件类。
    
    这是所有 OneBot v11 事件的基础类。它包含所有事件类型中都存在的公共字段。
    """
    
    time: datetime = Field(default_factory=datetime.now, description="事件时间戳")
    self_id: int = Field(..., description="机器人自身 ID")
    post_type: str = Field(..., description="帖子类型")
    
    model_config = ConfigDict(
        extra="allow",
        json_encoders={
            datetime: lambda v: int(v.timestamp()),
        },
    )


class MessageEvent(Event):
    """消息事件。
    
    所有消息事件的基础类。包含私聊和群消息的公共字段。
    """
    
    post_type: str = PostType.MESSAGE
    message_type: str = Field(..., description="消息类型")
    sub_type: str = Field(..., description="消息子类型")
    message_id: int = Field(..., description="消息 ID")
    user_id: int = Field(..., description="用户 ID")
    message: Union[str, List[Dict[str, Any]]] = Field(..., description="消息内容")
    raw_message: Optional[str] = Field(None, description="原始消息内容")
    font: Optional[int] = Field(None, description="字体")
    sender: Optional[Sender] = Field(None, description="发送者信息")
    
    @field_validator("message", mode="before")
    def parse_message(cls, v: Union[str, List[Dict[str, Any]]]) -> Union[str, List[Dict[str, Any]]]:
        """解析消息内容。"""
        return v


class PrivateMessageEvent(MessageEvent):
    """私聊消息事件。"""
    
    message_type: str = MessageType.PRIVATE
    temp_source: Optional[int] = Field(None, description="临时消息来源")


class GroupMessageEvent(MessageEvent):
    """群消息事件。"""
    
    message_type: str = MessageType.GROUP
    group_id: int = Field(..., description="群 ID")
    anonymous: Optional[Anonymous] = Field(None, description="匿名信息")


class NoticeEvent(Event):
    """通知事件。"""
    
    post_type: str = PostType.NOTICE
    notice_type: str = Field(..., description="通知类型")


class GroupUploadNoticeEvent(NoticeEvent):
    """群文件上传通知事件。"""
    
    notice_type: str = NoticeType.GROUP_UPLOAD
    group_id: int = Field(..., description="群 ID")
    user_id: int = Field(..., description="用户 ID")
    file: File = Field(..., description="文件信息")


class GroupAdminNoticeEvent(NoticeEvent):
    """群管理员变更通知事件。"""
    
    notice_type: str = NoticeType.GROUP_ADMIN
    sub_type: str = Field(..., description="管理员变更类型（设置/取消）")
    group_id: int = Field(..., description="群 ID")
    user_id: int = Field(..., description="用户 ID")


class GroupDecreaseNoticeEvent(NoticeEvent):
    """群成员减少通知事件。"""
    
    notice_type: str = NoticeType.GROUP_DECREASE
    sub_type: str = Field(..., description="减少类型（离开/被踢/自己被踢）")
    group_id: int = Field(..., description="群 ID")
    operator_id: int = Field(..., description="操作者 ID")
    user_id: int = Field(..., description="用户 ID")


class GroupIncreaseNoticeEvent(NoticeEvent):
    """群成员增加通知事件。"""
    
    notice_type: str = NoticeType.GROUP_INCREASE
    sub_type: str = Field(..., description="增加类型（同意/邀请）")
    group_id: int = Field(..., description="群 ID")
    operator_id: int = Field(..., description="操作者 ID")
    user_id: int = Field(..., description="用户 ID")


class GroupBanNoticeEvent(NoticeEvent):
    """群禁言通知事件。"""
    
    notice_type: str = NoticeType.GROUP_BAN
    sub_type: str = Field(..., description="禁言类型（禁言/解除禁言）")
    group_id: int = Field(..., description="群 ID")
    operator_id: int = Field(..., description="操作者 ID")
    user_id: int = Field(..., description="用户 ID")
    duration: int = Field(..., description="禁言时长（秒）")


class FriendAddNoticeEvent(NoticeEvent):
    """好友添加通知事件。"""
    
    notice_type: str = NoticeType.FRIEND_ADD
    user_id: int = Field(..., description="用户 ID")


class GroupRecallNoticeEvent(NoticeEvent):
    """群消息撤回通知事件。"""
    
    notice_type: str = NoticeType.GROUP_RECALL
    group_id: int = Field(..., description="群 ID")
    user_id: int = Field(..., description="用户 ID")
    operator_id: int = Field(..., description="操作者 ID")
    message_id: int = Field(..., description="消息 ID")


class FriendRecallNoticeEvent(NoticeEvent):
    """好友消息撤回通知事件。"""
    
    notice_type: str = NoticeType.FRIEND_RECALL
    user_id: int = Field(..., description="用户 ID")
    message_id: int = Field(..., description="消息 ID")


class NotifyNoticeEvent(NoticeEvent):
    """通知类通知事件。"""
    
    notice_type: str = NoticeType.NOTIFY
    sub_type: str = Field(..., description="通知子类型")
    group_id: int = Field(..., description="群 ID")
    user_id: int = Field(..., description="用户 ID")


class GroupCardNoticeEvent(NotifyNoticeEvent):
    """群名片变更通知事件。"""
    
    sub_type: str = "group_card"
    card_new: str = Field(..., description="新名片")
    card_old: str = Field(..., description="旧名片")


class OfflineFileNoticeEvent(NoticeEvent):
    """离线文件通知事件。"""
    
    notice_type: str = NoticeType.OFFLINE_FILE
    user_id: int = Field(..., description="用户 ID")
    file: File = Field(..., description="文件信息")


class EssenceNoticeEvent(NoticeEvent):
    """精华消息通知事件。"""
    
    notice_type: str = NoticeType.ESSENCE
    sub_type: str = Field(..., description="精华类型（添加/删除）")
    group_id: int = Field(..., description="群 ID")
    sender_id: int = Field(..., description="消息发送者 ID")
    operator_id: int = Field(..., description="操作者 ID")
    message_id: int = Field(..., description="消息 ID")


class RequestEvent(Event):
    """请求事件。"""
    
    post_type: str = PostType.REQUEST
    request_type: str = Field(..., description="请求类型")
    
    async def approve(self, bot: "OneBotBot", remark: Optional[str] = None) -> Dict[str, Any]:
        """同意请求。"""
        raise NotImplementedError
    
    async def reject(self, bot: "OneBotBot", remark: Optional[str] = None) -> Dict[str, Any]:
        """拒绝请求。"""
        raise NotImplementedError


class FriendRequestEvent(RequestEvent):
    """好友请求事件。"""
    
    request_type: str = RequestType.FRIEND
    user_id: int = Field(..., description="用户 ID")
    comment: str = Field(..., description="请求备注")
    flag: str = Field(..., description="请求标识")
    
    async def approve(self, bot: "OneBotBot", remark: Optional[str] = None) -> Dict[str, Any]:
        """同意好友请求。"""
        return await bot.set_friend_add_request(
            flag=self.flag,
            approve=True,
            remark=remark or ""
        )
    
    async def reject(self, bot: "OneBotBot", remark: Optional[str] = None) -> Dict[str, Any]:
        """拒绝好友请求。"""
        return await bot.set_friend_add_request(
            flag=self.flag,
            approve=False,
            remark=remark or ""
        )


class GroupRequestEvent(RequestEvent):
    """群请求事件。"""
    
    request_type: str = RequestType.GROUP
    sub_type: str = Field(..., description="请求子类型（添加/邀请）")
    group_id: int = Field(..., description="群 ID")
    user_id: int = Field(..., description="用户 ID")
    comment: str = Field(..., description="请求备注")
    flag: str = Field(..., description="请求标识")
    
    async def approve(self, bot: "OneBotBot", remark: Optional[str] = None) -> Dict[str, Any]:
        """同意群请求。"""
        return await bot.set_group_add_request(
            flag=self.flag,
            sub_type=self.sub_type,
            approve=True,
            reason=remark or ""
        )
    
    async def reject(self, bot: "OneBotBot", remark: Optional[str] = None) -> Dict[str, Any]:
        """拒绝群请求。"""
        return await bot.set_group_add_request(
            flag=self.flag,
            sub_type=self.sub_type,
            approve=False,
            reason=remark or ""
        )


class MetaEvent(Event):
    """元事件。"""
    
    post_type: str = PostType.META_EVENT
    meta_event_type: str = Field(..., description="元事件类型")


class LifecycleMetaEvent(MetaEvent):
    """生命周期元事件。"""
    
    meta_event_type: str = MetaEventType.LIFECYCLE
    sub_type: str = Field(..., description="生命周期子类型（启用/禁用/连接）")


class HeartbeatMetaEvent(MetaEvent):
    """心跳元事件。"""
    
    meta_event_type: str = MetaEventType.HEARTBEAT
    status: Dict[str, Any] = Field(..., description="机器人状态")
    interval: int = Field(..., description="心跳间隔（毫秒）")


def parse_event(data: Dict[str, Any]) -> Event:
    """从原始数据解析事件。"""
    post_type = data.get("post_type")
    
    if post_type == PostType.MESSAGE:
        message_type = data.get("message_type")
        if message_type == MessageType.PRIVATE:
            return PrivateMessageEvent.model_validate(data)
        elif message_type == MessageType.GROUP:
            return GroupMessageEvent.model_validate(data)
        else:
            return MessageEvent.model_validate(data)
    
    elif post_type == PostType.NOTICE:
        notice_type = data.get("notice_type")
        if notice_type == NoticeType.GROUP_UPLOAD:
            return GroupUploadNoticeEvent.model_validate(data)
        elif notice_type == NoticeType.GROUP_ADMIN:
            return GroupAdminNoticeEvent.model_validate(data)
        elif notice_type == NoticeType.GROUP_DECREASE:
            return GroupDecreaseNoticeEvent.model_validate(data)
        elif notice_type == NoticeType.GROUP_INCREASE:
            return GroupIncreaseNoticeEvent.model_validate(data)
        elif notice_type == NoticeType.GROUP_BAN:
            return GroupBanNoticeEvent.model_validate(data)
        elif notice_type == NoticeType.FRIEND_ADD:
            return FriendAddNoticeEvent.model_validate(data)
        elif notice_type == NoticeType.GROUP_RECALL:
            return GroupRecallNoticeEvent.model_validate(data)
        elif notice_type == NoticeType.FRIEND_RECALL:
            return FriendRecallNoticeEvent.model_validate(data)
        elif notice_type == NoticeType.NOTIFY:
            sub_type = data.get("sub_type")
            if sub_type == "group_card":
                return GroupCardNoticeEvent.model_validate(data)
            else:
                return NotifyNoticeEvent.model_validate(data)
        elif notice_type == NoticeType.OFFLINE_FILE:
            return OfflineFileNoticeEvent.model_validate(data)
        elif notice_type == NoticeType.ESSENCE:
            return EssenceNoticeEvent.model_validate(data)
        else:
            return NoticeEvent.model_validate(data)
    
    elif post_type == PostType.REQUEST:
        request_type = data.get("request_type")
        if request_type == RequestType.FRIEND:
            return FriendRequestEvent.model_validate(data)
        elif request_type == RequestType.GROUP:
            return GroupRequestEvent.model_validate(data)
        else:
            return RequestEvent.model_validate(data)
    
    elif post_type == PostType.META_EVENT:
        meta_event_type = data.get("meta_event_type")
        if meta_event_type == MetaEventType.LIFECYCLE:
            return LifecycleMetaEvent.model_validate(data)
        elif meta_event_type == MetaEventType.HEARTBEAT:
            return HeartbeatMetaEvent.model_validate(data)
        else:
            return MetaEvent.model_validate(data)
    
    else:
        return Event.model_validate(data)