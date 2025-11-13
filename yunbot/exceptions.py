"""OneBot v11 客户端适配器的异常类。

此模块定义了与 OneBot 适配器相关的所有异常类，用于标准化错误处理和提供详细的错误信息。
所有异常类都继承自 OneBotException 基类，提供了统一的错误处理接口。
"""

import time
from typing import Any, Dict, Optional, List


class OneBotException(Exception):
    """OneBot 适配器的基础异常类。
    
    所有其他异常类都继承自此类，提供基本的错误信息处理功能。
    
    Attributes:
        message: 错误信息
        timestamp: 异常发生的时间戳
    """
    
    def __init__(self, message: str, *args: Any) -> None:
        """初始化异常。
        
        Args:
            message: 错误信息
            args: 其他参数
        """
        super().__init__(message, *args)
        self.message = message
        self.timestamp = time.time()
    
    def __str__(self) -> str:
        """返回格式化的错误信息。"""
        return f"{self.message}"
    
    def __repr__(self) -> str:
        """返回异常的详细表示。"""
        return f"{self.__class__.__name__}(message='{self.message}', timestamp={self.timestamp})"


class NetworkException(OneBotException):
    """网络相关异常。
    
    当网络连接出现问题时抛出，如连接超时、连接失败等。
    
    Attributes:
        message: 错误信息
        status_code: HTTP 状态码
        timestamp: 异常发生的时间戳
        retry_count: 已重试次数
    """
    
    def __init__(
        self, 
        message: str, 
        status_code: Optional[int] = None,
        retry_count: int = 0,
        *args: Any
    ) -> None:
        """初始化网络异常。
        
        Args:
            message: 错误信息
            status_code: HTTP 状态码
            retry_count: 已重试次数
            args: 其他参数
        """
        super().__init__(message, *args)
        self.status_code = status_code
        self.retry_count = retry_count
    
    def __str__(self) -> str:
        """返回格式化的错误信息。"""
        status_info = f"状态码: {self.status_code}" if self.status_code else ""
        retry_info = f"已重试: {self.retry_count}次" if self.retry_count else ""
        
        parts = [self.message]
        if status_info:
            parts.append(status_info)
        if retry_info:
            parts.append(retry_info)
            
        return " | ".join(parts)
    
    def should_retry(self) -> bool:
        """判断是否应该重试。
        
        Returns:
            bool: 如果应该重试返回 True，否则返回 False
        """
        # 对于网络错误，通常应该重试
        return True


class ActionFailed(OneBotException):
    """API 调用失败异常。
    
    当 OneBot API 调用失败时抛出，包含详细的错误信息和返回数据。
    
    Attributes:
        message: 错误信息
        retcode: 返回码
        status: 状态信息
        data: 返回数据
        api: API 名称
        params: API 参数
    """
    
    def __init__(
        self, 
        message: str, 
        retcode: Optional[int] = None,
        status: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
        api: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
        *args: Any
    ) -> None:
        """初始化 API 调用失败异常。
        
        Args:
            message: 错误信息
            retcode: 返回码
            status: 状态信息
            data: 返回数据
            api: API 名称
            params: API 参数
            args: 其他参数
        """
        super().__init__(message, *args)
        self.retcode = retcode
        self.status = status
        self.data = data or {}
        self.api = api
        self.params = params or {}
    
    def __str__(self) -> str:
        """返回格式化的错误信息。"""
        parts = [self.message]
        if self.retcode is not None:
            parts.append(f"返回码: {self.retcode}")
        if self.status:
            parts.append(f"状态: {self.status}")
        if self.api:
            parts.append(f"API: {self.api}")
        return " | ".join(parts)
    
    def is_rate_limited(self) -> bool:
        """判断是否是速率限制错误。
        
        Returns:
            bool: 如果是速率限制错误返回 True，否则返回 False
        """
        # 假设返回码 429 表示速率限制
        return self.retcode == 429


class ApiNotAvailable(OneBotException):
    """API 不可用异常。
    
    当 API 不可用时抛出，例如连接未建立或 API 被禁用。
    """
    
    def __init__(self, message: str = "API not available", *args: Any) -> None:
        """初始化 API 不可用异常。
        
        Args:
            message: 错误信息
            args: 其他参数
        """
        super().__init__(message, *args)
    
    def __str__(self) -> str:
        """返回格式化的错误信息。"""
        return f"API不可用: {self.message}"


class TimeoutException(NetworkException):
    """超时异常。
    
    当请求超时时抛出。
    """
    
    def __init__(self, message: str = "Request timeout", *args: Any) -> None:
        """初始化超时异常。
        
        Args:
            message: 错误信息
            args: 其他参数
        """
        super().__init__(message, *args)
    
    def __str__(self) -> str:
        """返回格式化的错误信息。"""
        return f"请求超时: {self.message}"


class AuthenticationFailed(OneBotException):
    """身份验证失败异常。
    
    当身份验证失败时抛出，例如访问令牌无效。
    """
    
    def __init__(self, message: str = "Authentication failed", *args: Any) -> None:
        """初始化身份验证失败异常。
        
        Args:
            message: 错误信息
            args: 其他参数
        """
        super().__init__(message, *args)
    
    def __str__(self) -> str:
        """返回格式化的错误信息。"""
        return f"身份验证失败: {self.message}"


class ConnectionClosed(NetworkException):
    """连接关闭异常。"""
    
    def __init__(
        self, 
        message: str = "Connection closed", 
        code: Optional[int] = None,
        *args: Any
    ) -> None:
        """初始化连接关闭异常。"""
        super().__init__(message, *args)
        self.code = code


class InvalidEvent(OneBotException):
    """无效事件异常。"""
    
    def __init__(self, message: str = "Invalid event data", *args: Any) -> None:
        """初始化无效事件异常。"""
        super().__init__(message, *args)


class ConfigurationError(OneBotException):
    """配置错误异常。"""
    
    def __init__(self, message: str = "Configuration error", *args: Any) -> None:
        """初始化配置错误异常。"""
        super().__init__(message, *args)