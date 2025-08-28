import os
import openai
from src.config import load_config,set_env_variables
config = load_config()

from langchain_openai import ChatOpenAI
llm = ChatOpenAI(model=config["llm"]["model_name"], temperature = config["llm"]["temperature"])
llm_o3_mini = ChatOpenAI(model=config["llm"]["model_o3_mini"])
from langchain_core.messages import SystemMessage
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode
from weaviate.classes.query import Filter, GeoCoordinate, MetadataQuery, QueryReference
import re
from langgraph.graph import MessagesState, StateGraph
from langchain_core.messages import RemoveMessage
import json


def category_report_generator(state: MessagesState):
    """Generate report."""

    
    try:
        with open("src/Prompt_and_Question/prompts.json", "r", encoding="utf-8") as f:
            prompts = json.load(f)
    except Exception as e:
        print(f"Failed to read prompts.json : {str(e)}")
        return ""

    # read prompt
    if "category_report_generator" not in prompts:
        print("prompts.json can not found 'category_report_generator' ")
        return ""
    
    # append java code 
    system_message_content = prompts["category_report_generator"]


    conversation_messages = [
        message
        for message in state["messages"]
        if message.type in ("human", "system")
        or (message.type == "ai" and not message.tool_calls)
    ]
    # 生成大模型的输入
    prompt = [SystemMessage(system_message_content)] + conversation_messages

    # Run
    response = llm_o3_mini.invoke(prompt)


    return {"messages": [response]}


from langgraph.graph import MessagesState, StateGraph
from langgraph.graph import END
from langgraph.prebuilt import ToolNode, tools_condition

graph_builder4 = StateGraph(MessagesState)
graph_builder = graph_builder4

graph_builder.add_node(category_report_generator)

graph_builder.set_entry_point("category_report_generator")

graph = graph_builder.compile()

# img_data = graph.get_graph().draw_mermaid_png()

# # 确保output文件夹存在
# output_dir = "output"
# os.makedirs(output_dir, exist_ok=True)

# # 保存图像
# output_path = os.path.join(output_dir, "third_phase_graph.png")
# with open(output_path, "wb") as f:
#     f.write(img_data)

from langgraph.checkpoint.memory import MemorySaver
from datetime import datetime  # 导入 datetime 模块

# 创建 MemorySaver 实例
memory = MemorySaver()

# 编译图并设置检查点
graph = graph_builder.compile(checkpointer=memory)

# 生成当前时间的时间字符串，格式为 YYYYMMDD_HHMMSS
current_time = " Category Report Test " + datetime.now().strftime("%Y%m%d_%H%M%S")

# 配置图的执行参数，使用当前时间作为 thread_id
config = {
    "configurable": {
        "thread_id": current_time,  # 使用时间字符串作为 thread_id
    }
}

# 更新配置，添加递归限制
config.update({"recursion_limit": 25})






def category_report_generation(file_content):
    config = load_config()
    if isinstance(file_content, list):
        file_content = "\n".join(file_content)

    # 读取 APK 信息
    apk_info_path = config["directories"]["apk_info_dir"]
    with open(apk_info_path, 'r', encoding='utf-8') as file:
        apk_info_content = file.read()

    # 构建输入消息
    input_message = """
    \n
    Here is the apk info and app summaries
    \n
        """
    input_message += apk_info_content + "\n" + file_content + "\n"
    # input_message += file_content + "\n"

    # 模型推理并收集结果
    config = {
        "configurable": {
            "thread_id": current_time,  # 使用时间字符串作为 thread_id
        }
    }

    # 更新配置，添加递归限制
    config.update({"recursion_limit": 25})

    for step in graph.stream(
        {"messages": [{"role": "user", "content": input_message}]},
        stream_mode="values",
        config=config,
    ):
        step["messages"][-1].pretty_print()
        last_message = step["messages"][-1].content

    return last_message

