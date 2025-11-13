"""OneBot v11 协议的消息模型。"""

from typing import Any, Dict, List, Optional, Union, Iterator
import re
from pydantic import BaseModel, Field, RootModel


class MessageSegment(BaseModel):
    """OneBot v11 协议的消息段模型。
    
    表示消息的单个段，可以是文本、图像或其他类型。
    每个段都有一个类型和相关数据。
    
    属性:
        type: 消息段类型 (例如 "text", "image", "at")
        data: 消息段数据，包含类型特定的参数
    """
    
    type: str = Field(..., description="消息段类型")
    data: Dict[str, Any] = Field(default_factory=dict, description="消息段数据")
    
    @classmethod
    def text(cls, text: str) -> "MessageSegment":
        """创建一个文本段。
        
        参数:
            text: 文本内容
            
        返回:
            MessageSegment: 文本消息段
        """
        return cls(type="text", data={"text": text})
    
    @classmethod
    def face(cls, id: int) -> "MessageSegment":
        """创建一个表情段。
        
        参数:
            id: 表情 ID
            
        返回:
            MessageSegment: 表情消息段
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
        """创建一个图片段。
        
        参数:
            file: 图片文件路径或 URL
            type: 图片类型 (可选)
            url: 图片 URL (可选)
            cache: 是否缓存图片 (可选)
            proxy: 是否使用代理 (可选)
            timeout: 超时时间（秒） (可选)
            
        返回:
            MessageSegment: 图片消息段
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
        """创建一个录音段（语音消息）。
        
        参数:
            file: 音频文件路径或 URL
            magic: 是否使用魔法转换 (可选)
            cache: 是否缓存音频 (可选)
            proxy: 是否使用代理 (可选)
            timeout: 超时时间（秒） (可选)
            
        返回:
            MessageSegment: 录音消息段
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
        """创建一个视频段。
        
        参数:
            file: 视频文件路径或 URL
            cache: 是否缓存视频 (可选)
            proxy: 是否使用代理 (可选)
            timeout: 超时时间（秒） (可选)
            
        返回:
            MessageSegment: 视频消息段
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
        """创建一个 @ 段。
        
        参数:
            qq: 要 @ 的 QQ 号
            
        返回:
            MessageSegment: @ 消息段
        """
        return cls(type="at", data={"qq": str(qq)})
    
    @classmethod
    def at_all(cls, channel: Optional[str] = None) -> "MessageSegment":
        """创建一个 @全体成员 段。
        
        参数:
            channel: 频道名称 (可选)
            
        返回:
            MessageSegment: @全体成员 消息段
        """
        data = {"qq": "all"}
        if channel is not None:
            data["channel"] = channel
        return cls(type="at", data=data)
    
    @classmethod
    def rps(cls, type_: Optional[str] = None) -> "MessageSegment":
        """创建一个猜拳段。
        
        参数:
            type_: 猜拳类型 (可选)
            
        返回:
            MessageSegment: 猜拳消息段
        """
        data = {}
        if type_ is not None:
            data["type"] = type_
        return cls(type="rps", data=data)
    
    @classmethod
    def dice(cls, type_: Optional[str] = None) -> "MessageSegment":
        """创建一个骰子段。
        
        参数:
            type_: 骰子类型 (可选)
            
        返回:
            MessageSegment: 骰子消息段
        """
        data = {}
        if type_ is not None:
            data["type"] = type_
        return cls(type="dice", data=data)
    
    @classmethod
    def shake(cls) -> "MessageSegment":
        """创建一个窗口抖动段。
        
        返回:
            MessageSegment: 窗口抖动消息段
        """
        return cls(type="shake", data={})
    
    @classmethod
    def poke(cls, type_: str, id_: str) -> "MessageSegment":
        """创建一个戳一戳段。
        
        参数:
            type_: 戳一戳类型
            id_: 戳一戳 ID
            
        返回:
            MessageSegment: 戳一戳消息段
        """
        return cls(type="poke", data={"type": type_, "id": id_})
    
    @classmethod
    def anonymous(cls, ignore: Optional[bool] = None) -> "MessageSegment":
        """创建一个匿名段。
        
        参数:
            ignore: 是否忽略匿名检查 (可选)
            
        返回:
            MessageSegment: 匿名消息段
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
        """创建一个分享段。
        
        参数:
            url: 分享的 URL
            title: 分享标题
            content: 分享内容 (可选)
            image: 图片 URL (可选)
            
        返回:
            MessageSegment: 分享消息段
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
        """创建一个联系人段。
        
        参数:
            type_: 联系人类型
            id_: 联系人 ID
            
        返回:
            MessageSegment: 联系人消息段
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
        """创建一个位置段。
        
        参数:
            lat: 纬度
            lon: 经度
            title: 位置标题 (可选)
            content: 位置内容 (可选)
            
        返回:
            MessageSegment: 位置消息段
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
        """创建一个音乐段。
        
        参数:
            type_: 音乐类型
            id_: 音乐 ID (可选)
            url: 音乐 URL (可选)
            audio: 音频 URL (可选)
            title: 音乐标题 (可选)
            content: 音乐内容 (可选)
            image: 图片 URL (可选)
            
        返回:
            MessageSegment: 音乐消息段
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
        """创建一个回复段。
        
        参数:
            id_: 要回复的消息 ID
            
        返回:
            MessageSegment: 回复消息段
        """
        return cls(type="reply", data={"id": id_})
    
    @classmethod
    def forward(cls, id_: str) -> "MessageSegment":
        """创建一个转发段。
        
        参数:
            id_: 转发 ID
            
        返回:
            MessageSegment: 转发消息段
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
        """创建一个节点段。
        
        参数:
            id_: 节点 ID (可选)
            name: 节点名称 (可选)
            uin: 用户 ID (可选)
            content: 节点内容 (可选)
            seq: 序列 (可选)
            
        返回:
            MessageSegment: 节点消息段
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
        """创建一个 XML 段。
        
        参数:
            data: XML 数据字符串
            
        返回:
            MessageSegment: XML 消息段
        """
        return cls(type="xml", data={"data": data})
    
    @classmethod
    def json_data(cls, data: str) -> "MessageSegment":
        """创建一个 JSON 段。
        
        参数:
            data: JSON 数据字符串
            
        返回:
            MessageSegment: JSON 消息段
        """
        return cls(type="json", data={"data": data})


class Message(RootModel[List[MessageSegment]]):
    """OneBot v11 协议的消息模型。
    
    表示由多个段组成的完整消息。
    提供操作和处理消息段的方法。
    """
    
    def __init__(self, message: Union[str, List[MessageSegment], List[Dict[str, Any]]]) -> None:
        """初始化消息。
        
        参数:
            message: 消息内容，可以是字符串、段列表或字典列表
            
        异常:
            ValueError: 当消息格式无效时
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
        """将消息转换为字符串表示。
        
        返回:
            str: 消息的纯文本表示
        """
        return self.extract_plain_text()
    
    def __len__(self) -> int:
        """获取消息长度（段数）。
        
        返回:
            int: 消息中的段数
        """
        return len(self.root)
    
    def __getitem__(self, index: int) -> MessageSegment:
        """按索引获取段。
        
        参数:
            index: 段索引
            
        返回:
            MessageSegment: 指定索引处的消息段
        """
        return self.root[index]
    
    def __setitem__(self, index: int, value: Union[MessageSegment, Dict[str, Any]]) -> None:
        """按索引设置段。
        
        参数:
            index: 段索引
            value: 新的消息段或字典表示
        """
        if isinstance(value, dict):
            value = MessageSegment.model_validate(value)
        self.root[index] = value
    
    def __delitem__(self, index: int) -> None:
        """按索引删除段。
        
        参数:
            index: 要删除的段索引
        """
        del self.root[index]
    
    def segments(self) -> Iterator[MessageSegment]:
        """遍历段。
        
        返回:
            Iterator[MessageSegment]: 消息段的迭代器
        """
        return iter(self.root)
    
    def __contains__(self, item: str) -> bool:
        """检查消息是否包含文本。
        
        参数:
            item: 要搜索的文本
            
        返回:
            bool: 如果消息包含文本则返回 True，否则返回 False
        """
        return item in self.extract_plain_text()
    
    def append(self, segment: MessageSegment) -> None:
        """向消息追加一个段。
        
        参数:
            segment: 要追加的消息段
        """
        self.root.append(segment)
    
    def extend(self, segments: List[MessageSegment]) -> None:
        """用多个段扩展消息。
        
        参数:
            segments: 要扩展的消息段列表
        """
        self.root.extend(segments)
    
    def insert(self, index: int, segment: MessageSegment) -> None:
        """在指定索引处插入一个段。
        
        参数:
            index: 要插入的位置
            segment: 要插入的消息段
        """
        self.root.insert(index, segment)
    
    def remove(self, segment: MessageSegment) -> None:
        """从消息中删除一个段。
        
        参数:
            segment: 要删除的消息段
        """
        self.root.remove(segment)
    
    def pop(self, index: int = -1) -> MessageSegment:
        """从消息中弹出一个段。
        
        参数:
            index: 要弹出的段索引（默认：最后一个段）
            
        返回:
            MessageSegment: 弹出的消息段
        """
        return self.root.pop(index)
    
    def clear(self) -> None:
        """清除消息中的所有段。"""
        self.root.clear()
    
    def index(self, segment: MessageSegment) -> int:
        """获取段的索引。
        
        参数:
            segment: 要查找的消息段
            
        返回:
            int: 段的索引
        """
        return self.root.index(segment)
    
    def count(self, segment: MessageSegment) -> int:
        """计算段的出现次数。
        
        参数:
            segment: 要计数的消息段
            
        返回:
            int: 出现次数
        """
        return self.root.count(segment)
    
    def extract_plain_text(self) -> str:
        """从消息中提取纯文本。
        
        返回:
            str: 所有文本段的纯文本内容
        """
        text = ""
        for segment in self.root:
            if segment.type == "text":
                text += segment.data.get("text", "")
        return text
    
    def get_segments(self, segment_type: str) -> List[MessageSegment]:
        """按类型获取段。
        
        参数:
            segment_type: 要检索的段类型
            
        返回:
            List[MessageSegment]: 指定类型的段列表
        """
        return [seg for seg in self.root if seg.type == segment_type]
    
    def has_segment(self, segment_type: str) -> bool:
        """检查消息是否包含特定类型的段。
        
        参数:
            segment_type: 要检查的段类型
            
        返回:
            bool: 如果消息包含指定类型的段则返回 True，否则返回 False
        """
        return any(seg.type == segment_type for seg in self.root)
    
    def is_text_only(self) -> bool:
        """检查消息是否仅包含文本段。
        
        返回:
            bool: 如果所有段都是文本段则返回 True，否则返回 False
        """
        return all(seg.type == "text" for seg in self.root)
    
    def to_dict(self) -> List[Dict[str, Any]]:
        """将消息转换为字典表示。
        
        返回:
            List[Dict[str, Any]]: 段字典的列表
        """
        return [seg.model_dump() for seg in self.root]
    
    @classmethod
    def from_dict(cls, data: List[Dict[str, Any]]) -> "Message":
        """从字典表示创建消息。
        
        参数:
            data: 段字典的列表
            
        返回:
            Message: 新的消息实例
        """
        segments = [MessageSegment.model_validate(seg) for seg in data]
        return cls(segments)
    
    @classmethod
    def from_str(cls, text: str) -> "Message":
        """从字符串创建消息。
        
        参数:
            text: 消息的字符串表示
            
        返回:
            Message: 新的消息实例
        """
        return cls(text)

    @staticmethod
    def _parse_cq_code(message: str) -> List[MessageSegment]:
        """解析包含CQ码的消息字符串
        
        参数:
            message: 包含CQ码的消息字符串
            
        返回:
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