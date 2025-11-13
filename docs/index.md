# YunBot 使用文档

欢迎使用 YunBot - OneBot v11 客户端适配器！

## 项目简介

YunBot 是一个功能完整、易于使用的 OneBot v11 协议 Python 客户端库。它为开发者提供了构建聊天机器人应用的完整解决方案，支持多种连接方式和丰富的事件处理机制。

### 核心特性

- ✨ **完整的 OneBot v11 API 支持** - 实现所有标准 API 接口
- 🔌 **多种连接方式** - 支持 WebSocket、HTTP 等多种连接类型
- 📨 **强大的事件处理系统** - 支持消息、通知、请求、元事件
- 🎨 **丰富的消息构建** - 支持文本、图片、表情、@等多种消息段
- 🔄 **自动重连** - 智能重连机制保证连接稳定性
- ⚙️ **配置验证** - 基于 Pydantic 的强类型配置验证
- 📝 **详细日志** - 彩色日志输出,便于调试和问题排查

### 解决的问题

- 简化 OneBot v11 协议的复杂性
- 提供统一的 API 调用接口
- 实现自动重连和错误处理机制
- 支持多种消息类型和事件处理
- 提供完善的配置管理和日志记录

## 快速导航

### 入门指南

- 📦 [安装指南](installation.md) - 环境准备和安装步骤
- 🚀 [快速开始](quickstart.md) - 5分钟创建第一个机器人

### 使用指南

- 👤 [客户端使用](guide/client.md) - 客户端创建和生命周期管理
- 📬 [事件处理](guide/events.md) - 处理各类事件
- 💬 [消息构建](guide/messages.md) - 构建和发送各类消息
- ⚙️ [配置管理](guide/configuration.md) - 配置参数和最佳实践

### API 参考

- 📖 [API 概览](api/overview.md) - API 分类和调用约定
- 🔧 [客户端 API](api/client.md) - OneBotClient 类方法
- 📤 [消息 API](api/message.md) - 消息发送和操作
- 👥 [群组管理 API](api/group.md) - 群组管理功能
- ℹ️ [信息获取 API](api/info.md) - 信息查询接口

### 高级功能

- 🎯 [事件匹配器](advanced/event-matcher.md) - 高级事件匹配功能
- 📊 [日志系统](advanced/logging.md) - 日志配置和使用
- ⚠️ [错误处理](advanced/error-handling.md) - 异常处理和错误恢复

### 示例与教程

- 🤖 [基础机器人](examples/basic-bot.md) - 最简单的完整示例
- ⌨️ [命令处理机器人](examples/command-bot.md) - 命令式机器人开发
- 👮 [群管理机器人](examples/group-manager.md) - 群管理功能实现

### 其他资源

- ❓ [常见问题](faq.md) - 常见问题解答
- 📮 [GitHub](https://github.com/yang208115/YunBot) - 项目主页
- 📄 [许可证](https://github.com/yang208115/YunBot/blob/main/LICENSE) - MIT License

## 版本信息

当前文档版本: v0.0.1

## 社区支持

如有问题或建议,请通过以下方式联系我们:

- 📝 提交 [GitHub Issues](https://github.com/yang208115/YunBot/issues)
- 💬 加入 QQ 群交流 (群号: 123456789)
- 📧 发送邮件至项目维护者

我们欢迎所有形式的反馈和贡献!

## 开始使用

如果您是第一次使用 YunBot,建议按照以下顺序阅读文档:

1. [安装指南](installation.md) - 完成环境准备
2. [快速开始](quickstart.md) - 创建第一个机器人
3. [客户端使用](guide/client.md) - 深入了解客户端
4. [API 参考](api/overview.md) - 查阅 API 文档

祝您使用愉快! 🎉
