import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

# 1. 加载密钥并初始化模型（跟你刚才跑通的一样）
load_dotenv()
api_key = os.getenv("DEEPSEEK_API_KEY")
llm = ChatOpenAI(
    api_key=api_key,
    base_url="https://api.deepseek.com/v1",
    model="deepseek-chat",
    temperature=0.7
)

# 2. 打造一个“提示词模板”
# 这个模板包含：系统人设 + 历史对话（MessagesPlaceholder） + 用户最新提问
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个幽默风趣的AI助手。"),
    MessagesPlaceholder(variable_name="history"), # 这里是个占位符，会自动填入历史记录
    ("human", "{input}")
])

# 3. 把提示词和模型串成一条“链”
chain = prompt | llm

# 4. 准备一个内存，用来存历史聊天记录
store = {}

# 获取历史记录的函数
def get_session_history(session_id: str):
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]

# 5. 给这条链加上“记忆功能”
with_memory_chain = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="history",
)

# 6. 开始多轮对话测试
session_id = "user_123" # 给这次对话打个标签

print("--- 第一轮对话 ---")
res1 = with_memory_chain.invoke(
    {"input": "你好，我叫李雷，我是一名化工厂的中控员。"},
    config={"configurable": {"session_id": session_id}}
)
print(f"🤖 AI: {res1.content}\n")

print("--- 第二轮对话 ---")
res2 = with_memory_chain.invoke(
    {"input": "你还记得我叫什么名字吗？我是做什么工作的？"},
    config={"configurable": {"session_id": session_id}}
)
print(f"🤖 AI: {res2.content}")