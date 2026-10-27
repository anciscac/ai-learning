import os
from typing import TypedDict, Literal
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
    temperature=0
)

# 1. 定义黑板（State）：所有 AI 都能看到并修改
class AgentState(TypedDict):
    task: str          # 老板下达的任务
    code: str          # 程序员写的代码
    review: str        # 审查员的意见
    next_agent: str    # 主管决定下一个谁发言

# ==================== 定义 AI 角色（Nodes） ====================

# 2. 角色 A：主管（Supervisor）
def supervisor_node(state: AgentState):
    print("👔 [主管] 正在看进度...")
    # 如果代码是空的，说明还没写，安排程序员写
    if not state.get("code"):
        return {"next_agent": "programmer"}
    # 如果有代码，且审查意见包含“不通过”，安排程序员重写
    elif state.get("review") and "不通过" in state.get("review"):
        return {"next_agent": "programmer"}
    # 如果有代码，且审查意见包含“通过”，或者还没审查过，安排审查员
    elif state.get("code") and not state.get("review"):
        return {"next_agent": "reviewer"}
    # 如果审查通过了，结束
    else:
        return {"next_agent": "finish"}

# 3. 角色 B：程序员（写代码）
def programmer_node(state: AgentState):
    print("👨‍💻 [程序员] 正在疯狂敲代码...")
    # 如果审查员有意见，程序员要参考意见修改
    if state.get("review"):
        prompt_text = f"任务：{state['task']}\n上次的代码：{state['code']}\n审查员的意见：{state['review']}\n请根据意见修改代码。只输出 Python 代码，不要输出任何多余的解释。"
    else:
        prompt_text = f"任务：{state['task']}\n请编写 Python 代码。只输出 Python 代码，不要任何解释。"
        
    prompt = ChatPromptTemplate.from_messages([("user", "{text}")])
    chain = prompt | llm | StrOutputParser()
    new_code = chain.invoke({"text": prompt_text})
    
    # 程序员交卷后，把之前的审查意见清空，等待新一轮审查
    return {"code": new_code, "review": ""}

# 4. 角色 C：审查员（找 Bug）
def reviewer_node(state: AgentState):
    print("🕵️ [审查员] 正在严格审查代码...")
    prompt = ChatPromptTemplate.from_messages([
        ("system", "你是一个极其严格的代码审查员。请检查代码是否有语法错误或逻辑漏洞。如果代码完美，请以'通过'开头回答；如果代码有问题，请以'不通过'开头回答，并指出问题所在。"),
        ("user", "请审查这段代码：\n{code}")
    ])
    chain = prompt | llm | StrOutputParser()
    review_result = chain.invoke({"code": state["code"]})
    return {"review": review_result}
import os
from typing import TypedDict, Literal
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
    temperature=0
)

# 1. 定义黑板（State）：所有 AI 都能看到并修改
class AgentState(TypedDict):
    task: str          # 老板下达的任务
    code: str          # 程序员写的代码
    review: str        # 审查员的意见
    next_agent: str    # 主管决定下一个谁发言

# ==================== 定义 AI 角色（Nodes） ====================

# 2. 角色 A：主管（Supervisor）
def supervisor_node(state: AgentState):
    print("👔 [主管] 正在看进度...")
    # 如果代码是空的，说明还没写，安排程序员写
    if not state.get("code"):
        return {"next_agent": "programmer"}
    # 如果有代码，且审查意见包含“不通过”，安排程序员重写
    elif state.get("review") and "不通过" in state.get("review"):
        return {"next_agent": "programmer"}
    # 如果有代码，且审查意见包含“通过”，或者还没审查过，安排审查员
    elif state.get("code") and not state.get("review"):
        return {"next_agent": "reviewer"}
    # 如果审查通过了，结束
    else:
        return {"next_agent": "finish"}

# 3. 角色 B：程序员（写代码）
def programmer_node(state: AgentState):
    print("👨‍💻 [程序员] 正在疯狂敲代码...")
    # 如果审查员有意见，程序员要参考意见修改
    if state.get("review"):
        prompt_text = f"任务：{state['task']}\n上次的代码：{state['code']}\n审查员的意见：{state['review']}\n请根据意见修改代码。只输出 Python 代码，不要输出任何多余的解释。"
    else:
        prompt_text = f"任务：{state['task']}\n请编写 Python 代码。只输出 Python 代码，不要任何解释。"
        
    prompt = ChatPromptTemplate.from_messages([("user", "{text}")])
    chain = prompt | llm | StrOutputParser()
    new_code = chain.invoke({"text": prompt_text})
    
    # 程序员交卷后，把之前的审查意见清空，等待新一轮审查
    return {"code": new_code, "review": ""}

# 4. 角色 C：审查员（找 Bug）
def reviewer_node(state: AgentState):
    print("🕵️ [审查员] 正在严格审查代码...")
    prompt = ChatPromptTemplate.from_messages([
        ("system", "你是一个极其严格的代码审查员。请检查代码是否有语法错误或逻辑漏洞。如果代码完美，请以'通过'开头回答；如果代码有问题，请以'不通过'开头回答，并指出问题所在。"),
        ("user", "请审查这段代码：\n{code}")
    ])
    chain = prompt | llm | StrOutputParser()
    review_result = chain.invoke({"code": state["code"]})
    return {"review": review_result}
# ==================== 编排多智能体工作流 ====================

print("正在编译多智能体工作流...")
workflow = StateGraph(AgentState)

# 1. 把三个角色加入到图里
workflow.add_node("supervisor", supervisor_node)
workflow.add_node("programmer", programmer_node)
workflow.add_node("reviewer", reviewer_node)

# 2. 入口设置为主管（老板把任务直接扔给主管）
workflow.set_entry_point("supervisor")

# 3. 主管的决定（条件边）：主管看完状态后，决定下一个让谁干活
workflow.add_conditional_edges(
    "supervisor",
    lambda state: state["next_agent"], # 读取主管做出的决定
    {
        "programmer": "programmer", # 去程序员那里
        "reviewer": "reviewer",     # 去审查员那里
        "finish": END               # 结束
    }
)

# 4. 程序员的去向（固定边）：程序员干完活，必须汇报给主管
workflow.add_edge("programmer", "supervisor")

# 5. 审查员的去向（固定边）：审查员审完，也必须汇报给主管
workflow.add_edge("reviewer", "supervisor")

# 编译成可执行的应用
app = workflow.compile()

# ==================== 运行测试 ====================
if __name__ == "__main__":
    print("\n========== 老板下达任务 ==========")
    task = "写一个 Python 函数，计算两个数字的乘积。"
    print(f"📝 任务：{task}\n")
    
    # 初始状态：只有任务，其他都是空的
    inputs = {"task": task, "code": "", "review": "", "next_agent": ""}
    
    # 运行工作流，限制最多循环 10 次（防止 AI 陷入死循环卡死）
    result = app.invoke(inputs, {"recursion_limit": 10})
    
    print("\n========== 最终交付的代码 ==========")
    print(result["code"])
    print("\n========== 最终审查意见 ==========")
    print(result["review"])