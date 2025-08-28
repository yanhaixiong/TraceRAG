import xml.etree.ElementTree as ET
import hashlib
import os
from src.config import load_config,set_env_variables
config = load_config()


# 解析 AndroidManifest.xml 以提取包名、版本号等信息
def parse_manifest(manifest_path):
    tree = ET.parse(manifest_path)
    root = tree.getroot()

    package_name = root.attrib.get('package', 'Unknown')
    version_code = root.attrib.get('{http://schemas.android.com/apk/res/android}versionCode', 'Unknown')
    version_name = root.attrib.get('{http://schemas.android.com/apk/res/android}versionName', 'Unknown')

    return package_name, version_code, version_name

# 计算文件哈希值
def calculate_hash(file_path, hash_type="sha256"):
    hash_func = getattr(hashlib, hash_type)()
    with open(file_path, "rb") as f:
        while chunk := f.read(4096):
            hash_func.update(chunk)
    return hash_func.hexdigest()



# def apk_info_extract(apk_path):
#     # 解析 AndroidManifest.xml
#     manifest_path = os.path.join(config["directories"]["reversed_apk_dir"], "resources", "AndroidManifest.xml")

#     output_path = config["directories"]["apk_info_dir"]
#     package_name, version_code, version_name = parse_manifest(manifest_path)

#     # 计算 APK 文件哈希值
#     hash_algorithms = ["md5", "sha1", "sha256"]
#     hash_results = {algo.upper(): calculate_hash(apk_path, algo) for algo in hash_algorithms}

#     # 组织输出内容
#     output_content = [
#         f"Package Name: {package_name}",
#         f"Version Code: {version_code}",
#         f"Version Name: {version_name}",
#         "",
#     ]
#     output_content.extend([f"{algo}: {hash_results[algo]}" for algo in hash_results])

#     # 将结果写入文件
#     with open(output_path, "w", encoding="utf-8") as f:
#         f.write("\n".join(output_content))

#     print(f"结果已保存到 {output_path}")

def apk_info_extract(apk_path):
    # 解析 AndroidManifest.xml
    manifest_path = os.path.join(config["directories"]["reversed_apk_dir"], "resources", "AndroidManifest.xml")
    output_path = config["directories"]["apk_info_dir"]

    package_name, version_code, version_name = parse_manifest(manifest_path)

    # 只计算 SHA256 哈希值
    sha256_hash = calculate_hash(apk_path, "sha256")

    # 组织输出内容
    output_content = [
        f"Package Name: {package_name}",
        f"Version Code: {version_code}",
        f"Version Name: {version_name}",
        "",
        f"SHA256: {sha256_hash}"
    ]

    # 写入结果文件
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(output_content))

    print(f"结果已保存到 {output_path}")





# if __name__ == "__main__":
#     # 文件路径
#     manifest_path = r"E:\Android RAG\Dataset\AndroZoo\random_test_reversed\00B00978560173C270F0698260B5A9CED246C4115E9263B464DE5375D2966CF5\resources\AndroidManifest.xml"
#     apk_path = r"E:\Android RAG\Dataset\AndroZoo\random_test\00B00978560173C270F0698260B5A9CED246C4115E9263B464DE5375D2966CF5.apk"
#     output_path = r"E:\Android RAG\Dataset\AndroZoo\random_test_reversed\00B009_result\apk_info.txt"

#     # 解析 AndroidManifest.xml
#     package_name, version_code, version_name = parse_manifest(manifest_path)

#     # 计算 APK 文件哈希值
#     hash_algorithms = ["md5", "sha1", "sha256"]
#     hash_results = {algo.upper(): calculate_hash(apk_path, algo) for algo in hash_algorithms}

#     # 组织输出内容
#     output_content = [
#         f"Package Name: {package_name}",
#         f"Version Code: {version_code}",
#         f"Version Name: {version_name}",
#         "",
#     ]
#     output_content.extend([f"{algo}: {hash_results[algo]}" for algo in hash_results])

#     # 将结果写入文件
#     with open(output_path, "w", encoding="utf-8") as f:
#         f.write("\n".join(output_content))

#     print(f"结果已保存到 {output_path}")

