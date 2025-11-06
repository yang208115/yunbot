"""OneBot API 响应存储模块

此模块提供了 API 响应存储功能，用于管理异步 API 调用的响应。
主要功能包括响应匹配、超时处理和请求管理。
"""

import asyncio
from typing import Any, Dict, Optional, List
from .exceptions import NetworkException


class ResultStore:
    """API响应存储器，用于管理异步API调用的响应
    
    该类负责存储和管理API请求的响应结果，支持按echo标识匹配响应，
    处理超时情况，并提供请求管理功能。
    """

    def __init__(self) -> None:
        """初始化结果存储器"""
        self._futures: Dict[str, asyncio.Future] = {}

    def add_result(self, result: Dict[str, Any]) -> bool:
        """添加API响应结果，如果匹配成功返回True
        
        Args:
            result: API响应字典，应包含echo标识
            
        Returns:
            bool: 是否成功匹配到等待中的请求
        """
        echo = result.get("echo")
        if echo and echo in self._futures:
            future = self._futures.pop(echo)
            if not future.done():
                if result.get("status") == "failed":
                    error_msg = result.get("message", result.get("msg", "API调用失败"))
                    future.set_exception(NetworkException(error_msg))
                else:
                    future.set_result(result)
                return True
        return False

    def add_result_by_order(self, result: Dict[str, Any]) -> bool:
        """按顺序匹配API响应（当echo不匹配时使用）
        
        Args:
            result: API响应字典
            
        Returns:
            bool: 是否成功匹配到等待中的请求
        """
        if self._futures:
            first_echo = next(iter(self._futures))
            future = self._futures.pop(first_echo)
            if not future.done():
                if result.get("status") == "failed":
                    error_msg = result.get("message", result.get("msg", "API调用失败"))
                    future.set_exception(NetworkException(error_msg))
                else:
                    future.set_result(result)
                return True
        return False

    async def fetch(self, echo: str, timeout: Optional[float] = None) -> Dict[str, Any]:
        """等待API响应
        
        Args:
            echo: 请求的echo标识
            timeout: 超时时间（秒）
            
        Returns:
            Dict[str, Any]: API响应数据
            
        Raises:
            NetworkException: 超时或其他网络错误
        """
        future = asyncio.get_event_loop().create_future()
        self._futures[echo] = future
        try:
            return await asyncio.wait_for(future, timeout=timeout)
        except asyncio.TimeoutError:
            raise NetworkException(f"API请求超时: {echo}")
        finally:
            self._futures.pop(echo, None)

    def get_pending_requests(self) -> List[str]:
        """获取当前待处理的请求echo列表
        
        Returns:
            List[str]: 待处理请求的echo标识列表
        """
        return list(self._futures.keys())

    def clear_all(self) -> None:
        """清除所有待处理的请求"""
        for future in self._futures.values():
            if not future.done():
                future.cancel()
        self._futures.clear()