# src/preprocess/pipeline.py

# 导入预处理模块
# from src.preprocess import java_code_split, code_cleaning_summarization, store_vector_database
from src.preprocess import java_code_split, code_cleaning_summarization, store_vector_database,apk_decompile, apk_info_extract
from src.config import load_config,set_env_variables


# def preprocess_pipeline(java_directory):
def preprocess_pipeline(apk_path,index_name):
    """
    Preprocess Java Code: Code Split -> Code Cleaning and summarize -> store to vector database
    
    """
    # set_env_variables()
    config = load_config()
    
    openai_api_key = config["openai"]["api_key"]

    weaviate_url = config["weaviate"]["url"]
    weaviate_api_key = config["weaviate"]["api_key"]
    # weaviate_index_name = config["weaviate"]["index_name"]
    

    java_directory = config["directories"]["java_dir"]
    
    input_file_split = f"{java_directory}_Split"
    input_file_split_cleaned = f"{java_directory}_Split_Cleaned"
    input_file_split_cleaned_summarized = f"{java_directory}_Split_Cleaned_Summarized"

    # Decompile apk to Java
    apk_decompile.decompile_apk(apk_path)
    print(f"Decomplie Success !!")
    apk_info_extract.apk_info_extract(apk_path)

    # Split Java codes
    java_code_split.split_java_files(java_directory)

    #Code cleaning 
    code_cleaning_summarization.clean_java_files(input_file_split,input_file_split_cleaned)
    #Code Summarization
    code_cleaning_summarization.summarize_java_files(input_file_split_cleaned,input_file_split_cleaned_summarized)

    print(f"Code summaries have been saved to: {input_file_split_cleaned_summarized}")

    # 3️⃣ 存入向量数据库
    # store_vector_database.process_java_summaries(input_file_split_cleaned,input_file_split_cleaned_summarized,weaviate_url,weaviate_api_key,weaviate_index_name,openai_api_key)
    store_vector_database.process_java_summaries(input_file_split_cleaned,input_file_split_cleaned_summarized,weaviate_url,weaviate_api_key,index_name,openai_api_key)
    print(f"代码存入向量数据库完成")
