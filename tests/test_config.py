"""Tests for configuration module."""

import pytest
from onebot_adapter_client.config import (
    Config,
    HttpConfig,
    WebSocketConfig,
    ReverseWebSocketConfig,
    WebhookConfig,
)


class TestHttpConfig:
    """Test HTTP configuration."""
    
    def test_valid_http_config(self):
        """Test valid HTTP configuration."""
        config = HttpConfig(
            base_url="http://127.0.0.1:5700",
            access_token="test_token",
            self_id="123456789"
        )
        assert config.type == "http"
        assert config.base_url == "http://127.0.0.1:5700"
        assert config.access_token == "test_token"
        assert config.self_id == "123456789"
    
    def test_invalid_base_url(self):
        """Test invalid base URL."""
        with pytest.raises(ValueError, match="base_url must start with http:// or https://"):
            HttpConfig(base_url="invalid_url")
    
    def test_base_url_trailing_slash(self):
        """Test base URL trailing slash removal."""
        config = HttpConfig(base_url="http://127.0.0.1:5700/")
        assert config.base_url == "http://127.0.0.1:5700"


class TestWebSocketConfig:
    """Test WebSocket configuration."""
    
    def test_valid_websocket_config(self):
        """Test valid WebSocket configuration."""
        config = WebSocketConfig(
            url="ws://127.0.0.1:6700",
            access_token="test_token",
            heartbeat_interval=30.0
        )
        assert config.type == "websocket"
        assert config.url == "ws://127.0.0.1:6700"
        assert config.heartbeat_interval == 30.0
    
    def test_invalid_url(self):
        """Test invalid WebSocket URL."""
        with pytest.raises(ValueError, match="url must start with ws:// or wss://"):
            WebSocketConfig(url="invalid_url")


class TestReverseWebSocketConfig:
    """Test reverse WebSocket configuration."""
    
    def test_valid_reverse_ws_config(self):
        """Test valid reverse WebSocket configuration."""
        config = ReverseWebSocketConfig(
            host="0.0.0.0",
            port=8080,
            path="/onebot/v11/ws"
        )
        assert config.type == "reverse_ws"
        assert config.host == "0.0.0.0"
        assert config.port == 8080
        assert config.path == "/onebot/v11/ws"
    
    def test_invalid_port(self):
        """Test invalid port number."""
        with pytest.raises(ValueError, match="port must be between 1 and 65535"):
            ReverseWebSocketConfig(port=0)
        
        with pytest.raises(ValueError, match="port must be between 1 and 65535"):
            ReverseWebSocketConfig(port=70000)


class TestWebhookConfig:
    """Test webhook configuration."""
    
    def test_valid_webhook_config(self):
        """Test valid webhook configuration."""
        config = WebhookConfig(
            host="0.0.0.0",
            port=8081,
            path="/onebot/v11/webhook",
            secret="test_secret"
        )
        assert config.type == "webhook"
        assert config.host == "0.0.0.0"
        assert config.port == 8081
        assert config.secret == "test_secret"


class TestConfig:
    """Test main configuration."""
    
    def test_valid_config(self):
        """Test valid configuration."""
        connections = [
            HttpConfig(base_url="http://127.0.0.1:5700"),
            WebSocketConfig(url="ws://127.0.0.1:6700")
        ]
        
        config = Config(
            connections=connections,
            api_timeout=45.0,
            max_concurrent_requests=200
        )
        
        assert len(config.connections) == 2
        assert config.api_timeout == 45.0
        assert config.max_concurrent_requests == 200
    
    def test_empty_connections(self):
        """Test empty connections list."""
        with pytest.raises(ValueError, match="At least one connection configuration is required"):
            Config(connections=[])
    
    def test_get_connection_by_type(self):
        """Test getting connection by type."""
        connections = [
            HttpConfig(base_url="http://127.0.0.1:5700"),
            WebSocketConfig(url="ws://127.0.0.1:6700")
        ]
        
        config = Config(connections=connections)
        
        http_conn = config.get_connection_by_type("http")
        assert http_conn is not None
        assert http_conn.type == "http"
        
        ws_conn = config.get_connection_by_type("websocket")
        assert ws_conn is not None
        assert ws_conn.type == "websocket"
        
        missing_conn = config.get_connection_by_type("missing")
        assert missing_conn is None
    
    def test_get_connections_by_types(self):
        """Test getting connections by types."""
        connections = [
            HttpConfig(base_url="http://127.0.0.1:5700"),
            WebSocketConfig(url="ws://127.0.0.1:6700"),
            ReverseWebSocketConfig(port=8080)
        ]
        
        config = Config(connections=connections)
        
        http_conns = config.get_connections_by_types("http")
        assert len(http_conns) == 1
        
        ws_conns = config.get_connections_by_types("websocket", "reverse_ws")
        assert len(ws_conns) == 2