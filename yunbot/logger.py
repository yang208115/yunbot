"""YunBot 日志模块。

此模块提供了独立的日志功能，支持彩色输出、文件轮转和自定义格式。
基于 loguru 实现，采用分层架构设计，支持真正的多实例隔离。

主要组件：
    - LevelRegistry: 统一管理所有日志级别
    - FormatManager: 管理日志格式字符串
    - HandlerManager: 管理 handler 生命周期
    - LoggerManager: 管理 logger 实例
    - YunBotLogger: 公共 API 接口层

典型用法：
    >>> from yunbot.logger import get_logger
    >>> logger = get_logger("App").setup(level="INFO")
    >>> logger.info("应用启动")
"""

import sys
import os
import threading
from typing import Optional, Any, Dict, Callable, List
from loguru import logger as _loguru_logger


# ============================================================================
# 常量定义
# ============================================================================

SUCCESS_LEVEL = 25  # SUCCESS 级别数值


# ============================================================================
# 自定义异常
# ============================================================================

class LoggerNotConfiguredError(RuntimeError):
    """Logger 未配置异常。"""
    pass


class InvalidLogLevelError(ValueError):
    """无效的日志级别异常。"""
    pass


class LoggerConfigError(RuntimeError):
    """Logger 配置错误异常。"""
    pass


# ============================================================================
# 核心组件
# ============================================================================

class LevelRegistry:
    """级别注册中心,统一管理所有日志级别。
    
    职责:
        - 注册新的日志级别到 loguru
        - 存储级别的数值和颜色信息
        - 提供级别查询接口
        - 确保级别注册的线程安全
    
    Attributes:
        _levels (Dict[str, Dict[str, Any]]): 存储级别名称到级别信息的映射
        _lock (threading.Lock): 保护级别注册的线程锁
        _initialized (bool): 标记标准级别是否已初始化
    """
    
    def __init__(self):
        """初始化级别注册中心。"""
        self._levels: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()
        self._initialized = False
    
    def initialize_standard_levels(self) -> None:
        """初始化标准日志级别。
        
        包括: DEBUG(10), INFO(20), SUCCESS(25), WARNING(30), ERROR(40), CRITICAL(50)
        """
        if self._initialized:
            return
        
        with self._lock:
            if self._initialized:  # 双重检查
                return
            
            # 标准级别定义
            standard_levels = [
                ("DEBUG", 10, "<cyan>"),
                ("INFO", 20, "<white>"),
                ("SUCCESS", 25, "<white>"),
                ("WARNING", 30, "<yellow>"),
                ("ERROR", 40, "<red>"),
                ("CRITICAL", 50, "<bold><red>"),
            ]
            
            for name, level, color in standard_levels:
                try:
                    _loguru_logger.level(name)
                    # 级别已存在,仅存储信息
                    self._levels[name] = {"no": level, "color": color, "icon": "●"}
                except ValueError:
                    # 级别不存在,需要注册
                    _loguru_logger.level(name, no=level, color=color, icon="●")
                    self._levels[name] = {"no": level, "color": color, "icon": "●"}
            
            self._initialized = True
    
    def register_level(self, name: str, level: int, color: str = "<white>") -> None:
        """注册自定义日志级别。
        
        Args:
            name: 级别名称(将自动转换为大写)
            level: 级别数值(数值越大优先级越高)
            color: loguru 颜色标签,默认为白色
        """
        upper_name = name.upper()
        
        with self._lock:
            # 检查级别是否已存在
            if upper_name in self._levels:
                # 更新颜色信息
                self._levels[upper_name]["color"] = color
                return
            
            # 尝试注册新级别到 loguru
            try:
                _loguru_logger.level(upper_name, no=level, color=color, icon="●")
            except ValueError:
                # 级别存在于 loguru 但不在我们的注册表中
                # 这是合法的,只需添加到我们的注册表
                pass
            except Exception as e:
                raise LoggerConfigError(f"Failed to register level '{upper_name}': {e}")
            
            # 存储级别信息
            self._levels[upper_name] = {"no": level, "color": color, "icon": "●"}
    
    def is_registered(self, name: str) -> bool:
        """检查级别是否已注册。
        
        Args:
            name: 级别名称
            
        Returns:
            bool: 级别是否已注册
        """
        return name.upper() in self._levels
    
    def get_level_info(self, name: str) -> Optional[Dict[str, Any]]:
        """获取级别信息。
        
        Args:
            name: 级别名称
            
        Returns:
            Optional[Dict]: 级别信息,如果未注册则返回 None
        """
        return self._levels.get(name.upper())
    
    def get_all_levels(self) -> Dict[str, Dict[str, Any]]:
        """获取所有已注册级别。
        
        Returns:
            Dict: 所有级别信息
        """
        return self._levels.copy()


class FormatManager:
    """格式管理器,管理日志格式字符串和格式化逻辑。
    
    职责:
        - 提供默认的控制台和文件格式字符串
        - 支持自定义格式字符串
        - 处理 loguru 特殊标签
    """
    
    # 默认控制台格式(带颜色)
    DEFAULT_CONSOLE_FORMAT = (
        "<green>{time:MM-DD HH:mm:ss}</green> "
        "<level>[{level}]</level> "
        "<cyan>{extra[logger_name]}</cyan> | "
        "<cyan>{function}:{line}</cyan> | "
        "<white>{message}</white>"
    )
    
    # 默认文件格式(纯文本)
    DEFAULT_FILE_FORMAT = (
        "{time:YYYY-MM-DD HH:mm:ss} "
        "[{level}] "
        "{extra[logger_name]} | "
        "{function}:{line} | "
        "{message}"
    )
    
    @staticmethod
    def get_console_format(custom_format: Optional[str] = None) -> str:
        """获取控制台格式字符串。
        
        Args:
            custom_format: 自定义格式字符串,如果为 None 则使用默认格式
            
        Returns:
            str: 格式字符串
        """
        return custom_format if custom_format else FormatManager.DEFAULT_CONSOLE_FORMAT
    
    @staticmethod
    def get_file_format(custom_format: Optional[str] = None) -> str:
        """获取文件格式字符串。
        
        Args:
            custom_format: 自定义格式字符串,如果为 None 则使用默认格式
            
        Returns:
            str: 格式字符串
        """
        return custom_format if custom_format else FormatManager.DEFAULT_FILE_FORMAT


class HandlerManager:
    """处理器管理器,管理每个 logger 实例的 handler。
    
    职责:
        - 为每个 logger 实例创建独立的 handler ID
        - 通过过滤器实现实例隔离
        - 支持动态添加和移除 handler
        - 管理文件 handler 的轮转配置
    
    Attributes:
        _handler_ids (Dict[str, List[int]]): logger 名称到 handler ID 列表的映射
        _lock (threading.Lock): 保护 handler 操作的线程锁
    """
    
    def __init__(self):
        """初始化处理器管理器。"""
        self._handler_ids: Dict[str, List[int]] = {}
        self._lock = threading.Lock()
    
    def add_console_handler(
        self,
        logger_name: str,
        level: str,
        format_str: str
    ) -> int:
        """添加控制台 handler。
        
        Args:
            logger_name: logger 名称
            level: 日志级别
            format_str: 格式字符串
            
        Returns:
            int: handler ID
        """
        # 创建 filter 函数,只处理匹配的日志
        def logger_filter(record):
            return record["extra"].get("logger_name") == logger_name
        
        # 添加控制台 handler
        handler_id = _loguru_logger.add(
            sys.stdout,
            format=format_str,
            level=level.upper(),
            colorize=True,
            filter=logger_filter
        )
        
        # 保存 handler ID
        with self._lock:
            if logger_name not in self._handler_ids:
                self._handler_ids[logger_name] = []
            self._handler_ids[logger_name].append(handler_id)
        
        return handler_id
    
    def add_file_handler(
        self,
        logger_name: str,
        level: str,
        format_str: str,
        log_file: str,
        rotation: int,
        retention: int,
        encoding: str = "utf-8"
    ) -> int:
        """添加文件 handler。
        
        Args:
            logger_name: logger 名称
            level: 日志级别
            format_str: 格式字符串
            log_file: 日志文件路径
            rotation: 轮转大小(字节)
            retention: 保留文件数量
            encoding: 文件编码
            
        Returns:
            int: handler ID
        """
        # 创建 filter 函数,只处理匹配的日志
        def logger_filter(record):
            return record["extra"].get("logger_name") == logger_name
        
        # 添加文件 handler
        handler_id = _loguru_logger.add(
            log_file,
            format=format_str,
            level=level.upper(),
            filter=logger_filter,
            rotation=rotation,
            retention=retention,
            encoding=encoding,
            enqueue=True  # 线程安全的异步写入
        )
        
        # 保存 handler ID
        with self._lock:
            if logger_name not in self._handler_ids:
                self._handler_ids[logger_name] = []
            self._handler_ids[logger_name].append(handler_id)
        
        return handler_id
    
    def remove_handlers(self, logger_name: str) -> None:
        """移除指定 logger 的所有 handler。
        
        Args:
            logger_name: logger 名称
        """
        with self._lock:
            if logger_name not in self._handler_ids:
                return
            
            # 复制列表避免迭代时修改
            handler_ids = self._handler_ids[logger_name].copy()
            
            # 移除所有 handler
            for handler_id in handler_ids:
                try:
                    _loguru_logger.remove(handler_id)
                except ValueError:
                    # handler 已被移除,忽略
                    pass
            
            # 清空列表
            self._handler_ids[logger_name].clear()
    
    def get_handler_ids(self, logger_name: str) -> List[int]:
        """获取指定 logger 的 handler ID 列表。
        
        Args:
            logger_name: logger 名称
            
        Returns:
            List[int]: handler ID 列表
        """
        with self._lock:
            return self._handler_ids.get(logger_name, []).copy()


class LoggerManager:
    """日志记录器管理,管理 YunBotLogger 实例的生命周期和配置。
    
    职责:
        - 维护 logger 实例的注册表
        - 协调各个管理器完成配置
        - 提供 logger 查询接口
        - 管理默认 logger 实例
    
    Attributes:
        _instances (Dict[str, YunBotLogger]): 名称到实例的映射
        _instance_configs (Dict[str, Dict[str, Any]]): 实例配置信息
        _lock (threading.Lock): 保护注册表的线程锁
    """
    
    def __init__(self):
        """初始化日志记录器管理。"""
        self._instances: Dict[str, "YunBotLogger"] = {}
        self._instance_configs: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()
    
    def get_instance(self, name: str) -> "YunBotLogger":
        """获取或创建 logger 实例。
        
        Args:
            name: logger 名称
            
        Returns:
            YunBotLogger: logger 实例
        """
        # 快速路径:无锁检查
        if name in self._instances:
            return self._instances[name]
        
        # 慢速路径:加锁创建
        with self._lock:
            # 双重检查
            if name in self._instances:
                return self._instances[name]
            
            # 创建新实例
            instance = YunBotLogger._create_instance(name)
            self._instances[name] = instance
            return instance
    
    def has_instance(self, name: str) -> bool:
        """检查实例是否存在。
        
        Args:
            name: logger 名称
            
        Returns:
            bool: 实例是否存在
        """
        return name in self._instances
    
    def get_all_instances(self) -> Dict[str, "YunBotLogger"]:
        """获取所有实例。
        
        Returns:
            Dict: 所有 logger 实例
        """
        return self._instances.copy()
    
    def remove_instance(self, name: str) -> None:
        """移除实例及其 handler。
        
        Args:
            name: logger 名称
        """
        with self._lock:
            if name in self._instances:
                # 移除 handler
                _handler_manager.remove_handlers(name)
                # 删除实例
                del self._instances[name]
                if name in self._instance_configs:
                    del self._instance_configs[name]


class YunBotLogger:
    """YunBot 日志记录器,提供公共 API 接口层。
    
    支持:
        - 多实例隔离
        - 配置热更新
        - 动态日志级别
        - 标准日志方法(debug, info, warning, error, critical, exception, success)
    
    Attributes:
        name (str): Logger 名称
        _config (Dict[str, Any]): 当前配置
        _handler_ids (List[int]): Handler ID 列表
        _config_lock (threading.Lock): 配置更新锁
        _configured (bool): 是否已配置
        _method_cache (Dict[str, Callable]): 动态方法缓存
    """
    
    # 属性注解,供类型检查器识别
    name: str
    _configured: bool
    _config: Dict[str, Any]
    _handler_ids: List[int]
    _config_lock: threading.Lock
    _method_cache: Dict[str, Callable]
    
    @staticmethod
    def _create_instance(name: str) -> "YunBotLogger":
        """创建新实例(内部方法)。
        
        Args:
            name: logger 名称
            
        Returns:
            YunBotLogger: 新实例
        """
        instance = object.__new__(YunBotLogger)
        instance.name = name
        instance._configured = False
        instance._config = {}
        instance._handler_ids = []
        instance._config_lock = threading.Lock()
        instance._method_cache = {}
        return instance
    
    def __new__(cls, name: str = "YunBot") -> "YunBotLogger":
        """获取或创建 logger 实例。
        
        Args:
            name: logger 名称
            
        Returns:
            YunBotLogger: logger 实例
        """
        return _logger_manager.get_instance(name)
    
    def setup(
        self,
        level: str = "INFO",
        format_string: Optional[str] = None,
        log_to_file: bool = False,
        log_dir: str = "logs",
        max_size: int = 10 * 1024 * 1024,  # 10MB
        backup_count: int = 5
    ) -> "YunBotLogger":
        """设置日志记录(可多次调用)。
        
        Args:
            level: 日志级别,可选值为 DEBUG, INFO, SUCCESS, WARNING, ERROR, CRITICAL
            format_string: 日志格式字符串,如果为 None 则使用默认格式
            log_to_file: 是否将日志写入文件
            log_dir: 日志文件目录
            max_size: 单个日志文件的最大大小(字节)
            backup_count: 保留的日志文件数量
            
        Returns:
            YunBotLogger: 配置好的日志记录器实例
            
        Raises:
            InvalidLogLevelError: 无效的日志级别
            LoggerConfigError: 配置参数错误
        """
        # 验证参数
        upper_level = level.upper()
        if not _level_registry.is_registered(upper_level):
            available_levels = ", ".join(_level_registry.get_all_levels().keys())
            raise InvalidLogLevelError(
                f"Invalid log level '{level}'. Available levels: {available_levels}"
            )
        
        if max_size <= 0:
            raise LoggerConfigError("max_size must be greater than 0")
        
        if backup_count < 0:
            raise LoggerConfigError("backup_count must be greater than or equal to 0")
        
        with self._config_lock:
            # 移除旧 handler
            _handler_manager.remove_handlers(self.name)
            self._handler_ids.clear()
            
            # 获取格式字符串
            console_format = _format_manager.get_console_format(format_string)
            
            # 添加控制台 handler
            handler_id = _handler_manager.add_console_handler(
                self.name,
                upper_level,
                console_format
            )
            self._handler_ids.append(handler_id)
            
            # 添加文件 handler(如果需要)
            if log_to_file:
                # 创建日志目录
                try:
                    if not os.path.exists(log_dir):
                        os.makedirs(log_dir, exist_ok=True)
                except Exception as e:
                    raise LoggerConfigError(f"Failed to create log directory '{log_dir}': {e}")
                
                # 文件名包含日期
                log_file = os.path.join(log_dir, f"{self.name}_{{time:YYYYMMDD}}.log")
                file_format = _format_manager.get_file_format(format_string)
                
                # Windows 下使用 UTF-8-BOM 编码
                encoding = "utf-8-sig" if os.name == 'nt' else "utf-8"
                
                handler_id = _handler_manager.add_file_handler(
                    self.name,
                    upper_level,
                    file_format,
                    log_file,
                    max_size,
                    backup_count,
                    encoding
                )
                self._handler_ids.append(handler_id)
            
            # 保存配置
            self._config = {
                "level": upper_level,
                "format_string": format_string,
                "log_to_file": log_to_file,
                "log_dir": log_dir,
                "max_size": max_size,
                "backup_count": backup_count,
            }
            self._configured = True
        
        return self
    
    def _check_configured(self) -> None:
        """检查 logger 是否已配置。
        
        Raises:
            LoggerNotConfiguredError: Logger 未配置
        """
        if not self._configured:
            raise LoggerNotConfiguredError(
                f"Logger '{self.name}' is not configured. Please call setup() first."
            )
    
    def debug(self, message: str, *args: Any, **kwargs: Any) -> None:
        """记录 DEBUG 级别日志。
        
        Args:
            message: 日志消息,支持 {} 风格格式化
            *args: 位置参数
            **kwargs: 关键字参数
        """
        self._check_configured()
        _loguru_logger.bind(logger_name=self.name).debug(message, *args, **kwargs)
    
    def info(self, message: str, *args: Any, **kwargs: Any) -> None:
        """记录 INFO 级别日志。
        
        Args:
            message: 日志消息,支持 {} 风格格式化
            *args: 位置参数
            **kwargs: 关键字参数
        """
        self._check_configured()
        _loguru_logger.bind(logger_name=self.name).info(message, *args, **kwargs)
    
    def warning(self, message: str, *args: Any, **kwargs: Any) -> None:
        """记录 WARNING 级别日志。
        
        Args:
            message: 日志消息,支持 {} 风格格式化
            *args: 位置参数
            **kwargs: 关键字参数
        """
        self._check_configured()
        _loguru_logger.bind(logger_name=self.name).warning(message, *args, **kwargs)
    
    def error(self, message: str, *args: Any, **kwargs: Any) -> None:
        """记录 ERROR 级别日志。
        
        Args:
            message: 日志消息,支持 {} 风格格式化
            *args: 位置参数
            **kwargs: 关键字参数
        """
        self._check_configured()
        _loguru_logger.bind(logger_name=self.name).error(message, *args, **kwargs)
    
    def critical(self, message: str, *args: Any, **kwargs: Any) -> None:
        """记录 CRITICAL 级别日志。
        
        Args:
            message: 日志消息,支持 {} 风格格式化
            *args: 位置参数
            **kwargs: 关键字参数
        """
        self._check_configured()
        _loguru_logger.bind(logger_name=self.name).critical(message, *args, **kwargs)
    
    def exception(self, message: str, *args: Any, **kwargs: Any) -> None:
        """记录异常日志(含堆栈信息)。
        
        Args:
            message: 日志消息,支持 {} 风格格式化
            *args: 位置参数
            **kwargs: 关键字参数
        """
        self._check_configured()
        _loguru_logger.bind(logger_name=self.name).exception(message, *args, **kwargs)
    
    def success(self, message: str, *args: Any, **kwargs: Any) -> None:
        """记录 SUCCESS 级别日志。
        
        Args:
            message: 日志消息,支持 {} 风格格式化
            *args: 位置参数
            **kwargs: 关键字参数
        """
        self._check_configured()
        _loguru_logger.bind(logger_name=self.name).log("SUCCESS", message, *args, **kwargs)
    
    def __getattr__(self, name: str) -> Callable:
        """动态创建自定义级别方法。
        
        Args:
            name: 方法名(小写的级别名称)
            
        Returns:
            Callable: 日志方法
            
        Raises:
            AttributeError: 级别未注册或方法不存在
        """
        # 内部属性,直接抛出 AttributeError
        if name.startswith("_"):
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")
        
        # 检查缓存
        if name in self._method_cache:
            return self._method_cache[name]
        
        # 检查级别是否已注册
        upper_name = name.upper()
        if not _level_registry.is_registered(upper_name):
            raise AttributeError(
                f"Log level '{upper_name}' is not registered. "
                f"Use register_logger_level() to register it first."
            )
        
        # 创建动态方法
        def log_method(message: str, *args: Any, **kwargs: Any) -> None:
            self._check_configured()
            _loguru_logger.bind(logger_name=self.name).log(upper_name, message, *args, **kwargs)
        
        # 缓存方法
        self._method_cache[name] = log_method
        return log_method


# ============================================================================
# 模块级函数
# ============================================================================

def get_logger(name: str = "YunBot") -> YunBotLogger:
    """获取日志记录器实例。
    
    相同名称的 logger 仅创建一次。
    
    Args:
        name: 日志记录器名称
        
    Returns:
        YunBotLogger: 日志记录器实例
    """
    return YunBotLogger(name)


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


def register_logger_level(name: str, level: int, color: str = "<white>") -> None:
    """注册自定义日志级别。
    
    Args:
        name: 级别名称（将自动转换为大写）
        level: 级别数值（数值越大优先级越高）
        color: loguru 颜色标签，默认为白色
    """
    _level_registry.register_level(name, level, color)


def success(message: str, *args: Any, **kwargs: Any) -> None:
    """使用默认 logger 记录 SUCCESS 级别日志。
    
    Args:
        message: 日志消息，支持 {} 风格格式化
        *args: 位置参数
        **kwargs: 关键字参数
    """
    default_logger.success(message, *args, **kwargs)


def log_success(message: str, *args: Any, **kwargs: Any) -> None:
    """使用默认 logger 记录 SUCCESS 级别日志（别名）。
    
    Args:
        message: 日志消息，支持 {} 风格格式化
        *args: 位置参数
        **kwargs: 关键字参数
    """
    default_logger.success(message, *args, **kwargs)


# ============================================================================
# 模块初始化
# ============================================================================

# 创建全局管理器实例
_level_registry = LevelRegistry()
_format_manager = FormatManager()
_handler_manager = HandlerManager()
_logger_manager = LoggerManager()

# 移除 loguru 默认 handler
_loguru_logger.remove()

# 初始化标准级别
_level_registry.initialize_standard_levels()

# 创建并自动配置默认 logger
default_logger = YunBotLogger("YunBot").setup(level="INFO")


# ============================================================================
# 导出
# ============================================================================

__all__ = [
    # 类
    "YunBotLogger",
    # 函数
    "get_logger",
    "setup_logging",
    "register_logger_level",
    "success",
    "log_success",
    # 变量
    "default_logger",
    "SUCCESS_LEVEL",
    # 异常
    "LoggerNotConfiguredError",
    "InvalidLogLevelError",
    "LoggerConfigError",
]