"""Configuration module for OneBot v11 client adapter.

This module provides Pydantic models for configuring the OneBot v11 client.
It includes models for different connection types and main configuration.
"""

from typing import Dict, List, Optional, Union, Literal
from pydantic import BaseModel, Field, field_validator, ConfigDict


class ConnectionConfig(BaseModel):
    """Base connection configuration."""
    
    type: str = Field(..., description="Connection type")
    self_id: Optional[str] = Field(None, description="Bot self ID")
    access_token: Optional[str] = Field(None, description="Access token for authentication")
    secret: Optional[str] = Field(None, description="Secret for webhook signature")
    timeout: float = Field(30.0, description="Request timeout in seconds")
    retry_times: int = Field(3, description="Retry times for failed requests")
    retry_interval: float = Field(1.0, description="Retry interval in seconds")
    
    model_config = ConfigDict(extra="ignore")


class HttpConfig(ConnectionConfig):
    """HTTP connection configuration.
    
    Configuration for HTTP connections to the OneBot v11 API.
    """
    
    type: str = "http"
    base_url: str = Field(..., description="Base URL for HTTP API")
    
    @field_validator("base_url")
    def validate_base_url(cls, v: str) -> str:
        """Validate base URL format.
        
        Args:
            v: Base URL string to validate
            
        Returns:
            str: Validated and stripped base URL
            
        Raises:
            ValueError: If URL doesn't start with http:// or https://
        """
        if not v.startswith(("http://", "https://")):
            raise ValueError("base_url must start with http:// or https://")
        return v.rstrip("/")


class WebSocketConfig(ConnectionConfig):
    """WebSocket connection configuration.
    
    Configuration for WebSocket connections to the OneBot v11 API.
    """
    
    type: str = "websocket"
    url: str = Field(..., description="WebSocket URL")
    heartbeat_interval: Optional[float] = Field(None, description="Heartbeat interval in seconds")
    
    @field_validator("url")
    def validate_url(cls, v: str) -> str:
        """Validate WebSocket URL format.
        
        Args:
            v: WebSocket URL string to validate
            
        Returns:
            str: Validated URL
            
        Raises:
            ValueError: If URL doesn't start with ws:// or wss://
        """
        if not v.startswith(("ws://", "wss://")):
            raise ValueError("url must start with ws:// or wss://")
        return v


class ReverseWebSocketConfig(ConnectionConfig):
    """Reverse WebSocket connection configuration.
    
    Configuration for reverse WebSocket connections where the client acts as a server.
    """
    
    type: str = "reverse_ws"
    host: str = Field(default="127.0.0.1", description="Host to listen on")
    port: int = Field(..., description="Port to listen on")
    path: str = Field(default="/onebot/v11/ws", description="WebSocket path")
    
    @field_validator("port")
    def validate_port(cls, v: int) -> int:
        """Validate port number range.
        
        Args:
            v: Port number to validate
            
        Returns:
            int: Validated port number
            
        Raises:
            ValueError: If port is not between 1 and 65535
        """
        if not (1 <= v <= 65535):
            raise ValueError("port must be between 1 and 65535")
        return v


class WebhookConfig(ConnectionConfig):
    """Webhook connection configuration.
    
    Configuration for webhook connections where the client receives HTTP POST requests.
    """
    
    type: str = "webhook"
    host: str = Field(default="127.0.0.1", description="Host to listen on")
    port: int = Field(..., description="Port to listen on")
    path: str = Field(default="/onebot/v11/webhook", description="Webhook path")
    
    @field_validator("port")
    def validate_port(cls, v: int) -> int:
        """Validate port number range.
        
        Args:
            v: Port number to validate
            
        Returns:
            int: Validated port number
            
        Raises:
            ValueError: If port is not between 1 and 65535
        """
        if not (1 <= v <= 65535):
            raise ValueError("port must be between 1 and 65535")
        return v


ConnectionTypes = Union[HttpConfig, WebSocketConfig, ReverseWebSocketConfig, WebhookConfig]


class Config(BaseModel):
    """Main configuration class.
    
    Main configuration class that contains all connection configurations
    and global settings for the OneBot v11 client.
    """
    
    connections: List[ConnectionTypes] = Field(
        default_factory=list, 
        description="List of connection configurations"
    )
    api_timeout: float = Field(30.0, description="API call timeout in seconds")
    max_concurrent_requests: int = Field(100, description="Maximum concurrent API requests")
    enable_heartbeat: bool = Field(True, description="Enable heartbeat for WebSocket connections")
    heartbeat_interval: float = Field(30.0, description="Default heartbeat interval in seconds")
    reconnect_interval: float = Field(5.0, description="Reconnect interval in seconds")
    max_reconnect_attempts: int = Field(10, description="Maximum reconnect attempts")
    
    @field_validator("connections")
    def validate_connections(cls, v: List[ConnectionTypes]) -> List[ConnectionTypes]:
        """Validate that at least one connection is configured.
        
        Args:
            v: List of connection configurations
            
        Returns:
            List[ConnectionTypes]: Validated list of connections
            
        Raises:
            ValueError: If no connections are configured
        """
        if not v:
            raise ValueError("At least one connection configuration is required")
        return v
    
    def get_connection_by_type(self, connection_type: str) -> Optional[ConnectionTypes]:
        """Get connection configuration by type.
        
        Args:
            connection_type: Type of connection to find
            
        Returns:
            Optional[ConnectionTypes]: Connection configuration if found, None otherwise
        """
        for conn in self.connections:
            if conn.type == connection_type:
                return conn
        return None
    
    def get_connections_by_types(self, *types: str) -> List[ConnectionTypes]:
        """Get connection configurations by types.
        
        Args:
            *types: Connection types to filter by
            
        Returns:
            List[ConnectionTypes]: List of matching connection configurations
        """
        return [conn for conn in self.connections if conn.type in types]