"""YunBot 日志模块。

此模块提供了独立的日志功能，支持彩色输出、文件轮转和自定义格式。
"""

import logging
import os
import sys
from datetime import datetime
from logging.handlers import RotatingFileHandler
from typing import Optional, Any, Dict


class ColoredFormatter(logging.Formatter):
    """带颜色的日志格式化器。
    
    为不同级别的日志添加不同的颜色，使日志更易于阅读。
    """

    # 颜色代码
    COLORS = {
        'DEBUG': '\033[36m',     # 青色
        'INFO': '\033[37m',      # 白色
        'SUCCESS': '\033[37m',   # 白色（自定义级别）
        'WARNING': '\033[33m',   # 黄色
        'ERROR': '\033[31m',     # 红色
        'CRITICAL': '\033[35m',  # 紫色
    }
    
    # 特定部分的颜色
    TIME_COLOR = '\033[32m'       # 绿色
    MODULE_COLOR = '\033[94m'     # 淡蓝色
    FUNCTION_COLOR = '\033[94m'   # 淡蓝色
    MESSAGE_COLOR = '\033[37m'    # 白色
    RESET = '\033[0m'

    def format(self, record: logging.LogRecord) -> str:
        """格式化日志记录。
        
        Args:
            record: 日志记录对象
            
        Returns:
            str: 格式化后的日志字符串
        """
        # 获取原始格式化的日志
        log_message = super().format(record)
        
        if sys.stdout.isatty():
            # 解析日志消息的各个部分
            # 格式: 时间 [级别] 模块名 | 函数名:行号 | 消息内容
            import re
            
            # 匹配日志格式的正则表达式
            pattern = r'(\d{2}-\d{2} \d{2}:\d{2}:\d{2}) \[([A-Z]+)\] ([^|]+) \| ([^:]+):(\d+) \| (.*)'
            match = re.match(pattern, log_message)
            
            if match:
                time_part, level_part, module_part, func_part, line_part, message_part = match.groups()
                
                # 特殊处理：确保 exception 方法始终使用 ERROR 级别
                if hasattr(record, 'funcName') and record.funcName == "exception":
                    level_part = "ERROR"
                
                # 应用颜色
                colored_time = f"{self.TIME_COLOR}{time_part}{self.RESET}"
                # 级别使用原有颜色，如果未定义则检查动态颜色，否则使用白色
                if level_part in self.COLORS:
                    level_color = self.COLORS[level_part]
                elif level_part in _dynamic_colors:
                    level_color = _dynamic_colors[level_part]
                else:
                    level_color = '\033[37m'  # 默认白色
                
                colored_level = f"{level_color}[{level_part}]{self.RESET}"
                colored_module = f"{self.MODULE_COLOR}{module_part.strip()}{self.RESET}"
                colored_function = f"{self.FUNCTION_COLOR}{func_part}:{line_part}{self.RESET}"
                colored_message = f"{self.MESSAGE_COLOR}{message_part}{self.RESET}"
                
                # 重新组合日志消息
                return f"{colored_time} {colored_level} {colored_module} | {colored_function} | {colored_message}"
            else:
                # 如果不匹配预期格式，使用原有逻辑
                if record.levelname in self.COLORS:
                    level_color = self.COLORS[record.levelname]
                elif record.levelname in _dynamic_colors:
                    level_color = _dynamic_colors[record.levelname]
                else:
                    level_color = '\033[37m'  # 默认白色
                
                if level_color:
                    return f"{level_color}{log_message}{self.RESET}"
        
        return log_message


# 添加自定义日志级别
SUCCESS_LEVEL = 25  # 在 INFO(20) 和 WARNING(30) 之间

# 动态日志级别存储
_dynamic_levels: Dict[str, int] = {}
# 动态日志级别颜色存储
_dynamic_colors: Dict[str, str] = {}


def success(self: logging.Logger, message: str, *args: Any, **kwargs: Any) -> None:
    """记录 SUCCESS 级别日志"""
    if self.isEnabledFor(SUCCESS_LEVEL):
        self._log(SUCCESS_LEVEL, message, args, **kwargs)


def log_success(message: str, *args: Any, **kwargs: Any) -> None:
    """记录 SUCCESS 级别日志（模块级别函数）"""
    logging.log(SUCCESS_LEVEL, message, *args, **kwargs)


def register_logger_level(name: str, level: int, color: str = '\033[37m') -> None:
    """注册自定义日志级别
    
    Args:
        name: 级别名称
        level: 数值级别
        color: 颜色代码，默认为白色
    """
    # 转换名称为大写以保持一致性
    upper_name = name.upper()
    
    # 存储级别和颜色信息
    _dynamic_levels[upper_name] = level
    _dynamic_colors[upper_name] = color
    
    # 在 logging 模块中注册新级别
    logging.addLevelName(level, upper_name)
    
    # 创建对应的日志方法
    def level_method(self: logging.Logger, message: str, *args: Any, **kwargs: Any) -> None:
        if self.isEnabledFor(level):
            self._log(level, message, args, **kwargs)
    
    # 添加到 Logger 类
    setattr(logging.Logger, name.lower(), level_method)
    
    # 添加模块级别的函数
    def log_level_method(message: str, *args: Any, **kwargs: Any) -> None:
        logging.log(level, message, *args, **kwargs)
    
    setattr(logging, name.lower(), log_level_method)


# 添加到 logging 模块
logging.addLevelName(SUCCESS_LEVEL, 'SUCCESS')
logging.Logger.success = success  # type: ignore
logging.success = log_success  # type: ignore


class YunBotLogger:
    """YunBot 日志记录器"""
    
    def __init__(self, name: str = "YunBot"):
        """初始化日志记录器
        
        Args:
            name: 日志记录器名称
        """
        self.name = name
        self.logger = logging.getLogger(name)
        self._configured = False
    
    def setup(
        self,
        level: str = "INFO",
        format_string: Optional[str] = None,
        log_to_file: bool = False,
        log_dir: str = "logs",
        max_size: int = 10 * 1024 * 1024,  # 10MB
        backup_count: int = 5
    ) -> "YunBotLogger":
        """设置日志记录。
        
        Args:
            level: 日志级别，可选值为 DEBUG, INFO, SUCCESS, WARNING, ERROR, CRITICAL
            format_string: 日志格式字符串，如果为 None 则使用默认格式
            log_to_file: 是否将日志写入文件
            log_dir: 日志文件目录
            max_size: 单个日志文件的最大大小（字节）
            backup_count: 保留的日志文件数量
            
        Returns:
            YunBotLogger: 配置好的日志记录器实例
        """
        if self._configured:
            # 如果已经配置过，先清除现有的处理器
            for handler in self.logger.handlers[:]:
                self.logger.removeHandler(handler)
        
        # 设置日志级别
        level_num = getattr(logging, level.upper(), logging.INFO)
        self.logger.setLevel(level_num)
        
        # 设置日志格式
        if format_string is None:
            # 使用用户要求的格式：时间 + 级别 + 模块名 + 函数名:行号 | 消息内容
            format_string = (
                "%(asctime)s [%(levelname)s] %(name)s | %(funcName)s:%(lineno)d | %(message)s"
            )
        
        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(ColoredFormatter(format_string, datefmt="%m-%d %H:%M:%S"))
        self.logger.addHandler(console_handler)
        
        # 文件处理器（可选）
        if log_to_file:
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
            
            log_file = os.path.join(log_dir, f"{self.name}_{datetime.now().strftime('%Y%m%d')}.log")
            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=max_size,
                backupCount=backup_count,
                encoding='utf-8'  # 确保使用UTF-8编码
            )
            file_handler.setFormatter(logging.Formatter(format_string, datefmt="%Y-%m-%d %H:%M:%S"))
            self.logger.addHandler(file_handler)
        
        self._configured = True
        return self
    
    def debug(self, message: str, *args: Any, **kwargs: Any) -> None:
        """记录 DEBUG 级别日志"""
        self.logger.debug(message, *args, **kwargs)
    
    def info(self, message: str, *args: Any, **kwargs: Any) -> None:
        """记录 INFO 级别日志"""
        self.logger.info(message, *args, **kwargs)
    
    def warning(self, message: str, *args: Any, **kwargs: Any) -> None:
        """记录 WARNING 级别日志"""
        self.logger.warning(message, *args, **kwargs)
    
    def error(self, message: str, *args: Any, **kwargs: Any) -> None:
        """记录 ERROR 级别日志"""
        self.logger.error(message, *args, **kwargs)
    
    def critical(self, message: str, *args: Any, **kwargs: Any) -> None:
        """记录 CRITICAL 级别日志"""
        self.logger.critical(message, *args, **kwargs)
    
    def exception(self, message: str, *args: Any, **kwargs: Any) -> None:
        """记录异常日志（自动包含调用栈信息）"""
        # 确保使用 ERROR 级别记录异常
        kwargs['exc_info'] = kwargs.get('exc_info', True)
        self.logger.error(message, *args, **kwargs)
    
    def __getattr__(self, name: str) -> Any:
        """动态添加日志级别方法
        
        通过此方法动态处理自定义日志级别，支持任意名称的日志级别
        
        Args:
            name: 要访问的属性名称
            
        Returns:
            对应的日志方法或抛出 AttributeError
        """
        # 处理已知的自定义日志级别
        if name == "success":
            def success_method(message: str, *args: Any, **kwargs: Any) -> None:
                """记录 SUCCESS 级别日志"""
                # 确保 logger 有 success 方法
                if hasattr(self.logger, 'success'):
                    self.logger.success(message, *args, **kwargs)  # type: ignore
                else:
                    # 如果没有 success 方法，使用 log 方法直接记录
                    self.logger.log(SUCCESS_LEVEL, message, *args, **kwargs)
            return success_method
            
        # 处理标准日志方法，避免被当作动态级别处理
        if name in ['debug', 'info', 'warning', 'error', 'critical', 'exception']:
            # 对于标准日志方法，直接抛出异常，因为它们应该在类中明确定义
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
        
        # 动态处理通过 register_logger_level 注册的级别
        upper_name = name.upper()
        if upper_name in _dynamic_levels:
            level = _dynamic_levels[upper_name]
            def registered_method(message: str, *args: Any, **kwargs: Any) -> None:
                """记录注册的自定义级别日志"""
                self.logger.log(level, message, *args, **kwargs)
            return registered_method
        
        # 动态创建任意名称的日志级别
        # 检查是否为有效的日志方法名（避免访问特殊属性）
        if not name.startswith('_') and name.isidentifier():
            # 为新级别分配一个唯一的级别数值
            # 确保级别数值在合适的范围内（介于 INFO 和 WARNING 之间，或者更高）
            if upper_name not in _dynamic_levels:
                # 为每个新级别分配一个唯一的数值，从 40 开始递增
                base_level = 40
                new_level = base_level + len(_dynamic_levels) * 5
                _dynamic_levels[upper_name] = new_level
                # 默认颜色为白色
                _dynamic_colors[upper_name] = '\033[37m'
                # 在 logging 模块中注册新级别
                logging.addLevelName(new_level, upper_name)
            
            level = _dynamic_levels[upper_name]
            
            def dynamic_method(message: str, *args: Any, **kwargs: Any) -> None:
                """记录动态级别日志"""
                self.logger.log(level, message, *args, **kwargs)
            
            return dynamic_method
        
        # 对于其他未知属性，抛出异常
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")


# 创建默认的日志记录器实例
default_logger = YunBotLogger("YunBot")


def get_logger(name: str = "YunBot") -> YunBotLogger:
    """获取日志记录器实例
    
    Args:
        name: 日志记录器名称
        
    Returns:
        YunBotLogger: 日志记录器实例
    """
    return YunBotLogger(name)


# 为向后兼容保留的函数
def setup_logging(
    level: str = "INFO",
    format_string: Optional[str] = None,
    logger_name: str = "YunBot",
    log_to_file: bool = False,
    log_dir: str = "logs",
    max_size: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5
) -> YunBotLogger:
    """设置日志记录（向后兼容函数）。
    
    Args:
        level: 日志级别
        format_string: 日志格式字符串
        logger_name: 日志记录器名称
        log_to_file: 是否将日志写入文件
        log_dir: 日志文件目录
        max_size: 单个日志文件的最大大小（字节）
        backup_count: 保留的日志文件数量
        
    Returns:
        YunBotLogger: 配置好的日志记录器实例
    """
    logger = YunBotLogger(logger_name)
    return logger.setup(
        level=level,
        format_string=format_string,
        log_to_file=log_to_file,
        log_dir=log_dir,
        max_size=max_size,
        backup_count=backup_count
    )


# 默认导出
__all__ = [
    "YunBotLogger",
    "get_logger",
    "setup_logging",
    "default_logger",
    "SUCCESS_LEVEL",
    "success",
    "log_success",
    "register_logger_level",
]