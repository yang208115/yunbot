"""配置文件加载示例。

演示如何使用 Config.from_file() 和 Config.to_file() 方法。
"""

from yunbot import Config

# 示例 1: 从 JSON 文件加载配置
print("=== 从 JSON 文件加载配置 ===")
try:
    config = Config.from_file("config.example.json")
    print(f"加载成功! 配置了 {len(config.connections)} 个连接")
    print(f"API 超时时间: {config.api_timeout}秒")
    print(f"最大重连次数: {config.max_reconnect_attempts}")
except FileNotFoundError as e:
    print(f"文件未找到: {e}")
except Exception as e:
    print(f"加载失败: {e}")

print()

# 示例 2: 从 YAML 文件加载配置
print("=== 从 YAML 文件加载配置 ===")
try:
    config = Config.from_file("config.example.yaml")
    print(f"加载成功! 配置了 {len(config.connections)} 个连接")
    
    # 获取 WebSocket 连接配置
    ws_conn = config.get_connection_by_type("websocket")
    if ws_conn:
        print(f"WebSocket URL: {ws_conn.url}")
        print(f"心跳间隔: {ws_conn.heartbeat_interval}秒")
except FileNotFoundError as e:
    print(f"文件未找到: {e}")
except ImportError as e:
    print(f"缺少依赖: {e}")
    print("提示: 安装 PyYAML 以支持 YAML 格式: pip install pyyaml")
except Exception as e:
    print(f"加载失败: {e}")

print()

# 示例 3: 创建配置并保存到文件
print("=== 创建配置并保存到文件 ===")
from yunbot.config import WebSocketConfig

# 创建新配置
new_config = Config(
    connections=[
        WebSocketConfig(
            url="ws://127.0.0.1:6700",
            access_token="test_token",
            heartbeat_interval=30.0
        )
    ],
    api_timeout=60.0,
    max_reconnect_attempts=5
)

# 保存为 JSON
try:
    new_config.to_file("output_config.json")
    print("✓ 配置已保存到 output_config.json")
except Exception as e:
    print(f"保存 JSON 失败: {e}")

# 保存为 YAML
try:
    new_config.to_file("output_config.yaml")
    print("✓ 配置已保存到 output_config.yaml")
except ImportError as e:
    print(f"保存 YAML 失败: {e}")
    print("提示: 安装 PyYAML 以支持 YAML 格式: pip install pyyaml")
except Exception as e:
    print(f"保存 YAML 失败: {e}")

print()

# 示例 4: 环境变量覆盖
print("=== 环境变量覆盖示例 ===")
print("支持的环境变量:")
print("  YUNBOT_API_TIMEOUT - 覆盖 API 超时时间")
print("  YUNBOT_MAX_CONCURRENT_REQUESTS - 覆盖最大并发请求数")
print("  YUNBOT_ENABLE_HEARTBEAT - 覆盖心跳开关 (true/false)")
print("  YUNBOT_HEARTBEAT_INTERVAL - 覆盖心跳间隔")
print("  YUNBOT_RECONNECT_INTERVAL - 覆盖重连间隔")
print("  YUNBOT_MAX_RECONNECT_ATTEMPTS - 覆盖最大重连次数")
print()
print("使用方法:")
print("  Windows PowerShell:")
print('    $env:YUNBOT_API_TIMEOUT="60.0"')
print("    python config_file_demo.py")
print()
print("  Linux/Mac:")
print("    export YUNBOT_API_TIMEOUT=60.0")
print("    python config_file_demo.py")
