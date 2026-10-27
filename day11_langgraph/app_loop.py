import streamlit as st
import os
from typing import TypedDict
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langgraph.graph import StateGraph, END

load_dotenv()
st.set_page_config(page_title="AI 智能工作流", page_icon="🤖")
st.title("🤖 AI 反思循环工作流演示")

# 初始化模型
llm = ChatOpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com/v1",
    model="deepseek-chat",
    temperature=0.7
)

# ==================== 定义状态和节点 ====================
class AgentState(TypedDict):
    task: str
    poem: str
    feedback: str
    is_pass: bool

def poet_node(state: AgentState):
    if state.get("feedback") and "不通过" in state.get("feedback", ""):
        prompt_text = f"任务：{state['task']}\n你上次写的诗被批评了：{state['feedback']}\n请务必按照要求重写一首诗。"
    else:
        prompt_text = f"任务：{state['task']}\n请写一首诗。"
    prompt = ChatPromptTemplate.from_messages([("user", "{text}")])
    chain = prompt | llm | StrOutputParser()
    return {"poem": chain.invoke({"text": prompt_text})}

def teacher_node(state: AgentState):
    prompt = ChatPromptTemplate.from_messages([
        ("system", "你是一个严格的老师。请审查诗里是否包含'月亮'二字。如果包含，回复'通过'；如果不包含，回复'不通过，必须包含月亮'。只回复这几个字。"),
        ("user", "{poem}")
    ])
    chain = prompt | llm | StrOutputParser()
    feedback = chain.invoke({"poem": state["poem"]}).strip()
    
    is_pass = ("通过" in feedback and "不通过" not in feedback)
    return {"feedback": feedback, "is_pass": is_pass}

def check_route(state: AgentState):
    return "pass" if state["is_pass"] else "retry"

# ==================== 构建工作流 ====================
workflow = StateGraph(AgentState)
workflow.add_node("poet", poet_node)
workflow.add_node("teacher", teacher_node)
workflow.set_entry_point("poet")
workflow.add_edge("poet", "teacher")
workflow.add_conditional_edges("teacher", check_route, {"pass": END, "retry": "poet"})
app = workflow.compile()

# ==================== 网页交互界面 ====================
task_input = st.text_input("请输入作诗任务：", value="写一首关于夏天的诗（必须包含特定元素）")

if st.button("🚀 启动 AI 工作流"):
    if not task_input:
        st.warning("请输入任务！")
    else:
        st.write("--- 工作流开始 ---")
        
        # 使用占位符动态更新状态
        status_placeholder = st.empty()
        result_placeholder = st.empty()
        
        # 记录循环次数
        loop_count = 0
        final_poem = ""
        
        # app.stream() 会实时吐出每个节点执行完的结果
        for output in app.stream({"task": task_input}):
            # output 是一个字典，key 是节点名，value 是节点返回的状态更新
            for node_name, state_update in output.items():
                if node_name == "poet":
                    loop_count += 1
                    status_placeholder.info(f"✍️ 第 {loop_count} 次尝试：诗人正在奋笔疾书...")
                
                elif node_name == "teacher":
                    feedback = state_update.get("feedback", "")
                    if state_update.get("is_pass"):
                        status_placeholder.success(f"🧐 老师审查：{feedback}！完美通过！")
                    else:
                        status_placeholder.warning(f"🧐 老师审查：{feedback}。打回重写！")
                
                # 如果拿到了最新的诗，就更新在页面上
                if "poem" in state_update:
                    final_poem = state_update["poem"]
                    result_placeholder.text_area("当前生成的诗：", final_poem, height=150)

        st.balloons() # 结束时放个气球特效
        st.success("🎉 最终定稿！")