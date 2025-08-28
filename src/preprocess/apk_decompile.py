from src.config import load_config,set_env_variables
config = load_config()
import os
import subprocess
import yaml

JADX_PATH = config["jadx"]["jadx_bat"]

def decompile_apk(apk_path):
    
    output_path = config["directories"]["reversed_apk_dir"]

    """调用 `jadx` 反编译 APK 文件"""
    cmd = f'"{JADX_PATH}" -d "{output_path}" "{apk_path}"'
    
    subprocess.run(cmd, shell=True, check=True)
    print(f"APK 反编译完成，Java 代码存储在 {output_path}")