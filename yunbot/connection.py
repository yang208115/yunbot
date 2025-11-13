"""OneBot v11 客户端适配器的 WebSocket 连接管理。

该模块为 OneBot v11 客户端提供 WebSocket 连接实现。
它处理连接建立、消息发送/接收和事件处理。
"""

import asyncio
from typing import Any, Dict, Optional
import aiohttp
from aiohttp import ClientSession, ClientWebSocketResponse, WSMsgType, ClientTimeout
from yarl import URL

from .config import ConnectionConfig, WebSocketConfig
from .event import Event, parse_event
from .exceptions import NetworkException, ActionFailed
from .utils import generate_request_id, safe_json_loads
from .logger import default_logger as logger
from .store import ResultStore


class WebSocketConnection:
    """OneBot v11 的 WebSocket 连接实现。"""

    def __init__(self, config: WebSocketConfig):
        """初始化 WebSocket 连接。
        
        Args:
            config: WebSocket 配置
        """
        self.config: WebSocketConfig = config
        self._session: Optional[ClientSession] = None
        self._ws: Optional[ClientWebSocketResponse] = None
        self._receive_task: Optional[asyncio.Task] = None
        self._heartbeat_task: Optional[asyncio.Task] = None
        self.connected = False
        self._closed = False
        # 使用 ResultStore 来管理API响应
        self._result_store = ResultStore()

    @property
    def is_connected(self) -> bool:
        """检查连接是否已建立
        
        Returns:
            bool: 如果已连接且未关闭则返回 True，否则返回 False
        """
        return self.connected and not self._closed

    async def connect(self) -> None:
        """建立 WebSocket 连接
        
        该方法使用提供的配置建立 WebSocket 连接。
        它设置会话，连接到 WebSocket 端点，并启动
        接收和心跳循环。
        
        Raises:
            NetworkException: 如果连接失败则抛出
        """
        headers = {}
        if self.config.access_token:
            headers["Authorization"] = f"Bearer {self.config.access_token}"

        self._session = ClientSession(
            headers=headers,
            timeout=ClientTimeout(total=self.config.timeout)
        )

        try:
            self._ws = await self._session.ws_connect(
                self.config.url
            )

            self.connected = True
            self._receive_task = asyncio.create_task(self._receive_loop())

            # 启动心跳
            if self.config.heartbeat_interval and self.config.heartbeat_interval > 0:
                self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())

            logger.info(f"已建立WebSocket连接 {self.config.url}")

        except Exception as e:
            await self.disconnect()
            raise NetworkException(f"WebSocket连接失败: {e}")

    async def disconnect(self) -> None:
        """断开 WebSocket 连接
        
        该方法优雅地断开 WebSocket 连接，
        取消所有运行任务，并清理资源。
        """
        self._closed = True
        self.connected = False

        if self._heartbeat_task:
            self._heartbeat_task.cancel()
            try:
                await self._heartbeat_task
            except asyncio.CancelledError:
                pass

        if self._receive_task:
            self._receive_task.cancel()
            try:
                await self._receive_task
            except asyncio.CancelledError:
                pass

        if self._ws:
            await self._ws.close()

        if self._session:
            await self._session.close()

        # 清理 ResultStore 中的待处理请求
        self._result_store.clear_all()

        logger.info("WebSocket连接已关闭")

    async def send_request(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """发送 WebSocket 请求并等待真实响应
        
        该方法通过 WebSocket 连接发送请求，并使用 ResultStore 机制
        等待响应。
        
        Args:
            action: 要调用的 API 操作
            params: API 调用的参数
            
        Returns:
            Dict[str, Any]: API 响应数据
            
        Raises:
            NetworkException: 如果连接未建立则抛出
            Exception: 如果请求失败则抛出
        """
        if not self.is_connected or not self._ws:
            raise NetworkException("WebSocket 连接未建立")

        request_id = generate_request_id()
        payload = {
            "action": action,
            "params": params,
            "echo": request_id
        }

        try:
            await self._ws.send_json(payload)
            logger.debug(f"发送请求 {request_id}: {action}")

            # 使用 ResultStore 等待真实的 API 响应
            result = await self._result_store.fetch(request_id, timeout=self.config.timeout)

            # 提取 data 字段
            logger.info(f"返回响应:{result}")
            if isinstance(result, dict) and "data" in result:
                return result["data"]
            elif isinstance(result, dict):
                return result
            else:
                return result

        except Exception as e:
            logger.error(f"发送请求失败 {action}: {e}")
            raise

    def add_event_handler(self, handler):
        """添加事件处理器"""
        if not hasattr(self, '_event_handlers'):
            self._event_handlers = []
        self._event_handlers.append(handler)

    async def _handle_event(self, event: Event) -> None:
        """处理事件"""
        if hasattr(self, '_event_handlers'):
            for handler in self._event_handlers:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        # 使用 create_task 避免阻塞事件处理
                        asyncio.create_task(handler(event))
                    else:
                        handler(event)
                except Exception as e:
                    logger.error(f"事件处理器错误: {e}")

    async def _receive_loop(self) -> None:
        """接收消息循环"""
        if not self._ws:
            logger.error("WebSocket 连接未建立")
            return
            
        try:
            async for msg in self._ws:
                if msg.type == WSMsgType.TEXT:
                    # 使用 create_task 避免阻塞接收循环
                    asyncio.create_task(self._handle_message(msg.data))
                elif msg.type == WSMsgType.BINARY:
                    # 使用 create_task 避免阻塞接收循环
                    asyncio.create_task(self._handle_message(msg.data.decode()))
                elif msg.type == WSMsgType.ERROR:
                    if self._ws:
                        logger.error(f"WebSocket 错误: {self._ws.exception()}")
                elif msg.type in (WSMsgType.CLOSE, WSMsgType.CLOSING, WSMsgType.CLOSED):
                    logger.info("WebSocket 连接已关闭")
                    break
        except Exception as e:
            logger.error(f"WebSocket 接收错误: {e}")
        finally:
            self.connected = False

    async def _heartbeat_loop(self) -> None:
        """心跳循环"""
        # 确保心跳间隔不为 None
        heartbeat_interval = self.config.heartbeat_interval or 30.0
        
        try:
            while self.is_connected and self._ws:
                await asyncio.sleep(heartbeat_interval)
                if self.is_connected and self._ws:
                    logger.debug("发送 WebSocket 心跳请求")
                    await self._ws.ping()
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"心跳错误: {e}")

    async def _handle_message(self, data: str) -> None:
        """处理收到的 WebSocket 消息"""
        try:
            message = safe_json_loads(data)
            if not message:
                return

            # 调试：打印所有收到的消息
            logger.info(f"收到消息: {message}")

            # 检查消息类型
            if message.get("post_type") == "meta_event":
                if message.get("meta_event_type") == "heartbeat":
                    # 心跳事件
                    status = message.get('status', {})
                    online = status.get('online', False)
                    good = status.get('good', False)
                    if online and good:
                        logger.info("💓 机器人连接和响应")
                    elif online:
                        logger.info("💓 机器人在线，但可能有问题")
                    else:
                        logger.warning("💓 机器人连接丢失")
                elif message.get("meta_event_type") == "lifecycle":
                    logger.info(f"Bot 机器人生命周期: {message.get('sub_type')}")
                else:
                    logger.debug(f"元事件: {message.get('meta_event_type')}")
            elif message.get("post_type") == "message":
                # 消息事件
                sender = message.get("sender", {}).get("nickname", "Unknown")
                msg_type = message.get("message_type", "unknown")
                logger.info(f"📨 收到{msg_type}消息来自 {sender}")
            else:
                logger.debug(f"收到消息类型: {message.get('post_type', 'unknown')}")

            # 处理 API 响应 - 使用 ResultStore
            if "status" in message and "retcode" in message:
                logger.debug(f"检测到 API 响应: {message}")
                logger.debug(f"当前待处理请求: {self._result_store.get_pending_requests()}")

                # 优先尝试精确匹配 echo
                if self._result_store.add_result(message):
                    logger.debug(f"成功匹配 API 响应: {message.get('echo')}")
                    return

                # 如果精确匹配失败，尝试按顺序匹配
                elif self._result_store.add_result_by_order(message):
                    logger.warning(f"按顺序匹配 API 响应: {message.get('echo')}")
                    return

                # 如果没有匹配的请求
                else:
                    logger.warning(f"收到 API 响应但无待处理请求: {message.get('echo')}")

            # 处理事件
            if "post_type" in message:
                try:
                    event = parse_event(message)
                    # 使用 create_task 避免阻塞消息处理
                    asyncio.create_task(self._handle_event(event))
                except Exception as e:
                    logger.error(f"解析事件失败: {e}")

        except Exception as e:
            logger.error(f"处理 WebSocket 消息失败: {e}")


def create_connection(config: ConnectionConfig) -> WebSocketConnection:
    """创建 WebSocket 连接"""
    if not isinstance(config, WebSocketConfig):
        raise ValueError(f"只支持 WebSocket 连接，不支持: {type(config)}")

    return WebSocketConnection(config)