#!/usr/bin/env python3
"""
OneBot v11 客户端完整功能示例

本示例展示了 YunBot 客户端的所有主要功能：
1. 多种事件处理器（消息、通知、请求、元事件）
2. 消息发送（私聊、群聊）
3. 动态API调用
4. 消息段构建
5. 错误处理
6. 日志记录
"""

import asyncio
import os
import sys

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# 使用新的日志模块
from yunbot.logger import get_logger, setup_logging
from yunbot import OneBotClient, Message, MessageSegment
from yunbot import NetworkException, ActionFailed, ApiNotAvailable

# 设置日志记录器
logger = setup_logging(
    level="INFO",
    format_string="%(asctime)s [%(levelname)s] %(name)s | %(funcName)s:%(lineno)d | %(message)s",
    logger_name="Test"
)


async def main():
    # 创建客户端，不指定 self_id，让系统动态获取
    client = OneBotClient.create_simple_client(
        connection_type="websocket",
        url="ws://8.134.161.25:3001",  # 请替换为实际的 WebSocket 地址
        access_token="Lyf123456",  # 请替换为实际的访问令牌
        heartbeat_interval=30.0,
        timeout=30.0
    )
    
    # 注册消息事件处理器
    @client.on_message
    async def handle_message(event):
        """处理消息事件"""
        try:
            logger.info(f"[{event.time}] 收到消息 from {event.user_id}: {event.message}")
            
            # 提取消息文本内容
            message_text = extract_message_text(event.message)
            
            # 根据消息内容执行不同操作
            if message_text.startswith("/help"):
                await send_help_message(client, event)
            elif message_text.startswith("/echo "):
                await echo_message(client, event, message_text)
            elif message_text.startswith("/info"):
                await send_bot_info(client, event)
            elif message_text.startswith("/image"):
                await send_test_image(client, event)
            elif message_text.startswith("/status"):
                await send_status_info(client, event)
            else:
                await send_welcome_message(client, event, message_text)
                
        except Exception as e:
            logger.error(f"处理消息时出错: {e}", exc_info=True)
    
    # 注册通知事件处理器
    @client.on_notice
    async def handle_notice(event):
        """处理通知事件"""
        logger.info(f"收到通知: {event.notice_type}")
        
        # 处理群成员增加通知
        if event.notice_type == "group_increase":
            welcome_msg = Message([
                MessageSegment.text("欢迎 "),
                MessageSegment.at(event.user_id),
                MessageSegment.text(" 加入群聊！\n"),
                MessageSegment.face(178)  # 笑脸表情
            ])
            await client.send_group_msg(event.group_id, welcome_msg)
    
    # 注册请求事件处理器
    @client.on_request
    async def handle_request(event):
        """处理请求事件"""
        logger.info(f"收到请求: {event.request_type}")
        
        # 自动同意好友请求
        if event.request_type == "friend":
            try:
                await client.set_friend_add_request(
                    flag=event.flag,
                    approve=True,
                    remark=f"新朋友{event.user_id}"
                )
                logger.info(f"已同意好友请求: {event.user_id}")
            except Exception as e:
                logger.error(f"处理好友请求失败: {e}")
    
    # 注册元事件处理器
    @client.on_meta_event
    async def handle_meta_event(event):
        """处理元事件"""
        if event.meta_event_type == "heartbeat":
            logger.info(f"心跳事件 - 状态: {event.status}")
        elif event.meta_event_type == "lifecycle":
            logger.info(f"生命周期事件: {event.sub_type}")
    
    # 启动客户端
    try:
        logger.info("正在启动 OneBot 客户端...")
        await client.start()
        logger.info("客户端启动成功！")
        
        # 持续运行
        await client.run_forever()
        
    except NetworkException as e:
        logger.error(f"网络连接错误: {e}")
    except ActionFailed as e:
        logger.error(f"API 调用失败: {e}")
    except ApiNotAvailable as e:
        logger.error(f"API 不可用: {e}")
    except KeyboardInterrupt:
        logger.info("收到中断信号，正在停止客户端...")
    except Exception as e:
        logger.error(f"未知错误: {e}", exc_info=True)
    finally:
        logger.info("正在关闭客户端...")
        await client.stop()
        logger.info("客户端已关闭")


def extract_message_text(message):
    """从消息中提取纯文本内容"""
    if isinstance(message, str):
        return message
    elif isinstance(message, list):
        # 如果是消息段列表，提取纯文本
        return "".join(
            seg.get("data", {}).get("text", "")
            for seg in message
            if seg.get("type") == "text"
        )
    else:
        return str(message)


async def send_help_message(client, event):
    """发送帮助信息"""
    help_msg = Message([
        MessageSegment.text("🤖 机器人命令帮助:\n\n"),
        MessageSegment.text("📝 基础命令:\n"),
        MessageSegment.text("/help - 显示此帮助信息\n"),
        MessageSegment.text("/echo <内容> - 回显消息\n"),
        MessageSegment.text("/info - 获取机器人信息\n\n"),
        MessageSegment.text("🎨 多媒体命令:\n"),
        MessageSegment.text("/image - 发送测试图片\n\n"),
        MessageSegment.text("📊 状态命令:\n"),
        MessageSegment.text("/status - 获取运行状态\n"),
        MessageSegment.face(178)  # 笑脸表情
    ])
    
    await send_message_to_event(client, event, help_msg)


async def echo_message(client, event, message_text):
    """回显消息"""
    echo_content = message_text[6:]  # 去掉 "/echo " 前缀
    response = Message([
        MessageSegment.text("🔁 回显: "),
        MessageSegment.text(echo_content)
    ])
    
    await send_message_to_event(client, event, response)


async def send_bot_info(client, event):
    """发送机器人信息"""
    try:
        # 获取登录信息
        login_info = await client.get_login_info()
        user_id = login_info.get("user_id", "未知")
        nickname = login_info.get("nickname", "未知")
        
        # 获取版本信息
        version_info = await client.get_version_info()
        app_name = version_info.get("app_name", "未知")
        app_version = version_info.get("app_version", "未知")
        
        info_msg = Message([
            MessageSegment.text("🤖 机器人信息:\n"),
            MessageSegment.text(f"用户ID: {user_id}\n"),
            MessageSegment.text(f"昵称: {nickname}\n"),
            MessageSegment.text(f"应用: {app_name} v{app_version}\n"),
            MessageSegment.face(178)
        ])
        
        await send_message_to_event(client, event, info_msg)
    except Exception as e:
        logger.error(f"获取机器人信息失败: {e}")
        await send_error_message(client, event, "获取机器人信息失败")


async def send_test_image(client, event):
    """发送测试图片"""
    image_msg = Message([
        MessageSegment.text("🖼️ 这是一张测试图片:\n"),
        MessageSegment.image(
            file="https://http.cat/200.jpg",
            type="show"
        )
    ])
    
    await send_message_to_event(client, event, image_msg)


async def send_status_info(client, event):
    """发送状态信息"""
    try:
        # 获取状态信息
        status = await client.get_status()
        good = status.get("good", False)
        online = status.get("online", False)
        
        status_msg = Message([
            MessageSegment.text("📊 运行状态:\n"),
            MessageSegment.text(f"状态良好: {'是' if good else '否'}\n"),
            MessageSegment.text(f"在线: {'是' if online else '否'}\n"),
            MessageSegment.face(178 if good and online else 177)  # 根据状态选择表情
        ])
        
        await send_message_to_event(client, event, status_msg)
    except Exception as e:
        logger.error(f"获取状态信息失败: {e}")
        await send_error_message(client, event, "获取状态信息失败")


async def send_welcome_message(client, event, message_text):
    """发送欢迎消息"""
    response = Message([
        MessageSegment.text("👋 你好！我收到了你的消息:\n"),
        MessageSegment.text(f"❝{message_text}❞\n\n"),
        MessageSegment.text("输入 /help 查看可用命令"),
        MessageSegment.face(178)
    ])
    
    await send_message_to_event(client, event, response)


async def send_error_message(client, event, error_text):
    """发送错误消息"""
    error_msg = Message([
        MessageSegment.text("❌ 错误: "),
        MessageSegment.text(error_text),
        MessageSegment.face(177)
    ])
    
    await send_message_to_event(client, event, error_msg)


async def send_message_to_event(client, event, message):
    """根据事件类型发送消息"""
    try:
        if hasattr(event, 'group_id'):
            await client.send_group_msg(event.group_id, message)
        else:
            await client.send_private_msg(event.user_id, message)
    except Exception as e:
        logger.error(f"发送消息失败: {e}")


if __name__ == "__main__":
    asyncio.run(main())