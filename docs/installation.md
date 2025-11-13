# 安装指南

本文档将引导您完成 YunBot 的环境准备和安装步骤。

## 环境要求

在开始安装之前,请确保您的系统满足以下要求:

### Python 版本

- **Python 3.7 或更高版本**

检查 Python 版本:

```bash
python --version
# 或
python3 --version
```

### 操作系统

YunBot 支持以下操作系统:

- Windows 10/11
- macOS 10.14+
- Linux (Ubuntu 18.04+, Debian 10+, CentOS 7+等)

### 依赖库

YunBot 依赖以下 Python 库 (安装时会自动安装):

- **aiohttp** >= 3.7.0 - 异步 HTTP 客户端/服务器框架
- **pydantic** >= 2.0.0 - 数据验证和设置管理
- **websockets** - WebSocket 客户端和服务器实现

## 安装方式

如果您需要使用最新的开发版本或想要参与开发,可以从源码安装:

1. **克隆项目仓库**

```bash
git clone https://github.com/yang208115/YunBot.git
cd yunbot
```

2. **安装依赖**

```bash
pip install -r requirements.txt
```

3. **安装到本地** (可选)

```bash
pip install -e .
```

使用 `-e` 参数可以让您在修改代码后无需重新安装即可生效。

## 验证安装

安装完成后,您可以通过以下方式验证安装是否成功:

### 方法一: 检查包版本

```bash
pip show yunbot
```

您应该看到类似以下输出:

```
Name: yunbot
Version: 0.0.1
Summary: OneBot v11 客户端适配器
...
```

### 方法二: 导入测试

在 Python 交互环境中测试导入:

```python
import yunbot
print(yunbot.__version__)
```

如果能够成功导入并打印版本号,说明安装成功。

### 方法三: 运行简单示例

创建一个测试文件 `test_install.py`:

```python
from yunbot import OneBotClient, MessageSegment

# 如果没有报错,说明安装成功
print("✓ YunBot 安装成功!")
print(f"✓ 版本: {yunbot.__version__}")
```

运行:

```bash
python test_install.py
```

## 常见安装问题

### 问题 1: pip 版本过低

**错误信息**:
```
ERROR: Could not find a version that satisfies the requirement pydantic>=2.0.0
```

**解决方案**:
升级 pip 到最新版本:

```bash
pip install --upgrade pip
```

### 问题 2: 权限不足

**错误信息**:
```
ERROR: Could not install packages due to an EnvironmentError: [Errno 13] Permission denied
```

**解决方案**:
使用 `--user` 参数安装到用户目录:

```bash
pip install --user yunbot
```

或者在 Linux/macOS 上使用 sudo (不推荐):

```bash
sudo pip install yunbot
```

### 问题 3: Python 版本不兼容

**错误信息**:
```
ERROR: Package 'onebot-adapter-client' requires a different Python: 3.6.0 not in '>=3.7'
```

**解决方案**:
升级 Python 到 3.7 或更高版本,或使用虚拟环境:

```bash
# 创建 Python 3.7+ 虚拟环境
python3.7 -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# 在虚拟环境中安装
pip install onebot-adapter-client
```

### 问题 5: 依赖冲突

**错误信息**:
```
ERROR: pip's dependency resolver does not currently take into account all the packages that are installed
```

**解决方案**:
使用虚拟环境隔离项目依赖:

```bash
# 创建虚拟环境
python -m venv yunbot_env

# 激活虚拟环境
# Windows:
yunbot_env\Scripts\activate
# Linux/macOS:
source yunbot_env/bin/activate

# 在虚拟环境中安装
pip install onebot-adapter-client
```

## 开发环境设置

如果您计划参与 YunBot 的开发,建议进行以下额外设置:

### 安装开发依赖

```bash
cd yunbot
pip install -r requirements.txt
```

### 安装代码格式化工具

```bash
pip install black isort flake8
```

### 安装测试工具

```bash
pip install pytest pytest-asyncio pytest-cov
```

## 下一步

安装完成后,您可以:

- 阅读 [快速开始](quickstart.md) 创建第一个机器人
- 查看 [客户端使用](guide/client.md) 了解详细用法
- 浏览 [示例代码](examples/basic-bot.md) 学习实际应用

## 相关文档

- [快速开始](quickstart.md)
- [配置管理](guide/configuration.md)
- [常见问题](faq.md)
