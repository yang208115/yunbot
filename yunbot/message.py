"""Message models for OneBot v11 protocol."""

from typing import Any, Dict, List, Optional, Union, Iterator
import re
from pydantic import BaseModel, Field, RootModel


class MessageSegment(BaseModel):
    """Message segment model for OneBot v11 protocol.
    
    Represents a single segment of a message, which can be text, image, or other types.
    Each segment has a type and associated data.
    
    Attributes:
        type: Segment type (e.g., "text", "image", "at")
        data: Segment data containing type-specific parameters
    """
    
    type: str = Field(..., description="Segment type")
    data: Dict[str, Any] = Field(default_factory=dict, description="Segment data")
    
    @classmethod
    def text(cls, text: str) -> "MessageSegment":
        """Create a text segment.
        
        Args:
            text: The text content
            
        Returns:
            MessageSegment: A text message segment
        """
        return cls(type="text", data={"text": text})
    
    @classmethod
    def face(cls, id: int) -> "MessageSegment":
        """Create a face segment.
        
        Args:
            id: Face ID
            
        Returns:
            MessageSegment: A face message segment
        """
        return cls(type="face", data={"id": id})
    
    @classmethod
    def image(
        cls,
        file: str,
        type: Optional[str] = None,
        url: Optional[str] = None,
        cache: Optional[bool] = None,
        proxy: Optional[bool] = None,
        timeout: Optional[int] = None,
    ) -> "MessageSegment":
        """Create an image segment.
        
        Args:
            file: Image file path or URL
            type: Image type (optional)
            url: Image URL (optional)
            cache: Whether to cache the image (optional)
            proxy: Whether to use proxy (optional)
            timeout: Timeout in seconds (optional)
            
        Returns:
            MessageSegment: An image message segment
        """
        data: Dict[str, Any] = {"file": file}
        if type is not None:
            data["type"] = type
        if url is not None:
            data["url"] = url
        if cache is not None:
            data["cache"] = cache
        if proxy is not None:
            data["proxy"] = proxy
        if timeout is not None:
            data["timeout"] = timeout
        return cls(type="image", data=data)
    
    @classmethod
    def record(
        cls,
        file: str,
        magic: Optional[bool] = None,
        cache: Optional[bool] = None,
        proxy: Optional[bool] = None,
        timeout: Optional[int] = None,
    ) -> "MessageSegment":
        """Create a record segment (voice message).
        
        Args:
            file: Audio file path or URL
            magic: Whether to use magic conversion (optional)
            cache: Whether to cache the audio (optional)
            proxy: Whether to use proxy (optional)
            timeout: Timeout in seconds (optional)
            
        Returns:
            MessageSegment: A record message segment
        """
        data: Dict[str, Any] = {"file": file}
        if magic is not None:
            data["magic"] = magic
        if cache is not None:
            data["cache"] = cache
        if proxy is not None:
            data["proxy"] = proxy
        if timeout is not None:
            data["timeout"] = timeout
        return cls(type="record", data=data)
    
    @classmethod
    def video(
        cls,
        file: str,
        cache: Optional[bool] = None,
        proxy: Optional[bool] = None,
        timeout: Optional[int] = None,
    ) -> "MessageSegment":
        """Create a video segment.
        
        Args:
            file: Video file path or URL
            cache: Whether to cache the video (optional)
            proxy: Whether to use proxy (optional)
            timeout: Timeout in seconds (optional)
            
        Returns:
            MessageSegment: A video message segment
        """
        data: Dict[str, Any] = {"file": file}
        if cache is not None:
            data["cache"] = cache
        if proxy is not None:
            data["proxy"] = proxy
        if timeout is not None:
            data["timeout"] = timeout
        return cls(type="video", data=data)
    
    @classmethod
    def at(cls, qq: Union[int, str]) -> "MessageSegment":
        """Create an @ segment.
        
        Args:
            qq: QQ number to @
            
        Returns:
            MessageSegment: An @ message segment
        """
        return cls(type="at", data={"qq": str(qq)})
    
    @classmethod
    def at_all(cls, channel: Optional[str] = None) -> "MessageSegment":
        """Create an @all segment.
        
        Args:
            channel: Channel name (optional)
            
        Returns:
            MessageSegment: An @all message segment
        """
        data = {"qq": "all"}
        if channel is not None:
            data["channel"] = channel
        return cls(type="at", data=data)
    
    @classmethod
    def rps(cls, type_: Optional[str] = None) -> "MessageSegment":
        """Create a rock-paper-scissors segment.
        
        Args:
            type_: RPS type (optional)
            
        Returns:
            MessageSegment: A rock-paper-scissors message segment
        """
        data = {}
        if type_ is not None:
            data["type"] = type_
        return cls(type="rps", data=data)
    
    @classmethod
    def dice(cls, type_: Optional[str] = None) -> "MessageSegment":
        """Create a dice segment.
        
        Args:
            type_: Dice type (optional)
            
        Returns:
            MessageSegment: A dice message segment
        """
        data = {}
        if type_ is not None:
            data["type"] = type_
        return cls(type="dice", data=data)
    
    @classmethod
    def shake(cls) -> "MessageSegment":
        """Create a shake segment (window shake).
        
        Returns:
            MessageSegment: A shake message segment
        """
        return cls(type="shake", data={})
    
    @classmethod
    def poke(cls, type_: str, id_: str) -> "MessageSegment":
        """Create a poke segment.
        
        Args:
            type_: Poke type
            id_: Poke ID
            
        Returns:
            MessageSegment: A poke message segment
        """
        return cls(type="poke", data={"type": type_, "id": id_})
    
    @classmethod
    def anonymous(cls, ignore: Optional[bool] = None) -> "MessageSegment":
        """Create an anonymous segment.
        
        Args:
            ignore: Whether to ignore anonymous check (optional)
            
        Returns:
            MessageSegment: An anonymous message segment
        """
        data = {}
        if ignore is not None:
            data["ignore"] = ignore
        return cls(type="anonymous", data=data)
    
    @classmethod
    def share(
        cls,
        url: str,
        title: str,
        content: Optional[str] = None,
        image: Optional[str] = None,
    ) -> "MessageSegment":
        """Create a share segment.
        
        Args:
            url: URL to share
            title: Share title
            content: Share content (optional)
            image: Image URL (optional)
            
        Returns:
            MessageSegment: A share message segment
        """
        data = {"url": url, "title": title}
        if content is not None:
            data["content"] = content
        if image is not None:
            data["image"] = image
        return cls(type="share", data=data)
    
    @classmethod
    def contact(
        cls, 
        type_: str, 
        id_: Union[int, str]
    ) -> "MessageSegment":
        """Create a contact segment.
        
        Args:
            type_: Contact type
            id_: Contact ID
            
        Returns:
            MessageSegment: A contact message segment
        """
        return cls(type="contact", data={"type": type_, "id": str(id_)})
    
    @classmethod
    def location(
        cls,
        lat: float,
        lon: float,
        title: Optional[str] = None,
        content: Optional[str] = None,
    ) -> "MessageSegment":
        """Create a location segment.
        
        Args:
            lat: Latitude
            lon: Longitude
            title: Location title (optional)
            content: Location content (optional)
            
        Returns:
            MessageSegment: A location message segment
        """
        data: Dict[str, Any] = {"lat": lat, "lon": lon}
        if title is not None:
            data["title"] = title
        if content is not None:
            data["content"] = content
        return cls(type="location", data=data)
    
    @classmethod
    def music(
        cls,
        type_: str,
        id_: Optional[str] = None,
        url: Optional[str] = None,
        audio: Optional[str] = None,
        title: Optional[str] = None,
        content: Optional[str] = None,
        image: Optional[str] = None,
    ) -> "MessageSegment":
        """Create a music segment.
        
        Args:
            type_: Music type
            id_: Music ID (optional)
            url: Music URL (optional)
            audio: Audio URL (optional)
            title: Music title (optional)
            content: Music content (optional)
            image: Image URL (optional)
            
        Returns:
            MessageSegment: A music message segment
        """
        data: Dict[str, Any] = {"type": type_}
        if id_ is not None:
            data["id"] = id_
        if url is not None:
            data["url"] = url
        if audio is not None:
            data["audio"] = audio
        if title is not None:
            data["title"] = title
        if content is not None:
            data["content"] = content
        if image is not None:
            data["image"] = image
        return cls(type="music", data=data)
    
    @classmethod
    def reply(cls, id_: int) -> "MessageSegment":
        """Create a reply segment.
        
        Args:
            id_: Message ID to reply to
            
        Returns:
            MessageSegment: A reply message segment
        """
        return cls(type="reply", data={"id": id_})
    
    @classmethod
    def forward(cls, id_: str) -> "MessageSegment":
        """Create a forward segment.
        
        Args:
            id_: Forward ID
            
        Returns:
            MessageSegment: A forward message segment
        """
        return cls(type="forward", data={"id": id_})
    
    @classmethod
    def node(
        cls,
        id_: Optional[int] = None,
        name: Optional[str] = None,
        uin: Optional[int] = None,
        content: Optional[Union[str, List["MessageSegment"]]] = None,
        seq: Optional[str] = None,
    ) -> "MessageSegment":
        """Create a node segment.
        
        Args:
            id_: Node ID (optional)
            name: Node name (optional)
            uin: User ID (optional)
            content: Node content (optional)
            seq: Sequence (optional)
            
        Returns:
            MessageSegment: A node message segment
        """
        data = {}
        if id_ is not None:
            data["id"] = id_
        if name is not None:
            data["name"] = name
        if uin is not None:
            data["uin"] = uin
        if content is not None:
            if isinstance(content, str):
                data["content"] = content
            else:
                data["content"] = [seg.model_dump() for seg in content]
        if seq is not None:
            data["seq"] = seq
        return cls(type="node", data=data)
    
    @classmethod
    def xml(cls, data: str) -> "MessageSegment":
        """Create an XML segment.
        
        Args:
            data: XML data string
            
        Returns:
            MessageSegment: An XML message segment
        """
        return cls(type="xml", data={"data": data})
    
    @classmethod
    def json_data(cls, data: str) -> "MessageSegment":
        """Create a JSON segment.
        
        Args:
            data: JSON data string
            
        Returns:
            MessageSegment: A JSON message segment
        """
        return cls(type="json", data={"data": data})


class Message(RootModel[List[MessageSegment]]):
    """Message model for OneBot v11 protocol.
    
    Represents a complete message composed of multiple segments.
    Provides methods for manipulating and processing message segments.
    """
    
    def __init__(self, message: Union[str, List[MessageSegment], List[Dict[str, Any]]]) -> None:
        """Initialize message.
        
        Args:
            message: Message content, can be string, list of segments, or list of dictionaries
            
        Raises:
            ValueError: When message format is invalid
        """
        segments: List[MessageSegment]
        if isinstance(message, str):
            segments = self._parse_cq_code(message)
        elif isinstance(message, list):
            # 使用 isinstance 检查第一个元素来确定列表类型
            if len(message) > 0:
                if isinstance(message[0], MessageSegment):
                    segments = message  # type: ignore
                elif isinstance(message[0], dict):
                    segments = [MessageSegment.model_validate(seg) for seg in message]  # type: ignore
                else:
                    raise ValueError("Invalid message format")
            else:
                segments = []
        else:
            raise ValueError("Invalid message format")

        super().__init__(root=segments)
    
    def __str__(self) -> str:
        """Convert message to string representation.
        
        Returns:
            str: Plain text representation of the message
        """
        return self.extract_plain_text()
    
    def __len__(self) -> int:
        """Get message length (number of segments).
        
        Returns:
            int: Number of segments in the message
        """
        return len(self.root)
    
    def __getitem__(self, index: int) -> MessageSegment:
        """Get segment by index.
        
        Args:
            index: Segment index
            
        Returns:
            MessageSegment: Message segment at the specified index
        """
        return self.root[index]
    
    def __setitem__(self, index: int, value: Union[MessageSegment, Dict[str, Any]]) -> None:
        """Set segment by index.
        
        Args:
            index: Segment index
            value: New message segment or dictionary representation
        """
        if isinstance(value, dict):
            value = MessageSegment.model_validate(value)
        self.root[index] = value
    
    def __delitem__(self, index: int) -> None:
        """Delete segment by index.
        
        Args:
            index: Segment index to delete
        """
        del self.root[index]
    
    def segments(self) -> Iterator[MessageSegment]:
        """Iterate over segments.
        
        Returns:
            Iterator[MessageSegment]: Iterator over message segments
        """
        return iter(self.root)
    
    def __contains__(self, item: str) -> bool:
        """Check if message contains text.
        
        Args:
            item: Text to search for
            
        Returns:
            bool: True if message contains the text, False otherwise
        """
        return item in self.extract_plain_text()
    
    def append(self, segment: MessageSegment) -> None:
        """Append a segment to the message.
        
        Args:
            segment: Message segment to append
        """
        self.root.append(segment)
    
    def extend(self, segments: List[MessageSegment]) -> None:
        """Extend message with multiple segments.
        
        Args:
            segments: List of message segments to extend with
        """
        self.root.extend(segments)
    
    def insert(self, index: int, segment: MessageSegment) -> None:
        """Insert a segment at specific index.
        
        Args:
            index: Position to insert at
            segment: Message segment to insert
        """
        self.root.insert(index, segment)
    
    def remove(self, segment: MessageSegment) -> None:
        """Remove a segment from the message.
        
        Args:
            segment: Message segment to remove
        """
        self.root.remove(segment)
    
    def pop(self, index: int = -1) -> MessageSegment:
        """Pop a segment from the message.
        
        Args:
            index: Index of segment to pop (default: last segment)
            
        Returns:
            MessageSegment: Popped message segment
        """
        return self.root.pop(index)
    
    def clear(self) -> None:
        """Clear all segments from the message."""
        self.root.clear()
    
    def index(self, segment: MessageSegment) -> int:
        """Get index of a segment.
        
        Args:
            segment: Message segment to find
            
        Returns:
            int: Index of the segment
        """
        return self.root.index(segment)
    
    def count(self, segment: MessageSegment) -> int:
        """Count occurrences of a segment.
        
        Args:
            segment: Message segment to count
            
        Returns:
            int: Number of occurrences
        """
        return self.root.count(segment)
    
    def extract_plain_text(self) -> str:
        """Extract plain text from message.
        
        Returns:
            str: Plain text content of all text segments
        """
        text = ""
        for segment in self.root:
            if segment.type == "text":
                text += segment.data.get("text", "")
        return text
    
    def get_segments(self, segment_type: str) -> List[MessageSegment]:
        """Get segments by type.
        
        Args:
            segment_type: Type of segments to retrieve
            
        Returns:
            List[MessageSegment]: List of segments of the specified type
        """
        return [seg for seg in self.root if seg.type == segment_type]
    
    def has_segment(self, segment_type: str) -> bool:
        """Check if message has segment of specific type.
        
        Args:
            segment_type: Segment type to check for
            
        Returns:
            bool: True if message contains segments of the specified type, False otherwise
        """
        return any(seg.type == segment_type for seg in self.root)
    
    def is_text_only(self) -> bool:
        """Check if message contains only text segments.
        
        Returns:
            bool: True if all segments are text segments, False otherwise
        """
        return all(seg.type == "text" for seg in self.root)
    
    def to_dict(self) -> List[Dict[str, Any]]:
        """Convert message to dictionary representation.
        
        Returns:
            List[Dict[str, Any]]: List of segment dictionaries
        """
        return [seg.model_dump() for seg in self.root]
    
    @classmethod
    def from_dict(cls, data: List[Dict[str, Any]]) -> "Message":
        """Create message from dictionary representation.
        
        Args:
            data: List of segment dictionaries
            
        Returns:
            Message: New message instance
        """
        segments = [MessageSegment.model_validate(seg) for seg in data]
        return cls(segments)
    
    @classmethod
    def from_str(cls, text: str) -> "Message":
        """Create message from string.
        
        Args:
            text: String representation of the message
            
        Returns:
            Message: New message instance
        """
        return cls(text)

    @staticmethod
    def _parse_cq_code(message: str) -> List[MessageSegment]:
        """解析包含CQ码的消息字符串
        
        Args:
            message: 包含CQ码的消息字符串
            
        Returns:
            List[MessageSegment]: 解析后的消息段列表
        """
        segments = []

        # CQ码正则表达式匹配 [CQ:类型,参数=値,パラメータ=値]
        cq_pattern = re.compile(r'\[CQ:([^,\]]+)((?:,[^,=]+=[^,\]]*)*)\]')

        last_end = 0

        for match in cq_pattern.finditer(message):
            # 添加CQ码之前的普通文本
            if match.start() > last_end:
                plain_text = message[last_end:match.start()]
                if plain_text:
                    segments.append(MessageSegment.text(plain_text))

            # 解析CQ码
            cq_type = match.group(1)
            params_str = match.group(2)

            # 解析参数
            data = {}
            if params_str:
                # 去掉开头的逗号，然后按逗号分割
                param_pairs = params_str[1:].split(',')
                for pair in param_pairs:
                    if '=' in pair:
                        key, value = pair.split('=', 1)
                        data[key] = value

            segments.append(MessageSegment(type=cq_type, data=data))
            last_end = match.end()

        # 添加最后的普通文本
        if last_end < len(message):
            plain_text = message[last_end:]
            if plain_text:
                segments.append(MessageSegment.text(plain_text))

        # 如果没有找到任何CQ码，整个消息作为普通文本
        if not segments:
            segments.append(MessageSegment.text(message))

        return segments