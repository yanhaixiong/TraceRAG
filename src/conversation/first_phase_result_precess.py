import os
from src.config import load_config
def split_and_store_java_code():
    config = load_config()
    input_file_path = config["conversation_directories"]["user_query_retrieval_filtered_path"]
    output_folder = config["conversation_directories"]["user_query_retrieval_filtered_split_path"]
    os.makedirs(output_folder, exist_ok=True)

    with open(input_file_path, "r", encoding="utf-8") as file:
        content = file.read()

    sections = content.split("===\n")
    
    for idx, section in enumerate(sections):
        if not section.strip():
            continue
        
        output_file_path = os.path.join(output_folder, f"section_{idx + 1}.txt")
        with open(output_file_path, "w", encoding="utf-8") as output_file:
            output_file.write(section.strip())
    
    print(f"已成功拆分并存储内容到 {output_folder} 文件夹下。")