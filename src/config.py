import os
import yaml

def load_config():
    """加载 YAML 配置，确保始终从项目根目录读取"""
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))  # 获取项目根目录
    config_path = os.path.join(base_dir, "config.yaml")

    with open(config_path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)

def set_env_variables():
    """从 config.yaml 设置环境变量"""
    config = load_config()
    env_vars = config.get("env", {})

    for key, value in env_vars.items():
        os.environ[key] = value
        print(f"✅ 设置环境变量: {key} = {value}")  # 仅用于调试，生产环境可去掉