"""Event models for OneBot v11 protocol.

This module provides Pydantic models for all OneBot v11 event types.
It includes base event classes and specific event types for messages,
notices, requests, and meta events.
"""

from typing import Any, Dict, List, Optional, Union, Literal, TYPE_CHECKING
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, field_validator, ConfigDict

if TYPE_CHECKING:
    from .bot import OneBotBot


class PostType(str, Enum):
    """Post type enumeration."""
    MESSAGE = "message"
    NOTICE = "notice"
    REQUEST = "request"
    META_EVENT = "meta_event"


class MessageType(str, Enum):
    """Message type enumeration."""
    PRIVATE = "private"
    GROUP = "group"


class NoticeType(str, Enum):
    """Notice type enumeration."""
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
    """Request type enumeration."""
    FRIEND = "friend"
    GROUP = "group"


class MetaEventType(str, Enum):
    """Meta event type enumeration."""
    LIFECYCLE = "lifecycle"
    HEARTBEAT = "heartbeat"


class Sender(BaseModel):
    """Message sender information."""
    
    user_id: int = Field(..., description="User ID")
    nickname: Optional[str] = Field(None, description="Nickname")
    sex: Optional[str] = Field(None, description="Gender")
    age: Optional[int] = Field(None, description="Age")
    card: Optional[str] = Field(None, description="Group card")
    area: Optional[str] = Field(None, description="Area")
    level: Optional[str] = Field(None, description="Level")
    role: Optional[str] = Field(None, description="Role in group")
    title: Optional[str] = Field(None, description="Group title")


class Anonymous(BaseModel):
    """Anonymous user information."""
    
    id: int = Field(..., description="Anonymous ID")
    name: str = Field(..., description="Anonymous name")
    flag: str = Field(..., description="Anonymous flag")


class File(BaseModel):
    """File information."""
    
    id: str = Field(..., description="File ID")
    name: str = Field(..., description="File name")
    size: int = Field(..., description="File size in bytes")
    busid: int = Field(..., description="Bus ID")


class Event(BaseModel):
    """Base event class.
    
    This is the base class for all OneBot v11 events. It contains common
    fields that are present in all event types.
    """
    
    time: datetime = Field(default_factory=datetime.now, description="Event timestamp")
    self_id: int = Field(..., description="Bot self ID")
    post_type: str = Field(..., description="Post type")
    
    model_config = ConfigDict(
        extra="allow",
        json_encoders={
            datetime: lambda v: int(v.timestamp()),
        },
    )


class MessageEvent(Event):
    """Message event.
    
    Base class for all message events. Contains common fields for both
    private and group messages.
    """
    
    post_type: str = PostType.MESSAGE
    message_type: str = Field(..., description="Message type")
    sub_type: str = Field(..., description="Message sub-type")
    message_id: int = Field(..., description="Message ID")
    user_id: int = Field(..., description="User ID")
    message: Union[str, List[Dict[str, Any]]] = Field(..., description="Message content")
    raw_message: Optional[str] = Field(None, description="Raw message content")
    font: Optional[int] = Field(None, description="Font")
    sender: Optional[Sender] = Field(None, description="Sender information")
    
    @field_validator("message", mode="before")
    def parse_message(cls, v: Union[str, List[Dict[str, Any]]]) -> Union[str, List[Dict[str, Any]]]:
        """Parse message content."""
        return v


class PrivateMessageEvent(MessageEvent):
    """Private message event."""
    
    message_type: str = MessageType.PRIVATE
    temp_source: Optional[int] = Field(None, description="Temporary message source")


class GroupMessageEvent(MessageEvent):
    """Group message event."""
    
    message_type: str = MessageType.GROUP
    group_id: int = Field(..., description="Group ID")
    anonymous: Optional[Anonymous] = Field(None, description="Anonymous information")


class NoticeEvent(Event):
    """Notice event."""
    
    post_type: str = PostType.NOTICE
    notice_type: str = Field(..., description="Notice type")


class GroupUploadNoticeEvent(NoticeEvent):
    """Group upload notice event."""
    
    notice_type: str = NoticeType.GROUP_UPLOAD
    group_id: int = Field(..., description="Group ID")
    user_id: int = Field(..., description="User ID")
    file: File = Field(..., description="File information")


class GroupAdminNoticeEvent(NoticeEvent):
    """Group admin notice event."""
    
    notice_type: str = NoticeType.GROUP_ADMIN
    sub_type: str = Field(..., description="Admin change type (set/unset)")
    group_id: int = Field(..., description="Group ID")
    user_id: int = Field(..., description="User ID")


class GroupDecreaseNoticeEvent(NoticeEvent):
    """Group member decrease notice event."""
    
    notice_type: str = NoticeType.GROUP_DECREASE
    sub_type: str = Field(..., description="Decrease type (leave/kick/kick_me)")
    group_id: int = Field(..., description="Group ID")
    operator_id: int = Field(..., description="Operator ID")
    user_id: int = Field(..., description="User ID")


class GroupIncreaseNoticeEvent(NoticeEvent):
    """Group member increase notice event."""
    
    notice_type: str = NoticeType.GROUP_INCREASE
    sub_type: str = Field(..., description="Increase type (approve/invite)")
    group_id: int = Field(..., description="Group ID")
    operator_id: int = Field(..., description="Operator ID")
    user_id: int = Field(..., description="User ID")


class GroupBanNoticeEvent(NoticeEvent):
    """Group ban notice event."""
    
    notice_type: str = NoticeType.GROUP_BAN
    sub_type: str = Field(..., description="Ban type (ban/lift_ban)")
    group_id: int = Field(..., description="Group ID")
    operator_id: int = Field(..., description="Operator ID")
    user_id: int = Field(..., description="User ID")
    duration: int = Field(..., description="Ban duration in seconds")


class FriendAddNoticeEvent(NoticeEvent):
    """Friend add notice event."""
    
    notice_type: str = NoticeType.FRIEND_ADD
    user_id: int = Field(..., description="User ID")


class GroupRecallNoticeEvent(NoticeEvent):
    """Group message recall notice event."""
    
    notice_type: str = NoticeType.GROUP_RECALL
    group_id: int = Field(..., description="Group ID")
    user_id: int = Field(..., description="User ID")
    operator_id: int = Field(..., description="Operator ID")
    message_id: int = Field(..., description="Message ID")


class FriendRecallNoticeEvent(NoticeEvent):
    """Friend message recall notice event."""
    
    notice_type: str = NoticeType.FRIEND_RECALL
    user_id: int = Field(..., description="User ID")
    message_id: int = Field(..., description="Message ID")


class NotifyNoticeEvent(NoticeEvent):
    """Notify notice event."""
    
    notice_type: str = NoticeType.NOTIFY
    sub_type: str = Field(..., description="Notify sub-type")
    group_id: int = Field(..., description="Group ID")
    user_id: int = Field(..., description="User ID")


class GroupCardNoticeEvent(NotifyNoticeEvent):
    """Group card notice event."""
    
    sub_type: str = "group_card"
    card_new: str = Field(..., description="New card")
    card_old: str = Field(..., description="Old card")


class OfflineFileNoticeEvent(NoticeEvent):
    """Offline file notice event."""
    
    notice_type: str = NoticeType.OFFLINE_FILE
    user_id: int = Field(..., description="User ID")
    file: File = Field(..., description="File information")


class EssenceNoticeEvent(NoticeEvent):
    """Essence message notice event."""
    
    notice_type: str = NoticeType.ESSENCE
    sub_type: str = Field(..., description="Essence type (add/delete)")
    group_id: int = Field(..., description="Group ID")
    sender_id: int = Field(..., description="Message sender ID")
    operator_id: int = Field(..., description="Operator ID")
    message_id: int = Field(..., description="Message ID")


class RequestEvent(Event):
    """Request event."""
    
    post_type: str = PostType.REQUEST
    request_type: str = Field(..., description="Request type")
    
    async def approve(self, bot: "OneBotBot", remark: Optional[str] = None) -> Dict[str, Any]:
        """Approve the request."""
        raise NotImplementedError
    
    async def reject(self, bot: "OneBotBot", remark: Optional[str] = None) -> Dict[str, Any]:
        """Reject the request."""
        raise NotImplementedError


class FriendRequestEvent(RequestEvent):
    """Friend request event."""
    
    request_type: str = RequestType.FRIEND
    user_id: int = Field(..., description="User ID")
    comment: str = Field(..., description="Request comment")
    flag: str = Field(..., description="Request flag")
    
    async def approve(self, bot: "OneBotBot", remark: Optional[str] = None) -> Dict[str, Any]:
        """Approve friend request."""
        return await bot.set_friend_add_request(
            flag=self.flag,
            approve=True,
            remark=remark or ""
        )
    
    async def reject(self, bot: "OneBotBot", remark: Optional[str] = None) -> Dict[str, Any]:
        """Reject friend request."""
        return await bot.set_friend_add_request(
            flag=self.flag,
            approve=False,
            remark=remark or ""
        )


class GroupRequestEvent(RequestEvent):
    """Group request event."""
    
    request_type: str = RequestType.GROUP
    sub_type: str = Field(..., description="Request sub-type (add/invite)")
    group_id: int = Field(..., description="Group ID")
    user_id: int = Field(..., description="User ID")
    comment: str = Field(..., description="Request comment")
    flag: str = Field(..., description="Request flag")
    
    async def approve(self, bot: "OneBotBot", remark: Optional[str] = None) -> Dict[str, Any]:
        """Approve group request."""
        return await bot.set_group_add_request(
            flag=self.flag,
            sub_type=self.sub_type,
            approve=True,
            reason=remark or ""
        )
    
    async def reject(self, bot: "OneBotBot", remark: Optional[str] = None) -> Dict[str, Any]:
        """Reject group request."""
        return await bot.set_group_add_request(
            flag=self.flag,
            sub_type=self.sub_type,
            approve=False,
            reason=remark or ""
        )


class MetaEvent(Event):
    """Meta event."""
    
    post_type: str = PostType.META_EVENT
    meta_event_type: str = Field(..., description="Meta event type")


class LifecycleMetaEvent(MetaEvent):
    """Lifecycle meta event."""
    
    meta_event_type: str = MetaEventType.LIFECYCLE
    sub_type: str = Field(..., description="Lifecycle sub-type (enable/disable/connect)")


class HeartbeatMetaEvent(MetaEvent):
    """Heartbeat meta event."""
    
    meta_event_type: str = MetaEventType.HEARTBEAT
    status: Dict[str, Any] = Field(..., description="Bot status")
    interval: int = Field(..., description="Heartbeat interval in milliseconds")


def parse_event(data: Dict[str, Any]) -> Event:
    """Parse event from raw data."""
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