"""OneBot v11 客户端适配器的配置模块。

该模块提供 Pydantic 模型用于配置 OneBot v11 客户端。
它包含不同连接类型的模型和主要配置。
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Union, Literal
from pydantic import BaseModel, Field, field_validator, ConfigDict

try:
    import yaml  # type: ignore
    YAML_AVAILABLE = True
except ImportError:
    yaml = None  # type: ignore
    YAML_AVAILABLE = False


class ConnectionConfig(BaseModel):
    """基础连接配置。"""
    
    type: str = Field(..., description="连接类型")
    self_id: Optional[str] = Field(None, description="机器人自身 ID")
    access_token: Optional[str] = Field(None, description="用于身份验证的访问令牌")
    secret: Optional[str] = Field(None, description="Webhook 签名密钥")
    timeout: float = Field(30.0, description="请求超时时间（秒）")
    retry_times: int = Field(3, description="失败请求的重试次数")
    retry_interval: float = Field(1.0, description="重试间隔（秒）")
    
    model_config = ConfigDict(extra="ignore")


class HttpConfig(ConnectionConfig):
    """HTTP 连接配置。
    
    用于 OneBot v11 API 的 HTTP 连接配置。
    """
    
    type: str = "http"
    base_url: str = Field(..., description="HTTP API 的基础 URL")
    heartbeat_interval: Optional[float] = Field(None, description="心跳间隔（秒）")
    
    @field_validator("base_url")
    def validate_base_url(cls, v: str) -> str:
        """验证基础 URL 格式。
        
        Args:
            v: 要验证的基础 URL 字符串
            
        Returns:
            str: 验证并去除末尾斜杠的基础 URL
            
        Raises:
            ValueError: 如果 URL 不以 http:// 或 https:// 开头
        """
        if not v.startswith(("http://", "https://")):
            raise ValueError("base_url 必须以 http:// 或 https:// 开头")
        return v.rstrip("/")


class WebSocketConfig(ConnectionConfig):
    """WebSocket 连接配置。
    
    用于 OneBot v11 API 的 WebSocket 连接配置。
    """
    
    type: str = "websocket"
    url: str = Field(..., description="WebSocket URL")
    heartbeat_interval: Optional[float] = Field(None, description="心跳间隔（秒）")
    
    @field_validator("url")
    def validate_url(cls, v: str) -> str:
        """验证 WebSocket URL 格式。
        
        Args:
            v: 要验证的 WebSocket URL 字符串
            
        Returns:
            str: 验证后的 URL
            
        Raises:
            ValueError: 如果 URL 不以 ws:// 或 wss:// 开头
        """
        if not v.startswith(("ws://", "wss://")):
            raise ValueError("url 必须以 ws:// 或 wss:// 开头")
        return v


class ReverseWebSocketConfig(ConnectionConfig):
    """反向 WebSocket 连接配置。
    
    客户端作为服务器的反向 WebSocket 连接配置。
    """
    
    type: str = "reverse_ws"
    host: str = Field(default="127.0.0.1", description="监听的主机")
    port: int = Field(..., description="监听的端口")
    path: str = Field(default="/onebot/v11/ws", description="WebSocket 路径")
    heartbeat_interval: Optional[float] = Field(None, description="心跳间隔（秒）")
    
    @field_validator("port")
    def validate_port(cls, v: int) -> int:
        """验证端口号范围。
        
        Args:
            v: 要验证的端口号
            
        Returns:
            int: 验证后的端口号
            
        Raises:
            ValueError: 如果端口号不在 1 到 65535 之间
        """
        if not (1 <= v <= 65535):
            raise ValueError("端口必须在 1 到 65535 之间")
        return v


class WebhookConfig(ConnectionConfig):
    """Webhook 连接配置。
    
    客户端接收 HTTP POST 请求的 Webhook 连接配置。
    """
    
    type: str = "webhook"
    host: str = Field(default="127.0.0.1", description="监听的主机")
    port: int = Field(..., description="监听的端口")
    path: str = Field(default="/onebot/v11/webhook", description="Webhook 路径")
    heartbeat_interval: Optional[float] = Field(None, description="心跳间隔（秒）")
    
    @field_validator("port")
    def validate_port(cls, v: int) -> int:
        """验证端口号范围。
        
        Args:
            v: 要验证的端口号
            
        Returns:
            int: 验证后的端口号
            
        Raises:
            ValueError: 如果端口号不在 1 到 65535 之间
        """
        if not (1 <= v <= 65535):
            raise ValueError("端口必须在 1 到 65535 之间")
        return v


ConnectionTypes = Union[HttpConfig, WebSocketConfig, ReverseWebSocketConfig, WebhookConfig]


class Config(BaseModel):
    """主要配置类。
    
    包含所有连接配置和 OneBot v11 客户端全局设置的主要配置类。
    """
    
    connections: List[ConnectionTypes] = Field(
        default_factory=list, 
        description="连接配置列表"
    )
    api_timeout: float = Field(30.0, description="API 调用超时时间（秒）")
    max_concurrent_requests: int = Field(100, description="最大并发 API 请求数")
    enable_heartbeat: bool = Field(True, description="为 WebSocket 连接启用心跳")
    heartbeat_interval: float = Field(30.0, description="默认心跳间隔（秒）")
    reconnect_interval: float = Field(5.0, description="重连间隔（秒）")
    max_reconnect_attempts: int = Field(10, description="最大重连尝试次数")
    
    @field_validator("connections")
    def validate_connections(cls, v: List[ConnectionTypes]) -> List[ConnectionTypes]:
        """验证至少配置了一个连接。
        
        Args:
            v: 连接配置列表
            
        Returns:
            List[ConnectionTypes]: 验证后的连接列表
            
        Raises:
            ValueError: 如果未配置任何连接
        """
        if not v:
            raise ValueError("至少需要配置一个连接")
        return v
    
    def get_connection_by_type(self, connection_type: str) -> Optional[ConnectionTypes]:
        """根据类型获取连接配置。
        
        Args:
            connection_type: 要查找的连接类型
            
        Returns:
            Optional[ConnectionTypes]: 如果找到则返回连接配置，否则返回 None
        """
        for conn in self.connections:
            if conn.type == connection_type:
                return conn
        return None
    
    def get_connections_by_types(self, *types: str) -> List[ConnectionTypes]:
        """根据类型获取连接配置。
        
        Args:
            *types: 要筛选的连接类型
            
        Returns:
            List[ConnectionTypes]: 匹配的连接配置列表
        """
        return [conn for conn in self.connections if conn.type in types]
    
    @classmethod
    def from_file(cls, path: Union[str, Path], encoding: str = "utf-8") -> "Config":
        """从文件加载配置。
        
        支持 JSON 和 YAML 格式,根据文件扩展名自动识别。
        加载后会应用环境变量覆盖(以 YUNBOT_ 为前缀)。
        
        Args:
            path: 配置文件路径
            encoding: 文件编码,默认为 utf-8
            
        Returns:
            Config: 配置实例
            
        Raises:
            FileNotFoundError: 如果文件不存在
            ValueError: 如果文件格式不支持或解析失败
            ImportError: 如果 YAML 文件需要 PyYAML 但未安装
            
        Examples:
            >>> config = Config.from_file("config.json")
            >>> config = Config.from_file("config.yaml")
        """
        path = Path(path)
        
        if not path.exists():
            raise FileNotFoundError(f"配置文件不存在: {path}")
        
        # 读取文件内容
        content = path.read_text(encoding=encoding)
        
        # 根据扩展名解析
        suffix = path.suffix.lower()
        
        if suffix == ".json":
            data = json.loads(content)
        elif suffix in (".yaml", ".yml"):
            if not YAML_AVAILABLE:
                raise ImportError(
                    "加载 YAML 配置需要安装 PyYAML: pip install pyyaml"
                )
            data = yaml.safe_load(content)
        else:
            raise ValueError(
                f"不支持的配置文件格式: {suffix}。支持的格式: .json, .yaml, .yml"
            )
        
        # 应用环境变量覆盖
        data = cls._apply_env_overrides(data)
        
        return cls(**data)
    
    @staticmethod
    def _apply_env_overrides(data: Dict) -> Dict:
        """应用环境变量覆盖配置。
        
        支持的环境变量格式:
        - YUNBOT_API_TIMEOUT: 覆盖 api_timeout
        - YUNBOT_MAX_CONCURRENT_REQUESTS: 覆盖 max_concurrent_requests
        - YUNBOT_ENABLE_HEARTBEAT: 覆盖 enable_heartbeat (true/false)
        - YUNBOT_HEARTBEAT_INTERVAL: 覆盖 heartbeat_interval
        - YUNBOT_RECONNECT_INTERVAL: 覆盖 reconnect_interval
        - YUNBOT_MAX_RECONNECT_ATTEMPTS: 覆盖 max_reconnect_attempts
        
        Args:
            data: 原始配置字典
            
        Returns:
            Dict: 应用环境变量覆盖后的配置字典
        """
        env_mappings = {
            "YUNBOT_API_TIMEOUT": ("api_timeout", float),
            "YUNBOT_MAX_CONCURRENT_REQUESTS": ("max_concurrent_requests", int),
            "YUNBOT_ENABLE_HEARTBEAT": ("enable_heartbeat", lambda x: x.lower() == "true"),
            "YUNBOT_HEARTBEAT_INTERVAL": ("heartbeat_interval", float),
            "YUNBOT_RECONNECT_INTERVAL": ("reconnect_interval", float),
            "YUNBOT_MAX_RECONNECT_ATTEMPTS": ("max_reconnect_attempts", int),
        }
        
        for env_key, (config_key, converter) in env_mappings.items():
            env_value = os.getenv(env_key)
            if env_value is not None:
                try:
                    data[config_key] = converter(env_value)
                except (ValueError, TypeError):
                    # 忽略无效的环境变量值
                    pass
        
        return data
    
    def to_file(self, path: Union[str, Path], encoding: str = "utf-8", indent: int = 2) -> None:
        """将配置保存到文件。
        
        支持 JSON 和 YAML 格式,根据文件扩展名自动识别。
        
        Args:
            path: 配置文件路径
            encoding: 文件编码,默认为 utf-8
            indent: 缩进空格数,默认为 2
            
        Raises:
            ValueError: 如果文件格式不支持
            ImportError: 如果 YAML 文件需要 PyYAML 但未安装
            
        Examples:
            >>> config.to_file("config.json")
            >>> config.to_file("config.yaml")
        """
        path = Path(path)
        suffix = path.suffix.lower()
        
        # 转换为字典
        data = self.model_dump()
        
        if suffix == ".json":
            content = json.dumps(data, ensure_ascii=False, indent=indent)
        elif suffix in (".yaml", ".yml"):
            if not YAML_AVAILABLE:
                raise ImportError(
                    "保存 YAML 配置需要安装 PyYAML: pip install pyyaml"
                )
            content = yaml.safe_dump(
                data, 
                allow_unicode=True, 
                default_flow_style=False,
                indent=indent
            )
        else:
            raise ValueError(
                f"不支持的配置文件格式: {suffix}。支持的格式: .json, .yaml, .yml"
            )
        
        # 确保父目录存在
        path.parent.mkdir(parents=True, exist_ok=True)
        
        # 写入文件
        path.write_text(content, encoding=encoding)