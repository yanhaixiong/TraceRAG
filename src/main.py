import sys
import os
import shutil
import json
import argparse
import yaml
from src.config import load_config,set_env_variables

from src.preprocess.pipeline import preprocess_pipeline

from src.conversation.first_phase import execute_query
from src.conversation.first_phase_result_precess import split_and_store_java_code
from src.conversation.second_phase import model_conversation

from src.postprocess.combine_single_question_report import quesiton_report_generation
from src.postprocess.txt2markwon_and_html import convert_txt_to_md_and_html
from src.postprocess.Final_report_Generation import apk_report_generation



CONFIG_PATH = r"config.yaml"

def update_config_index_name(new_index_name, config_path=CONFIG_PATH):
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    # 更新 index_name
    config['weaviate']['index_name'] = new_index_name

    with open(config_path, 'w', encoding='utf-8') as f:
        yaml.safe_dump(config, f, allow_unicode=True)



if __name__ == "__main__":

    set_env_variables()

    # 读取 YAML 配置
    config = load_config()



    parser = argparse.ArgumentParser(description="Run APK analysis pipeline.")
    parser.add_argument("apk_directory", type=str, help="Path to the APK file or directory containing APKs.")
    parser.add_argument("index_name", type=str, help="Index name for the vector database.")

    args = parser.parse_args()
    apk_directory = args.apk_directory
    index_name = args.index_name

    # 更新 YAML 文件中的 index_name
    update_config_index_name(index_name)

    # 读取更新后的配置
    config = load_config()

    
    # # accept a apk file as input
    # # 1.decompile it to extract java files ### also extract all the apk info like sha256,package name, version from manifest and other
    # # 2.spilt these extracted java file into methods
    # # 3.clean the code to remove obfuscation
    # # 4.generated code description for split and cleaned code snippets/.
    # # 5.store these java code and txt description into vector database to construct RAG
    preprocess_pipeline(apk_directory, index_name)




    #read json to retrieve prompt 
    try:
        with open("src/Prompt_and_Question/questions_3_category.json", "r", encoding="utf-8") as f:
            questions = json.load(f)
    except Exception as e:
        print(f"Failed to read questions.json : {str(e)}")

    # 遍历每个问题并依次执行查询与代码处理
    for question_name, retrieve_question in questions.items():
        print(f"Processing: {question_name}")
        try:

            ###### First stage, retrieve the code using pre designed question#########
            ########################################################################
            execute_query(retrieve_question)  # execute query
            split_and_store_java_code()     # process the retrieve result, seperatedly save retrieved code snippets
            ########################################################################
            

            output_dir = config["conversation_directories"]["user_query_analyze_path"]
            os.makedirs(output_dir, exist_ok=True)

            code_snippet_path = config["conversation_directories"]["user_query_retrieval_filtered_split_path"]
            # Check if the path exists
            if not os.path.exists(code_snippet_path):
                print(f"[Error] The directory '{code_snippet_path}' does not exist.")
            else:
                print(f"[Info] Starting to process .txt files in: {code_snippet_path}")

                file_contents = []  # append every code snippet's result together to generate question report 用于收集合并内容

                # Loop through all .txt files in the directory
                for idx, filename in enumerate(sorted(os.listdir(code_snippet_path)), start=1):
                    if filename.endswith(".txt"):
                        file_path = os.path.join(code_snippet_path, filename)
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                code_snippet = f.read()
                            analyze_question = (
                                "Here is an Android app's java code about " +
                                question_name +
                                ". Please help me to identify the potential exist malicious behavior."
                            )
                            print(f"[Processing] Running model on: {filename}")

                            ###############################################################
                            #########Second stage, using LLM to analyze retrieved code####
                            ###############################################################
                            result = model_conversation(analyze_question, code_snippet)
                            ###############################################################
                            
                            # Save result to output file (same name as input, different folder)
                            output_file = os.path.join(output_dir, filename)  # same name as .txt
                            with open(output_file, 'w', encoding='utf-8') as out_f:
                                out_f.write(str(result))  # Ensure it's string or serialize properly

                            # append the code report together, and pass it to LLM to generate quesiton report.
                            file_contents.append(f"conversation history {idx}\n{str(result)}")


                        except Exception as e:
                            print(f"[Warning] Failed to process file: {filename}. Error: {e}")

                
                combined_file_path = os.path.join(output_dir, 'code_report_combined.txt')
                with open(combined_file_path, 'w', encoding='utf-8') as combined_f:
                    combined_f.write("\n\n".join(file_contents))

                print("\n\n[Done] All files have been processed and combined report saved.")

                
                try:
                    final_result = quesiton_report_generation(file_contents)

                    # save result as  question_report.txt
                    final_report_path = os.path.join(output_dir, 'question_report.txt')
                    with open(final_report_path, 'w', encoding='utf-8') as f:
                        f.write(final_result)

                    print(f"[Final Report Saved] {final_report_path}")


                    convert_txt_to_md_and_html(final_report_path)

                except Exception as e:
                    print(f"[Error] Failed to run quesiton_report_generation. Error: {e}")









                ##########################################
                ##### organise the analyze result ########
                ##########################################
                try:
                    llm_output_base = config["conversation_directories"]["LLM_output"]
                    question_output_dir = os.path.join(llm_output_base, question_name)
                    os.makedirs(question_output_dir, exist_ok=True)

                    # 要转移的文件夹
                    folders_to_move = ['analyze', 'retrieve']

                    for folder_name in folders_to_move:
                        src_folder = os.path.join(llm_output_base, folder_name)
                        dst_folder = os.path.join(question_output_dir, folder_name)

                        if os.path.exists(src_folder):
                            # 如果目标已存在，则先删除再复制（避免文件冲突）
                            if os.path.exists(dst_folder):
                                shutil.rmtree(dst_folder)
                            shutil.move(src_folder, dst_folder)
                            print(f"[Moved] {folder_name} → {question_output_dir}")
                        else:
                            print(f"[Skipped] {folder_name} not found in {llm_output_base}")

                except Exception as e:
                    print(f"[Error] Failed to move folders for {question_name}: {e}")


        except Exception as e:
            print(f"Error processing {question_name}: {str(e)}")



    ####################################################################################
    ######## Combine all question reports to generate final app report #################
    ####################################################################################
    import os
    from src.config import load_config,set_env_variables
    config = load_config()
    def collect_question_reports(base_dir):
        final_report = ""
        for category in os.listdir(base_dir):
            category_path = os.path.join(base_dir, category)
            question_path = os.path.join(category_path, "analyze", "question_report.txt")
            if os.path.isfile(question_path):
                with open(question_path, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                    final_report += f"{category} Report:\n{content}\n\n"
        return final_report.strip()

    # 你配置中的路径
    llm_output_base = config["conversation_directories"]["LLM_output"]

    # 生成合并报告
    merged_question_reports = collect_question_reports(llm_output_base)

    apk_analyze_result = apk_report_generation(merged_question_reports)
    output_path = os.path.join(llm_output_base, "APK_Report.txt")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(apk_analyze_result)
    convert_txt_to_md_and_html(output_path)






    




















