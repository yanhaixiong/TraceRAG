# 运行流程
def model_conversation():

    file_path = r"E:\Android RAG\Android RAG Project Code\output\user_query_retrieve\split_filtered_result\user_query_retrieval_filtered_result\section_1.txt"
    with open(file_path, 'r', encoding='utf-8') as file:
        file_content = file.read()
    print(file_content)
    input_message ="""
    Here is the code of an Android app about the part dynamically load and execute a class or method at runtime using reflection.
    Please help me to identify the potential exist malicious behavior.

    """

    input_message += "\n" + file_content

    print(input_message)
    # """执行查询流程，并将结果保存至文件。"""
    # current_time = "package test Phase 2 " + datetime.now().strftime("%Y%m%d_%H%M%S")
    # config = {"configurable": {"thread_id": current_time}, "recursion_limit": 25}
    # final_result = ""
    
    # for step in graph1.stream(
    #     {"messages": [{"role": "user", "content": input_message}]},
    #     stream_mode="values",
    #     config=config,
    # ):
    #     step["messages"][-1].pretty_print()
    #     final_result += str(step["messages"][-1]) + "\n"
    

model_conversation()