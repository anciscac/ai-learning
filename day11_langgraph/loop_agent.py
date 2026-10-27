import os
from typing import TypedDict
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langgraph.graph import StateGraph, END

load_dotenv()
llm = ChatOpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com/v1",
    model="deepseek-chat",
    temperature=0.7
)

# 1. 定义 State（记录本）
class AgentState(TypedDict):
    task: str          # 任务要求
    poem: str          # AI 写的诗
    feedback: str      # 老师的反馈
    is_pass: bool      # 是否通过

# 2. 节点 A：写诗的诗人
def poet_node(state: AgentState):
    print("--- ✍️ 诗人正在写诗... ---")
    # 如果老师给了反馈，就把反馈加进去；如果是第一次写，反馈是空的
    if state.get("feedback"):
        prompt_text = f"任务：{state['task']}\n你上次写的诗被老师批评了，老师的反馈是：{state['feedback']}\n请根据反馈重写一首诗。"
    else:
        prompt_text = f"任务：{state['task']}\n请写一首诗。"
        
    prompt = ChatPromptTemplate.from_messages([("user", "{text}")])
    chain = prompt | llm | StrOutputParser()
    poem = chain.invoke({"text": prompt_text})
    print(f"📝 诗人写出了：\n{poem}\n")
    return {"poem": poem}

# 3. 节点 B：严格的语文老师
def teacher_node(state: AgentState):
    print("--- 🧐 老师正在审查... ---")
    prompt = ChatPromptTemplate.from_messages([
        ("system", "你是一个严格的语文老师。请审查学生的诗是否包含了'月亮'这个词。如果包含，回复'通过'；如果不包含，回复'不通过，必须包含月亮'。只回复这几个字。"),
        ("user", "{poem}")
    ])
    chain = prompt | llm | StrOutputParser()
    feedback = chain.invoke({"poem": state["poem"]}).strip()
    
    print(f"🧑‍🏫 老师的评价：{feedback}")
    
    if "通过" in feedback and "不通过" not in feedback:
        return {"feedback": feedback, "is_pass": True}
    else:
        return {"feedback": feedback, "is_pass": False}

# 4. 交警函数：决定是结束，还是打回重写
def check_route(state: AgentState):
    if state["is_pass"]:
        return "pass"  # 通过了，去终点
    else:
        return "retry" # 没通过，回炉重造

# ==================== 开始画图 ====================
print("正在编译带循环的工作流...")
workflow = StateGraph(AgentState)

workflow.add_node("poet", poet_node)
workflow.add_node("teacher", teacher_node)

# 从诗人开始
workflow.set_entry_point("poet")

# 诗人写完后，固定去找老师
workflow.add_edge("poet", "teacher")

# 老师审查完后，根据结果走岔路口
workflow.add_conditional_edges(
    "teacher",
    check_route,
    {
        "pass": END,      # 如果通过，结束程序
        "retry": "poet"   # 如果没通过，连回诗人节点（这就形成了循环！）
    }
)

app = workflow.compile()

# ==================== 运行测试 ====================
if __name__ == "__main__":
    print("\n========== 任务开始 ==========")
    # 我们故意给一个刁钻的要求，看它要循环几次
    result = app.invoke({"task": "写一首关于夏天的诗。"})
    print("\n========== 最终过关的诗 ==========")
    print(result["poem"])