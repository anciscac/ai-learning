import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults
# 引入构建 Agent 的核心组件
from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

# 1. 初始化大模型（大脑）
llm = ChatOpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com/v1",
    model="deepseek-chat",
    temperature=0
)

# 2. 初始化搜索工具（手脚）
search_tool = TavilySearchResults(max_results=2)
tools = [search_tool]

# 3. 定义 Agent 的提示词模板
# 这里必须有 agent_scratchpad，这是给 AI 留的“草稿纸”，用来记录它的思考过程
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个专业的 AI 情报助手。你可以使用搜索工具来查找最新信息。请用中文回答。"),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"), 
])

# 4. 将模型、工具和提示词组装成一个 Agent
agent = create_tool_calling_agent(llm, tools, prompt)

# 5. 创建 AgentExecutor（执行器），驱动整个思考循环
# verbose=True 会在终端打印出 AI 的详细思考过程，方便我们看它到底有没有去查网
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# ==================== 运行测试 ====================
if __name__ == "__main__":
    print("🤖 AI 情报官已就绪！\n")
    
    # 测试 1：不需要联网的常识问题
    print("========== 测试 1：常识问题 ==========")
    res1 = agent_executor.invoke({"input": "你好，请用一句话介绍一下你自己。"})
    print(f"\n🎉 最终回答：\n{res1['output']}\n")
    
    print("-" * 50)
    
    # 测试 2：必须联网才能回答的实时问题
    print("\n========== 测试 2：需要实时信息的问题 ==========")
    res2 = agent_executor.invoke({"input": "2026年10月24日到2026年10月27日科技圈有什么重大的 AI 新闻？"})
    print(f"\n🎉 最终回答：\n{res2['output']}\n")