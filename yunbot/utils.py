"""OneBot v11 客户端适配器的工具函数和类。

此模块提供了各种实用工具，包括请求ID生成、时间转换、性能监控等功能。
所有工具函数都经过优化，以提高性能和可靠性。

主要功能：
1. 请求ID生成 - 用于跟踪API调用
2. 时间转换 - 在不同时间格式之间转换
3. 性能监控 - 测量函数执行时间
4. 重试装饰器 - 自动重试失败的操作
"""

import asyncio
import json
import logging
import os
import secrets
import sys
import time
from datetime import datetime
from logging.handlers import RotatingFileHandler
from typing import Any, Awaitable, Callable, Dict, Optional, TypeVar, Union, List, Tuple, cast, Type
from functools import wraps, lru_cache

# 导入新的日志模块
from .logger import default_logger as logger

T = TypeVar("T")


def generate_request_id() -> str:
    """生成唯一请求ID。
    
    Returns:
        str: 32位十六进制字符串
    """
    return secrets.token_hex(16)


@lru_cache(maxsize=128)
def timestamp_to_datetime(timestamp: int) -> float:
    """将时间戳转换为日期时间。
    
    Args:
        timestamp: 整数时间戳
        
    Returns:
        float: 浮点时间戳
    """
    return float(timestamp)


@lru_cache(maxsize=128)
def datetime_to_timestamp(dt: float) -> int:
    """将日期时间转换为时间戳。
    
    Args:
        dt: 浮点时间戳或日期时间对象
        
    Returns:
        int: 整数时间戳
    """
    return int(dt)


def performance_monitor(func: Callable[..., Any]) -> Callable[..., Any]:
    """性能监控装饰器。
    
    记录函数执行时间并在执行时间过长时发出警告。
    
    Args:
        func: 要监控的函数
        
    Returns:
        装饰后的函数
    """
    @wraps(func)
    async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
        finally:
            execution_time = time.time() - start_time

            if execution_time > 1.0:  # 超过1秒记录警告
                logger.warning(
                    f"性能警告: 函数 {func.__name__} 执行时间为 {execution_time:.2f}秒"
                )
            elif execution_time > 0.1:  # 超过100毫秒记录信息
                logger.info(
                    f"性能信息: 函数 {func.__name__} 执行时间为 {execution_time:.2f}秒"
                )

        return result

    @wraps(func)
    def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
        finally:
            execution_time = time.time() - start_time

            if execution_time > 1.0:  # 超过1秒记录警告
                logger.warning(
                    f"性能警告: 函数 {func.__name__} 执行时间为 {execution_time:.2f}秒"
                )
            elif execution_time > 0.1:  # 超过100毫秒记录信息
                logger.info(
                    f"性能信息: 函数 {func.__name__} 执行时间为 {execution_time:.2f}秒"
                )

        return result

    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    return sync_wrapper


def escape_text(text: str) -> str:
    """转义文本中的特殊字符。
    
    参数:
        text: 要转义的文本
        
    返回:
        str: 转义后的文本
    """
    return text.replace("&", "&amp;").replace("[", "&#91;").replace("]", "&#93;")


def unescape_text(text: str) -> str:
    """反转义文本中的特殊字符。
    
    参数:
        text: 要反转义的文本
        
    返回:
        str: 反转义后的文本
    """
    return text.replace("&#93;", "]").replace("&#91;", "[").replace("&amp;", "&")


def validate_qq(qq: Union[int, str]) -> str:
    """验证QQ号码。
    
    参数:
        qq: QQ号码
        
    返回:
        str: 验证后的QQ号码字符串
        
    异常:
        ValueError: 当QQ号码格式不正确时
    """
    qq_str = str(qq)
    if not qq_str.isdigit() or len(qq_str) < 5 or len(qq_str) > 12:
        raise ValueError(f"Invalid QQ number: {qq}")
    return qq_str


def validate_group_id(group_id: Union[int, str]) -> str:
    """验证群组ID。
    
    参数:
        group_id: 群组ID
        
    返回:
        str: 验证后的群组ID字符串
        
    异常:
        ValueError: 当群组ID格式不正确时
    """
    group_id_str = str(group_id)
    if not group_id_str.isdigit() or len(group_id_str) < 5 or len(group_id_str) > 12:
        raise ValueError(f"Invalid group ID: {group_id}")
    return group_id_str


def retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,)
) -> Callable[[Callable[..., Awaitable[T]]], Callable[..., Awaitable[T]]]:
    """重试装饰器。
    
    参数:
        max_attempts: 最大重试次数
        delay: 初始延迟时间（秒）
        backoff: 延迟时间增长因子
        exceptions: 需要重试的异常类型元组
        
    返回:
        装饰器函数
    """
    def decorator(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            last_exception: Optional[Exception] = None
            current_delay = delay

            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        logger.warning(
                            f"第 {attempt + 1} 次尝试失败 {func.__name__}: {e}"
                        )
                        await asyncio.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error(
                            f"所有 {max_attempts} 次尝试都失败 {func.__name__}: {e}"
                        )

            # 这里确保last_exception不为None
            if last_exception is not None:
                raise last_exception
            # 理论上不应该到达这里，但为了类型检查安全
            raise RuntimeError("重试失败且没有异常")

        return wrapper
    return decorator


def rate_limit(
    max_calls: int = 10,
    time_window: float = 60.0
) -> Callable[[Callable[..., Awaitable[T]]], Callable[..., Awaitable[T]]]:
    """速率限制装饰器。
    
    限制函数在指定时间窗口内的最大调用次数。
    
    Args:
        max_calls: 时间窗口内允许的最大调用次数
        time_window: 时间窗口大小（秒）
        
    Returns:
        装饰器函数
    """
    def decorator(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
        calls: List[float] = []
        lock = asyncio.Lock()

        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            async with lock:
                now = time.time()
                # 清理过期的调用记录
                calls[:] = [call for call in calls if now - call < time_window]

                if len(calls) >= max_calls:
                    sleep_time = time_window - (now - calls[0])
                    if sleep_time > 0:
                        await asyncio.sleep(sleep_time)
                        # 再次清理过期的调用记录
                        calls[:] = [call for call in calls if time.time() - call < time_window]

                calls.append(now)

            return await func(*args, **kwargs)

        return wrapper
    return decorator


def singleton(cls: type) -> Callable[..., Any]:
    """单例装饰器。
    
    参数:
        cls: 要装饰的类
        
    返回:
        装饰器函数
    """
    instances: Dict[type, Any] = {}

    @wraps(cls)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return wrapper


class AsyncLock:
    """异步锁管理器。"""

    def __init__(self) -> None:
        """初始化异步锁"""
        self._lock = asyncio.Lock()

    async def __aenter__(self) -> "AsyncLock":
        """进入异步上下文管理器"""
        await self._lock.acquire()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """退出异步上下文管理器"""
        self._lock.release()


class Debouncer:
    """防抖工具。"""

    def __init__(self, delay: float) -> None:
        """初始化防抖器
        
        参数:
            delay: 延迟时间（秒）
        """
        self.delay = delay
        self._timer: Optional[asyncio.Task[Any]] = None
        self._lock = asyncio.Lock()

    async def debounce(self, func: Callable[[], Awaitable[None]]) -> None:
        """防抖函数调用。
        
        参数:
            func: 要防抖的异步函数
        """
        async with self._lock:
            if self._timer:
                self._timer.cancel()

            async def delayed_call() -> None:
                await asyncio.sleep(self.delay)
                await func()

            self._timer = asyncio.create_task(delayed_call())


class Throttler:
    """节流工具。"""

    def __init__(self, delay: float) -> None:
        """初始化节流器
        
        参数:
            delay: 节流延迟时间（秒）
        """
        self.delay = delay
        self._last_call = 0.0
        self._lock = asyncio.Lock()

    async def throttle(self, func: Callable[[], Awaitable[T]]) -> T:
        """节流函数调用。
        
        参数:
            func: 要节流的异步函数
            
        返回:
            T: 函数返回值
        """
        async with self._lock:
            now = time.time()
            time_since_last = now - self._last_call

            if time_since_last < self.delay:
                await asyncio.sleep(self.delay - time_since_last)

            self._last_call = time.time()
            return await func()


def deep_merge(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """深度合并两个字典。
    
    参数:
        dict1: 第一个字典
        dict2: 第二个字典
        
    返回:
        Dict[str, Any]: 合并后的字典
    """
    result = dict1.copy()

    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value

    return result


def safe_json_loads(data: str, default: Any = None) -> Any:
    """安全加载JSON数据。
    
    参数:
        data: JSON字符串
        default: 默认值
        
    返回:
        解析后的数据或默认值
    """
    try:
        return json.loads(data)
    except (json.JSONDecodeError, TypeError):
        return default


def safe_json_dumps(data: Any, default: str = "") -> str:
    """安全序列化JSON数据。
    
    参数:
        data: 要序列化的数据
        default: 默认值
        
    返回:
        str: JSON字符串或默认值
    """
    try:
        return json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    except (TypeError, ValueError):
        return default


class EventEmitter:
    """简单的事件发射器。"""

    def __init__(self) -> None:
        """初始化事件发射器"""
        self._handlers: Dict[str, List[Callable[..., Any]]] = {}

    def on(self, event: str, handler: Callable[..., Any]) -> None:
        """注册事件处理器。
        
        参数:
            event: 事件名称
            handler: 事件处理器
        """
        if event not in self._handlers:
            self._handlers[event] = []
        self._handlers[event].append(handler)

    def off(self, event: str, handler: Callable[..., Any]) -> None:
        """注销事件处理器。
        
        参数:
            event: 事件名称
            handler: 事件处理器
        """
        if event in self._handlers:
            try:
                self._handlers[event].remove(handler)
            except ValueError:
                pass

    async def emit(self, event: str, *args: Any, **kwargs: Any) -> None:
        """发射事件。
        
        参数:
            event: 事件名称
            *args: 位置参数
            **kwargs: 关键字参数
        """
        if event in self._handlers:
            for handler in self._handlers[event]:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(*args, **kwargs)
                    else:
                        handler(*args, **kwargs)
                except Exception as e:
                    logger.error(f"事件处理器错误 {event}: {e}")


class CircularBuffer:
    """循环缓冲区实现。"""

    def __init__(self, size: int) -> None:
        """初始化循环缓冲区
        
        参数:
            size: 缓冲区大小
        """
        self.size = size
        self.buffer: List[Optional[Any]] = [None] * size
        self.head = 0
        self.count = 0

    def put(self, item: Any) -> None:
        """将项目放入缓冲区。
        
        参数:
            item: 要放入的项目
        """
        self.buffer[self.head] = item
        self.head = (self.head + 1) % self.size
        if self.count < self.size:
            self.count += 1

    def get(self) -> Any:
        """从缓冲区获取项目。
        
        返回:
            从缓冲区获取的项目，如果缓冲区为空则返回None
        """
        if self.count == 0:
            return None

        tail = (self.head - self.count) % self.size
        item = self.buffer[tail]
        self.buffer[tail] = None
        self.count -= 1
        return item

    def is_empty(self) -> bool:
        """检查缓冲区是否为空。
        
        返回:
            bool: 如果缓冲区为空返回True，否则返回False
        """
        return self.count == 0

    def is_full(self) -> bool:
        """检查缓冲区是否已满。
        
        返回:
            bool: 如果缓冲区已满返回True，否则返回False
        """
        return self.count == self.size

    def clear(self) -> None:
        """清空缓冲区。"""
        self.buffer = [None] * self.size
        self.head = 0
        self.count = 0