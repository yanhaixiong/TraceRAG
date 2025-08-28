from langgraph.graph import MessagesState, StateGraph
from langgraph.graph import END
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.messages import SystemMessage
import json
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_core.tools import tool
import weaviate
from weaviate.classes.query import Filter
from llama_index.vector_stores.weaviate import WeaviateVectorStore
from weaviate.exceptions import WeaviateBaseError
import os
import time
import tenacity
from tenacity import retry, stop_after_attempt, wait_fixed

from src.config import load_config,set_env_variables
config = load_config()

from langchain_openai import ChatOpenAI


llm = ChatOpenAI(model=config["llm"]["model_name"], temperature = config["llm"]["temperature"])
llm_o3_mini = ChatOpenAI(model=config["llm"]["model_o3_mini"])

max_retries = 5
retry_count = 0

while retry_count < max_retries:
    try:
        client = weaviate.connect_to_wcs(
            cluster_url=config["weaviate"]["url"],
            auth_credentials=weaviate.auth.AuthApiKey(config["weaviate"]["api_key"]),
        )
        vector_store = WeaviateVectorStore(
            weaviate_client=client,
            index_name=config["weaviate"]["index_name"]
        )
        break  # Success
    except Exception as e:
        retry_count += 1
        print(f"[Retry {retry_count}/{max_retries}] Connection to Weaviate failed: {e}. Retrying in 3 seconds...")
        time.sleep(3)
else:
    raise RuntimeError(f"Failed to connect to Weaviate after {max_retries} attempts. Please check your configuration.")

        
# Tool. Retrieve using query from Weaviate Vector DataBase
@tool(response_format="content_and_artifact")
@retry(stop=stop_after_attempt(10), wait=wait_fixed(5), retry=tenacity.retry_if_exception_type(weaviate.exceptions.WeaviateQueryError))
def retrieve(query: str, method_name: str, class_name: str):
    """Retrieve information related to a query.
    The query will be a question about an Android app's Java code.
    `method_metadata` refers to the name of a Java method explicitly present in the seen code and related to the query.
    `class_name` refers to the name of the Java class that may also be relevant for filtering results.
    If either `method_metadata` or `class_name` is not provided, those filters will not be used.
    """
    try:
        # 生成嵌入
        embeddings_query = OpenAIEmbeddings(model="text-embedding-ada-002")
        embedding_vector = embeddings_query.embed_query(query)
        Java_Vec_DB = client.collections.get(config["weaviate"]["index_name"])

        if method_name and class_name:
            filter_condition= Filter.by_property("methods").equal(f"{method_name}*")  &  Filter.by_property("class").equal(f"{class_name}*")
            
        else:
            filter_condition = None  # 不使用过滤条件

        # 查询向量数据库
        retrieved_docs = Java_Vec_DB.query.near_vector(
            near_vector=embedding_vector,
            filters= filter_condition,
            limit=5,
            # distance=0.25
        )

        # 格式化结果
        serialized = "\n\n".join(
            f"File Path:{obj.properties['file_path']}\nClass Name:{obj.properties['class']}\nContent: {obj.properties['original_code']}"
            for obj in retrieved_docs.objects
            if 'original_code' in obj.properties
        )

        return serialized, retrieved_docs
    except weaviate.exceptions.WeaviateQueryError as e:
        raise RuntimeError(f"Query failed after multiple retries: {str(e)}")


# Step 2: Execute the retrieval.
tools = ToolNode([retrieve])

# Step 3: Generate a response using the retrieved content.
def reorder_for_graph_2(state: MessagesState):
    """Generate answer."""
    
    # 提取查询内容
    query = ""
    for message in state["messages"]:
        if hasattr(message, 'additional_kwargs') and 'tool_calls' in message.additional_kwargs:
            for tool_call in message.additional_kwargs['tool_calls']:
                arguments = json.loads(tool_call['function']['arguments'])
                query = arguments.get('query', None)


    recent_tool_messages = []
    for message in reversed(state["messages"]):
        if message.type == "tool":
            recent_tool_messages.append(message)
        else:
            break
    tool_messages = recent_tool_messages[::-1]

    # Format into prompt
    docs_content_re = "\n\n".join(doc.content for doc in tool_messages)

    # # # # # # return all the related result,  returned code num <= total retrieved code num # # # # # # # 

    try:
        with open("src/Prompt_and_Question/prompts.json", "r", encoding="utf-8") as f:
            prompts = json.load(f)
    except Exception as e:
        print(f"Failed to read prompts.json : {str(e)}")
        return ""

    # read prompt
    if "reorder_for_graph_2" not in prompts:
        print("prompts.json can not found 'reorder_for_graph_2' ")
        return ""
    
    # append java code 
    system_message_content = prompts["reorder_for_graph_2"] + "Here's the query: \n" + query + "\nHere's the code with path\n" + docs_content_re


    # prompt = [SystemMessage(system_message_content)] + conversation_messages
    prompt = [SystemMessage(system_message_content)]
    docs_content_re = "\n\n".join(doc.content for doc in tool_messages)

    # Run
    response = llm.invoke(prompt)

    return {"messages": [response]}


# Step 3: Generate a response using the retrieved content.

def generate(state: MessagesState):
    """Generate answer."""
    # Get generated ToolMessages
    recent_tool_messages = []
    for message in reversed(state["messages"]):
        if message.type == "tool":
            recent_tool_messages.append(message)
        else:
            break
    tool_messages = recent_tool_messages[::-1]

    # Format into prompt
    docs_content = "\n\n".join(doc.content for doc in tool_messages)

    try:
        with open("src/Prompt_and_Question/prompts.json", "r", encoding="utf-8") as f:
            prompts = json.load(f)
    except Exception as e:
        print(f"Failed to read prompts.json : {str(e)}")
        return ""

    # read prompt
    if "generate" not in prompts:
        print("prompts.json can not found 'generate' ")
        return ""
    
    # append java code 
    system_message_content = prompts["generate"] + "Here's the code: \n" + docs_content


    conversation_messages = [
        message
        for message in state["messages"]
        if message.type in ("human", "system")
        or (message.type == "ai" and not message.tool_calls)
    ]
    prompt = [SystemMessage(system_message_content)] + conversation_messages

    # Run
    # response = llm.invoke(prompt)
    response = llm_o3_mini.invoke(prompt)
    return {"messages": [response]}

# Step 4: Go back to RAG or output the response
def back_or_output(state: MessagesState):
    """
    Call the tool when a question was generated by your upstream.
    """

    try:
        with open("src/Prompt_and_Question/prompts.json", "r", encoding="utf-8") as f:
            prompts = json.load(f)
    except Exception as e:
        print(f"Failed to read prompts.json : {str(e)}")
        return ""

    # read prompt
    if "back_or_output" not in prompts:
        print("prompts.json can not found 'back_or_output' ")
        return ""
    
    # append java code 
    system_message_content = prompts["back_or_output"]

    
    conversation_messages = [
        message
        for message in reversed(state["messages"])
        if message.type == "ai"
    ][0:1]

    prompt = [SystemMessage(system_message_content)] + conversation_messages

    # Run
    llm_with_tools = llm.bind_tools([retrieve])
    response = llm_with_tools.invoke(prompt)
    return {"messages": [response]}




def report_generator(state: MessagesState):
    """
    Generate report base on the whole process.
    """

    try:
        with open("src/Prompt_and_Question/prompts.json", "r", encoding="utf-8") as f:
            prompts = json.load(f)
    except Exception as e:
        print(f"Failed to read prompts.json : {str(e)}")
        return ""

    # read prompt
    if "report_generator" not in prompts:
        print("prompts.json can not found 'report_generator' ")
        return ""
    
    # append java code 
    system_message_content = prompts["report_generator"]




    conversation_messages = [
        message
        for message in state["messages"]
        if message.type in ("human", "system")
        or (message.type == "ai" and not message.tool_calls)
    ]

    prompt = [SystemMessage(system_message_content)] + conversation_messages

    #
    # # output_dir = "output/LLM_answer"
    # output/LLM_output/analyze
    output_dir = config["conversation_directories"]["user_query_analyze_path"]

    os.makedirs(output_dir, exist_ok=True)  # 只创建目录

    # 保存 LLM 分析细节
    output_file_1 = os.path.join(output_dir, "Detail.txt")
    with open(output_file_1, "w", encoding="utf-8") as file:
        for msg in conversation_messages:
            file.write(msg.content + "\n\n")

    # 运行 LLM
    response = llm.invoke(prompt)

    # # 保存分析结论
    # output_file_2 = os.path.join(output_dir, "conclusion.txt")
    # with open(output_file_2, "w", encoding="utf-8") as file: 
    #     file.write(str(response.content))

    # MessagesState appends messages to state instead of overwriting
    return {"messages": [response]}


graph_builder2 = StateGraph(MessagesState)
graph_builder1 = graph_builder2

# graph_builder1.add_node(query_or_respond)
graph_builder1.add_node(tools)
# graph_builder.add_node(retrieve_re)
graph_builder1.add_node(generate)
#graph_builder.add_node(reorder_for_graph_2)
graph_builder1.add_node(back_or_output)
graph_builder1.add_node(reorder_for_graph_2)######add a new reorder here to prevent same name!!!!!!!!!!!!!!!!!!!!!!!!!
graph_builder1.add_node(report_generator)



graph_builder1.set_entry_point("generate")
graph_builder1.add_edge("tools", "reorder_for_graph_2")
graph_builder1.add_edge("reorder_for_graph_2", "generate")
graph_builder1.add_edge("generate", "back_or_output")
# graph_builder.add_edge("back_or_output", "report_generator")


def back_or_output_condition(state: MessagesState):
    """
    Decide whether to return to tools or generate the report.
    If there is sufficient data to generate the report (i.e., identified malicious behavior),
    proceed to the report generation. Otherwise, return to the tools for further analysis.
    """

    # 获取最新的 AI 消息
    conversation_messages = [
        message
        for message in reversed(state["messages"])
        if message.type == "ai"
    ][0:1]
    
    # 如果没有函数调用，则返回“generate_report”
    if not conversation_messages:  # 确保列表不为空
        return "generate_report"
    
    message = conversation_messages[0]  # 获取最新的消息


    # 检查该消息是否包含 "tool_call"
    if "tool_calls" not in message.additional_kwargs:
        return "generate_report"
    else:
        return "back_to_retrieve"

graph_builder1.add_conditional_edges(
    "back_or_output",  # 起始节点
    back_or_output_condition,  # 条件函数
    { "back_to_retrieve": "tools", "generate_report": "report_generator"}  # 目标节点字典
)



from langgraph.checkpoint.memory import MemorySaver
from datetime import datetime  # 导入 datetime 模块

# 创建 MemorySaver 实例
memory1 = MemorySaver()

# 编译图并设置检查点
graph1 = graph_builder1.compile(checkpointer=memory1)

img_data = graph1.get_graph().draw_mermaid_png()

# 确保output文件夹存在
output_dir = "output"
os.makedirs(output_dir, exist_ok=True)

# 保存图像
output_path = os.path.join(output_dir, "second_phase_graph.png")
with open(output_path, "wb") as f:
    f.write(img_data)





# 运行流程
def model_conversation(input_message,code_snippet):


    input_message += "\n" + code_snippet

    """执行查询流程，并将结果保存至文件。"""
    current_time = "Conversation " + datetime.now().strftime("%Y%m%d_%H%M%S")
    config = {"configurable": {"thread_id": current_time}, "recursion_limit": 25}
    
    for step in graph1.stream(
        {"messages": [{"role": "user", "content": input_message}]},
        stream_mode="values",
        config=config,
    ):
        step["messages"][-1].pretty_print()
        last_message = step["messages"][-1].content

    return last_message