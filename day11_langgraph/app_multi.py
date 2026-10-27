import streamlit as st
import os
from typing import TypedDict
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langgraph.graph import StateGraph, END

load_dotenv()
st.set_page_config(page_title="AI 开发团队", page_icon="👨‍💻")
st.title("👨‍💻 多智能体 AI 开发团队")
st.write("输入你的开发需求，AI 主管将调度程序员和审查员为你完成任务。")

llm = ChatOpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com/v1",
    model="deepseek-chat",
    temperature=0
)

class AgentState(TypedDict):
    task: str
    code: str
    review: str
    next_agent: str

def supervisor_node(state: AgentState):
    if not state.get("code"):
        return {"next_agent": "programmer"}
    elif state.get("review") and "不通过" in state.get("review"):
        return {"next_agent": "programmer"}
    elif state.get("code") and not state.get("review"):
        return {"next_agent": "reviewer"}
    else:
        return {"next_agent": "finish"}

def programmer_node(state: AgentState):
    if state.get("review"):
        prompt_text = f"任务：{state['task']}\n上次的代码：{state['code']}\n审查意见：{state['review']}\n请根据意见修改代码。只输出 Python 代码。"
    else:
        prompt_text = f"任务：{state['task']}\n请编写 Python 代码。只输出 Python 代码，不要任何解释。"
    prompt = ChatPromptTemplate.from_messages([("user", "{text}")])
    chain = prompt | llm | StrOutputParser()
    new_code = chain.invoke({"text": prompt_text})
    return {"code": new_code, "review": ""}

def reviewer_node(state: AgentState):
    prompt = ChatPromptTemplate.from_messages([
        ("system", "你是严格的代码审查员。如果代码完美，请以'通过'开头回答；否则以'不通过'开头并指出问题。"),
        ("user", "请审查代码：\n{code}")
    ])
    chain = prompt | llm | StrOutputParser()
    return {"review": chain.invoke({"code": state["code"]})}

# 构建工作流
workflow = StateGraph(AgentState)
workflow.add_node("supervisor", supervisor_node)
workflow.add_node("programmer", programmer_node)
workflow.add_node("reviewer", reviewer_node)
workflow.set_entry_point("supervisor")
workflow.add_conditional_edges(
    "supervisor",
    lambda state: state["next_agent"],
    {"programmer": "programmer", "reviewer": "reviewer", "finish": END}
)
workflow.add_edge("programmer", "supervisor")
workflow.add_edge("reviewer", "supervisor")
app = workflow.compile()

# ==================== 网页界面 ====================
task_input = st.text_input("请输入任务：", value="写一个 Python 函数，判断一个数字是否为偶数。")

if st.button("🚀 启动 AI 开发团队"):
    if not task_input:
        st.warning("请输入任务！")
    else:
        # 创建一个空的容器，用来动态滚动显示聊天记录
        chat_container = st.container()
        
        inputs = {"task": task_input, "code": "", "review": "", "next_agent": ""}
        
        # 使用 stream 方法实时获取每个节点的输出
        for output in app.stream(inputs, {"recursion_limit": 10}):
            for node_name, state_update in output.items():
                with chat_container:
                    if node_name == "supervisor":
                        st.info("👔 **主管**：正在查看进度，分配任务...")
                    elif node_name == "programmer":
                        st.success("👨‍💻 **程序员**：代码写好了，请主管过目：")
                        st.code(state_update["code"], language="python")
                    elif node_name == "reviewer":
                        review_text = state_update["review"]
                        if "通过" in review_text and "不通过" not in review_text:
                            st.warning(f"🕵️ **审查员**：✅ {review_text}")
                        else:
                            st.error(f"🕵️ **审查员**：❌ {review_text}")
                            
        st.balloons()
        st.success("🎉 团队协作完成，代码已交付！")