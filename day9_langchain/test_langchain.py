import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# 1. 加载密钥
load_dotenv()
api_key = os.getenv("DEEPSEEK_API_KEY")

# 2. 初始化 DeepSeek 大模型
llm = ChatOpenAI(
    api_key=api_key,
    base_url="https://api.deepseek.com/v1", # DeepSeek 的接口地址
    model="deepseek-chat",                  # DeepSeek 的对话模型
    temperature=0.7
)

print("🙋‍♂️ 提问：用一句话夸夸我。")
response = llm.invoke("用一句话夸夸我。")
print("\n🤖 AI 回答：")
print(response.content)

print("\n🤖 AI 回答（流式输出）：")
for chunk in llm.stream("给我讲一个关于程序员的笑话。"):
    print(chunk.content, end="", flush=True)