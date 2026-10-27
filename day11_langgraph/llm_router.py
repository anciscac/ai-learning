import os 
from typing import TypedDict, Literal
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langgraph.graph import StateGraph,END

load_dotenv()

llm = ChatOpenAI(
    api_key = os.getenv("DEEPSEEK_API_KEY"),
    base_url = "https://api.deepseek.com/v1",
    model = "deepseek-chat",
    temperature = 0
)
class AgentState(TypedDict):
    question: str
    decision: str
    answer: str

def router_node(state: AgentState):
    print("---正在执行，路由决策节点---")
    prompt = ChatPromptTemplate.from_messages([
        ("system","你是一个意图分类器。如果用户的问题是数学问题，请回复‘math’；如果是其他问题，请回复‘chat’。请只回复一个单词，不要包含任何其他标点和废话。"),
        ("user","{question}") 
    ])
    chain = prompt | llm | StrOutputParser()
    decision = chain.invoke({"question": state["question"]}).strip().lower()

    if "math" in decision:
        decision = "math"
    else:
        decision = "chat"
        
    print(f"🤖 大模型判断意图为: {decision}")
    return {"decision": decision}

def math_node(state: AgentState):
    print("--- 🧮 正在执行：数学专家节点 ---")
    prompt = ChatPromptTemplate.from_messages([
        ("system", "你是一个严谨的数学老师。请一步步计算用户的数学题。"),
        ("user", "{question}")
    ])
    chain = prompt | llm | StrOutputParser()
    answer = chain.invoke({"question": state["question"]})
    return {"answer": answer}

def chat_node(state: AgentState):
    print("--- 💬 正在执行：闲聊专家节点 ---")
    prompt = ChatPromptTemplate.from_messages([
        ("system", "你是一个幽默风趣的AI助手。请回答用户的问题。"),
        ("user", "{question}")
    ])
    chain = prompt | llm | StrOutputParser()
    answer = chain.invoke({"question": state["question"]})
    return {"answer": answer}
print("正在编译工作流。。。")
workflow = StateGraph(AgentState)

workflow.add_node("router",router_node)
workflow.add_node("math_expert", math_node)
workflow.add_node("chat_expert",chat_node)

workflow.set_entry_point("router")

workflow.add_conditional_edges(
    "router",
    lambda state: state["decision"],
    {

        "math": "math_expert",
        "chat": "chat_expert"
    }
)
workflow.add_edge("math_expert",END)
workflow.add_edge("chat_expert",END)
app = workflow.compile()

if __name__ =="__main__":
    print("\n========测试1:数学问题=======")
    result1 = app.invoke({"question":"123乘以45等于多少？","decision":"","answer":""})
    print(f"最终答案:\n{result1['answer']}\n")

    print("\n========== 测试 2：闲聊问题 ==========")
    result2 = app.invoke({"question": "你今天心情怎么样？给我讲个笑话吧。", "decision": "", "answer": ""})
    print(f"最终答案：\n{result2['answer']}\n")