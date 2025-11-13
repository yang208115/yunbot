"""配置文件加载测试脚本。

测试 Config.from_file() 和 Config.to_file() 方法。
"""

import sys
from pathlib import Path

# 将项目根目录添加到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from yunbot import Config
from yunbot.config import WebSocketConfig, ConnectionTypes

def test_json_loading():
    """测试从 JSON 文件加载配置。"""
    print("=== 测试 1: 从 JSON 文件加载配置 ===")
    try:
        # 使用绝对路径
        config_path = Path(__file__).parent / "config.example.json"
        config = Config.from_file(config_path)
        print(f"✓ 加载成功! 配置了 {len(config.connections)} 个连接")
        print(f"  - API 超时时间: {config.api_timeout}秒")
        print(f"  - 最大重连次数: {config.max_reconnect_attempts}")
        return True
    except FileNotFoundError as e:
        print(f"✗ 文件未找到: {e}")
        return False
    except Exception as e:
        print(f"✗ 加载失败: {e}")
        return False

def test_yaml_loading():
    """测试从 YAML 文件加载配置。"""
    print("\n=== 测试 2: 从 YAML 文件加载配置 ===")
    try:
        # 使用绝对路径
        config_path = Path(__file__).parent / "config.example.yaml"
        config = Config.from_file(config_path)
        print(f"✓ 加载成功! 配置了 {len(config.connections)} 个连接")
        
        # 获取 WebSocket 连接配置
        ws_conn = config.get_connection_by_type("websocket")
        if ws_conn and isinstance(ws_conn, WebSocketConfig):
            print(f"  - WebSocket URL: {ws_conn.url}")
            print(f"  - 心跳间隔: {ws_conn.heartbeat_interval}秒")
        return True
    except FileNotFoundError as e:
        print(f"✗ 文件未找到: {e}")
        return False
    except ImportError as e:
        print(f"⚠ 缺少依赖: {e}")
        print("  提示: 安装 PyYAML 以支持 YAML 格式: pip install pyyaml")
        return False
    except Exception as e:
        print(f"✗ 加载失败: {e}")
        return False

def test_config_saving():
    """测试保存配置到文件。"""
    print("\n=== 测试 3: 创建配置并保存到文件 ===")
    
    # 创建 WebSocket 连接配置
    ws_config = WebSocketConfig(
        url="ws://127.0.0.1:6700",
        access_token="test_token",
        self_id=None,
        secret=None,
        timeout=30.0,
        retry_times=3,
        retry_interval=1.0,
        heartbeat_interval=None
    )
    
    # 创建新配置
    new_config = Config(
        connections=[ws_config],
        api_timeout=60.0,
        max_concurrent_requests=100,
        enable_heartbeat=True,
        heartbeat_interval=30.0,
        reconnect_interval=5.0,
        max_reconnect_attempts=5
    )
    
    json_ok = False
    yaml_ok = False
    
    # 保存为 JSON
    try:
        output_path = Path(__file__).parent / "test_output.json"
        new_config.to_file(output_path)
        print("✓ 配置已保存到 test_output.json")
        json_ok = True
    except Exception as e:
        print(f"✗ 保存 JSON 失败: {e}")
    
    # 保存为 YAML
    try:
        output_path = Path(__file__).parent / "test_output.yaml"
        new_config.to_file(output_path)
        print("✓ 配置已保存到 test_output.yaml")
        yaml_ok = True
    except ImportError as e:
        print(f"⚠ 保存 YAML 跳过: 需要安装 PyYAML")
    except Exception as e:
        print(f"✗ 保存 YAML 失败: {e}")
    
    return json_ok

def test_env_override():
    """测试环境变量覆盖功能。"""
    print("\n=== 测试 4: 环境变量覆盖 ===")
    import os
    
    # 设置环境变量
    os.environ["YUNBOT_API_TIMEOUT"] = "90.0"
    os.environ["YUNBOT_MAX_RECONNECT_ATTEMPTS"] = "15"
    
    try:
        # 使用绝对路径
        config_path = Path(__file__).parent / "config.example.json"
        config = Config.from_file(config_path)
        
        if config.api_timeout == 90.0:
            print("✓ API 超时时间已被环境变量覆盖: 90.0秒")
        else:
            print(f"✗ API 超时时间覆盖失败,当前值: {config.api_timeout}")
        
        if config.max_reconnect_attempts == 15:
            print("✓ 最大重连次数已被环境变量覆盖: 15")
        else:
            print(f"✗ 最大重连次数覆盖失败,当前值: {config.max_reconnect_attempts}")
        
        # 清理环境变量
        del os.environ["YUNBOT_API_TIMEOUT"]
        del os.environ["YUNBOT_MAX_RECONNECT_ATTEMPTS"]
        
        return True
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False

if __name__ == "__main__":
    print("配置文件功能测试\n" + "=" * 50)
    
    results = []
    results.append(("JSON 加载", test_json_loading()))
    results.append(("YAML 加载", test_yaml_loading()))
    results.append(("配置保存", test_config_saving()))
    results.append(("环境变量覆盖", test_env_override()))
    
    print("\n" + "=" * 50)
    print("测试结果汇总:")
    for name, passed in results:
        status = "✓ 通过" if passed else "✗ 失败"
        print(f"  {name}: {status}")
    
    passed_count = sum(1 for _, p in results if p)
    print(f"\n总计: {passed_count}/{len(results)} 项测试通过")