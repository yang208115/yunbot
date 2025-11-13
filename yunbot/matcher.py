"""事件处理器装饰器模块

本模块为 YunBot 提供类似 NoneBot2 的事件处理器装饰器功能，
包括 on_keyword、on_fullmatch、on_command 等装饰器。
"""

import asyncio
import re
from typing import Any, Awaitable, Callable, Dict, List, Optional, Set, Union
from functools import wraps

from .event import Event, MessageEvent
from .message import Message, MessageSegment
from .logger import default_logger as logger


class Matcher:
    """事件处理器类"""
    
    def __init__(
        self,
        type_: str = "",
        priority: int = 1,
        block: bool = False,
    ):
        self.type = type_
        self.priority = priority
        self.block = block
        self.handlers: List[Callable] = []
    
    def __call__(self, func: Callable) -> Callable:
        """使匹配器可以作为装饰器使用"""
        self.handlers.append(func)
        return func
    
    def handle(self) -> Callable:
        """装饰器，用于注册事件处理器"""
        def decorator(func: Callable) -> Callable:
            self.handlers.append(func)
            return func
        return decorator
    
    async def check_perm(self, event: Event) -> bool:
        """检查事件类型权限"""
        if not self.type:
            return True
        return hasattr(event, 'post_type') and event.post_type == self.type
    
    async def run(self, event: Event) -> bool:
        """运行事件处理器"""
        try:
            for handler in self.handlers:
                if asyncio.iscoroutinefunction(handler):
                    # 异步函数
                    await handler(event)
                else:
                    # 同步函数
                    handler(event)
            return self.block
        except Exception as e:
            logger.error(f"运行匹配器处理器时出错: {e}")
            return False


# 存储所有注册的匹配器
_matchers: List[Matcher] = []


def _register_matcher(matcher: Matcher) -> None:
    """注册匹配器"""
    _matchers.append(matcher)
    # 按优先级排序
    _matchers.sort(key=lambda m: m.priority)


async def handle_event(event: Event) -> None:
    """处理事件，调用匹配的处理器"""
    for matcher in _matchers:
        try:
            if await matcher.check_perm(event):
                block = await matcher.run(event)
                if block:
                    break  # 阻止事件继续传播
        except Exception as e:
            logger.error(f"处理匹配器 {matcher} 时出错: {e}")


def on(
    type_: str = "",
    priority: int = 1,
    block: bool = False,
) -> Matcher:
    """注册一个基础事件处理器"""
    matcher = Matcher(type_=type_, priority=priority, block=block)
    _register_matcher(matcher)
    return matcher


def on_message(
    priority: int = 1,
    block: bool = True,
) -> Matcher:
    """注册一个消息事件处理器"""
    return on(type_="message", priority=priority, block=block)


def on_notice(
    priority: int = 1,
    block: bool = False,
) -> Matcher:
    """注册一个通知事件处理器"""
    return on(type_="notice", priority=priority, block=block)


def on_request(
    priority: int = 1,
    block: bool = False,
) -> Matcher:
    """注册一个请求事件处理器"""
    return on(type_="request", priority=priority, block=block)


def on_metaevent(
    priority: int = 1,
    block: bool = False,
) -> Matcher:
    """注册一个元事件处理器"""
    return on(type_="meta_event", priority=priority, block=block)


def startswith(msg: Union[str, tuple[str, ...]]) -> Callable[[Event], bool]:
    """匹配消息开头"""
    def _startswith_checker(event: Event) -> bool:
        if not isinstance(event, MessageEvent):
            return False
        message = event.message
        if isinstance(message, list):
            # 提取文本内容
            text = ""
            for seg in message:
                if isinstance(seg, dict) and seg.get("type") == "text":
                    text += seg.get("data", {}).get("text", "")
                elif isinstance(seg, MessageSegment) and seg.type == "text":
                    text += str(seg)
        else:
            text = str(message)
        
        if isinstance(msg, str):
            return text.startswith(msg)
        else:
            return any(text.startswith(m) for m in msg)
    
    return _startswith_checker


def endswith(msg: Union[str, tuple[str, ...]]) -> Callable[[Event], bool]:
    """匹配消息结尾"""
    def _endswith_checker(event: Event) -> bool:
        if not isinstance(event, MessageEvent):
            return False
        message = event.message
        if isinstance(message, list):
            # 提取文本内容
            text = ""
            for seg in message:
                if isinstance(seg, dict) and seg.get("type") == "text":
                    text += seg.get("data", {}).get("text", "")
                elif isinstance(seg, MessageSegment) and seg.type == "text":
                    text += str(seg)
        else:
            text = str(message)
        
        if isinstance(msg, str):
            return text.endswith(msg)
        else:
            return any(text.endswith(m) for m in msg)
    
    return _endswith_checker


def fullmatch(msg: Union[str, tuple[str, ...]]) -> Callable[[Event], bool]:
    """完全匹配消息"""
    def _fullmatch_checker(event: Event) -> bool:
        if not isinstance(event, MessageEvent):
            return False
        message = event.message
        if isinstance(message, list):
            # 提取文本内容
            text = ""
            for seg in message:
                if isinstance(seg, dict) and seg.get("type") == "text":
                    text += seg.get("data", {}).get("text", "")
                elif isinstance(seg, MessageSegment) and seg.type == "text":
                    text += str(seg)
        else:
            text = str(message)
        
        if isinstance(msg, str):
            return text == msg
        else:
            return text in msg
    
    return _fullmatch_checker


def keyword(keywords: Set[str]) -> Callable[[Event], bool]:
    """匹配消息关键词"""
    def _keyword_checker(event: Event) -> bool:
        if not isinstance(event, MessageEvent):
            return False
        message = event.message
        if isinstance(message, list):
            # 提取文本内容
            text = ""
            for seg in message:
                if isinstance(seg, dict) and seg.get("type") == "text":
                    text += seg.get("data", {}).get("text", "")
                elif isinstance(seg, MessageSegment) and seg.type == "text":
                    text += str(seg)
        else:
            text = str(message)
        
        return any(keyword in text for keyword in keywords)
    
    return _keyword_checker


def command(cmd: Union[str, tuple[str, ...]]) -> Callable[[Event], bool]:
    """匹配命令"""
    def _command_checker(event: Event) -> bool:
        if not isinstance(event, MessageEvent):
            return False
        message = event.message
        if isinstance(message, list):
            # 提取文本内容
            text = ""
            for seg in message:
                if isinstance(seg, dict) and seg.get("type") == "text":
                    text += seg.get("data", {}).get("text", "")
                elif isinstance(seg, MessageSegment) and seg.type == "text":
                    text += str(seg)
        else:
            text = str(message)
        
        # 移除前导斜杠
        if text.startswith('/'):
            text = text[1:]
        
        if isinstance(cmd, str):
            return text.split()[0] == cmd
        else:
            return text.split()[0] in cmd
    
    return _command_checker


def regex(pattern: str, flags: Union[int, re.RegexFlag] = 0) -> Callable[[Event], bool]:
    """正则表达式匹配"""
    def _regex_checker(event: Event) -> bool:
        if not isinstance(event, MessageEvent):
            return False
        message = event.message
        if isinstance(message, list):
            # 提取文本内容
            text = ""
            for seg in message:
                if isinstance(seg, dict) and seg.get("type") == "text":
                    text += seg.get("data", {}).get("text", "")
                elif isinstance(seg, MessageSegment) and seg.type == "text":
                    text += str(seg)
        else:
            text = str(message)
        
        match_result = bool(re.search(pattern, text, flags))
        
        return match_result
    
    return _regex_checker


def on_startswith(
    msg: Union[str, tuple[str, ...]],
    priority: int = 1,
    block: bool = True,
) -> Matcher:
    """注册一个匹配消息开头的事件处理器"""
    matcher = Matcher(type_="message", priority=priority, block=block)
    # 添加规则检查器
    checker = startswith(msg)
    
    # 重写 check_perm 方法以包含规则检查
    original_check_perm = matcher.check_perm
    
    async def check_perm_with_rule(event: Event) -> bool:
        base_perm = await original_check_perm(event)
        return base_perm and checker(event)
    
    matcher.check_perm = check_perm_with_rule
    _register_matcher(matcher)
    return matcher


def on_endswith(
    msg: Union[str, tuple[str, ...]],
    priority: int = 1,
    block: bool = True,
) -> Matcher:
    """注册一个匹配消息结尾的事件处理器"""
    matcher = Matcher(type_="message", priority=priority, block=block)
    # 添加规则检查器
    checker = endswith(msg)
    
    # 重写 check_perm 方法以包含规则检查
    original_check_perm = matcher.check_perm
    
    async def check_perm_with_rule(event: Event) -> bool:
        base_perm = await original_check_perm(event)
        return base_perm and checker(event)
    
    matcher.check_perm = check_perm_with_rule
    _register_matcher(matcher)
    return matcher


def on_fullmatch(
    msg: Union[str, tuple[str, ...]],
    priority: int = 1,
    block: bool = True,
) -> Matcher:
    """注册一个完全匹配消息的事件处理器"""
    matcher = Matcher(type_="message", priority=priority, block=block)
    # 添加规则检查器
    checker = fullmatch(msg)
    
    # 重写 check_perm 方法以包含规则检查
    original_check_perm = matcher.check_perm
    
    async def check_perm_with_rule(event: Event) -> bool:
        base_perm = await original_check_perm(event)
        return base_perm and checker(event)
    
    matcher.check_perm = check_perm_with_rule
    _register_matcher(matcher)
    return matcher


def on_keyword(
    keywords: Set[str],
    priority: int = 1,
    block: bool = True,
) -> Matcher:
    """注册一个匹配关键词的事件处理器"""
    matcher = Matcher(type_="message", priority=priority, block=block)
    # 添加规则检查器
    checker = keyword(keywords)
    
    # 重写 check_perm 方法以包含规则检查
    original_check_perm = matcher.check_perm
    
    async def check_perm_with_rule(event: Event) -> bool:
        base_perm = await original_check_perm(event)
        return base_perm and checker(event)
    
    matcher.check_perm = check_perm_with_rule
    _register_matcher(matcher)
    return matcher


def on_command(
    cmd: Union[str, tuple[str, ...]],
    priority: int = 1,
    block: bool = True,
) -> Matcher:
    """注册一个匹配命令的事件处理器"""
    matcher = Matcher(type_="message", priority=priority, block=block)
    # 添加规则检查器
    checker = command(cmd)
    
    # 重写 check_perm 方法以包含规则检查
    original_check_perm = matcher.check_perm
    
    async def check_perm_with_rule(event: Event) -> bool:
        base_perm = await original_check_perm(event)
        return base_perm and checker(event)
    
    matcher.check_perm = check_perm_with_rule
    _register_matcher(matcher)
    return matcher


def on_regex(
    pattern: str,
    flags: Union[int, re.RegexFlag] = 0,
    priority: int = 1,
    block: bool = True,
) -> Matcher:
    """注册一个正则表达式匹配的事件处理器"""
    matcher = Matcher(type_="message", priority=priority, block=block)
    # 添加规则检查器
    checker = regex(pattern, flags)
    
    # 重写 check_perm 方法以包含规则检查
    original_check_perm = matcher.check_perm
    
    async def check_perm_with_rule(event: Event) -> bool:
        base_perm = await original_check_perm(event)
        return base_perm and checker(event)
    
    matcher.check_perm = check_perm_with_rule
    _register_matcher(matcher)
    return matcher


# 导出常用类和函数
__all__ = [
    "Matcher",
    "on",
    "on_message",
    "on_notice",
    "on_request",
    "on_metaevent",
    "on_startswith",
    "on_endswith",
    "on_fullmatch",
    "on_keyword",
    "on_command",
    "on_regex",
    "startswith",
    "endswith",
    "fullmatch",
    "keyword",
    "command",
    "regex",
    "handle_event",
]