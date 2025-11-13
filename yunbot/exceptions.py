"""OneBot v11 客户端适配器的异常类。

此模块定义了与 OneBot 适配器相关的所有异常类，用于标准化错误处理和提供详细的错误信息。
所有异常类都继承自 OneBotException 基类，提供了统一的错误处理接口。
"""

import time
from typing import Any, Dict, Optional, List, Union


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


class RateLimitError(ActionFailed):
    """速率限制异常。
    
    当 API 调用频率超过限制时抛出。
    
    Attributes:
        retry_after: 建议的重试等待时间(秒)
        limit_type: 限制类型(api/message/global)
    """
    
    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: Optional[int] = None,
        limit_type: str = "api",
        *args: Any
    ) -> None:
        """初始化速率限制异常。
        
        Args:
            message: 错误信息
            retry_after: 建议的重试等待时间(秒)
            limit_type: 限制类型
            args: 其他参数
        """
        super().__init__(message, retcode=429, *args)
        self.retry_after = retry_after
        self.limit_type = limit_type
    
    def __str__(self) -> str:
        """返回格式化的错误信息。"""
        parts = [f"速率限制: {self.message}"]
        if self.retry_after:
            parts.append(f"建议{self.retry_after}秒后重试")
        if self.limit_type:
            parts.append(f"限制类型: {self.limit_type}")
        return " | ".join(parts)


class PermissionError(ActionFailed):
    """权限不足异常。
    
    当机器人没有执行某操作的权限时抛出。
    
    Attributes:
        required_permission: 需要的权限
        current_permission: 当前权限
    """
    
    def __init__(
        self,
        message: str = "Permission denied",
        required_permission: Optional[str] = None,
        current_permission: Optional[str] = None,
        *args: Any
    ) -> None:
        """初始化权限不足异常。
        
        Args:
            message: 错误信息
            required_permission: 需要的权限
            current_permission: 当前权限
            args: 其他参数
        """
        super().__init__(message, retcode=403, *args)
        self.required_permission = required_permission
        self.current_permission = current_permission
    
    def __str__(self) -> str:
        """返回格式化的错误信息。"""
        parts = [f"权限不足: {self.message}"]
        if self.required_permission:
            parts.append(f"需要权限: {self.required_permission}")
        if self.current_permission:
            parts.append(f"当前权限: {self.current_permission}")
        return " | ".join(parts)


class RetryableError(OneBotException):
    """可重试的错误异常。
    
    表示该错误是暂时性的，可以通过重试解决。
    
    Attributes:
        max_retries: 最大重试次数
        current_retry: 当前重试次数
        backoff_factor: 退避系数(指数退避)
    """
    
    def __init__(
        self,
        message: str,
        max_retries: int = 3,
        current_retry: int = 0,
        backoff_factor: float = 2.0,
        *args: Any
    ) -> None:
        """初始化可重试错误异常。
        
        Args:
            message: 错误信息
            max_retries: 最大重试次数
            current_retry: 当前重试次数
            backoff_factor: 退避系数
            args: 其他参数
        """
        super().__init__(message, *args)
        self.max_retries = max_retries
        self.current_retry = current_retry
        self.backoff_factor = backoff_factor
    
    def should_retry(self) -> bool:
        """判断是否应该重试。
        
        Returns:
            bool: 如果应该重试返回 True，否则返回 False
        """
        return self.current_retry < self.max_retries
    
    def get_retry_delay(self) -> float:
        """计算下次重试的等待时间(指数退避)。
        
        Returns:
            float: 等待时间(秒)
        """
        return self.backoff_factor ** self.current_retry
    
    def increment_retry(self) -> None:
        """增加重试计数。"""
        self.current_retry += 1
    
    def __str__(self) -> str:
        """返回格式化的错误信息。"""
        return f"{self.message} (重试 {self.current_retry}/{self.max_retries})"


class ResourceNotFound(ActionFailed):
    """资源未找到异常。
    
    当请求的资源不存在时抛出。
    
    Attributes:
        resource_type: 资源类型(user/group/message等)
        resource_id: 资源ID
    """
    
    def __init__(
        self,
        message: str = "Resource not found",
        resource_type: Optional[str] = None,
        resource_id: Optional[Union[int, str]] = None,
        *args: Any
    ) -> None:
        """初始化资源未找到异常。
        
        Args:
            message: 错误信息
            resource_type: 资源类型
            resource_id: 资源ID
            args: 其他参数
        """
        super().__init__(message, retcode=404, *args)
        self.resource_type = resource_type
        self.resource_id = resource_id
    
    def __str__(self) -> str:
        """返回格式化的错误信息。"""
        parts = [f"资源未找到: {self.message}"]
        if self.resource_type:
            parts.append(f"类型: {self.resource_type}")
        if self.resource_id:
            parts.append(f"ID: {self.resource_id}")
        return " | ".join(parts)


class ServerError(OneBotException):
    """服务器错误异常。
    
    当服务器内部错误时抛出。
    
    Attributes:
        status_code: HTTP状态码
        server_message: 服务器返回的错误信息
    """
    
    def __init__(
        self,
        message: str = "Server error",
        status_code: int = 500,
        server_message: Optional[str] = None,
        *args: Any
    ) -> None:
        """初始化服务器错误异常。
        
        Args:
            message: 错误信息
            status_code: HTTP状态码
            server_message: 服务器返回的错误信息
            args: 其他参数
        """
        super().__init__(message, *args)
        self.status_code = status_code
        self.server_message = server_message
    
    def __str__(self) -> str:
        """返回格式化的错误信息。"""
        parts = [f"服务器错误({self.status_code}): {self.message}"]
        if self.server_message:
            parts.append(f"服务器消息: {self.server_message}")
        return " | ".join(parts)