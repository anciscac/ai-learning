import streamlit as st
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate

# 1. 页面基础配置
load_dotenv()
st.set_page_config(page_title="AI 联网情报官", page_icon="🌐")
st.title("🌐 AI 联网情报官")
st.write("输入任何最新发生的事件或新闻，AI 将自动联网搜索并为你生成总结报告。")

# 2. 初始化模型和工具
llm = ChatOpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com/v1",
    model="deepseek-chat",
    temperature=0
)

search_tool = TavilySearchResults(max_results=2)
tools = [search_tool]

# 3. 构建 Agent
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个专业的 AI 情报助手。你可以使用搜索工具来查找最新信息。请用中文回答。"),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"), 
])

agent = create_tool_calling_agent(llm, tools, prompt)
# 注意这里：加上了 return_intermediate_steps=True，为了在网页上显示搜索过程
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, return_intermediate_steps=True)

# ==================== 网页界面 ====================
query = st.text_input("请输入你的问题：", placeholder="例如：今天有什么重大的科技新闻？")

if st.button("🚀 开始联网搜索"):
    if not query:
        st.warning("请输入问题！")
    else:
        with st.spinner("AI 正在疯狂查资料中，请稍候..."):
            # 执行 Agent
            result = agent_executor.invoke({"input": query})
            
            # 1. 展示最终回答
            st.subheader("🤖 AI 总结报告：")
            st.success(result["output"])
            
            # 2. 展示搜索来源（过程透明化，这招在面试时极其加分）
            st.subheader("🔗 参考来源（联网搜索记录）：")
            
            # intermediate_steps 记录了 AI 调用了什么工具，传了什么参数，得到了什么结果
            steps = result.get("intermediate_steps", [])
            if not steps:
                st.info("本次回答 AI 觉得不需要联网，直接使用了自身知识库。")
            else:
                # 遍历所有的搜索动作
                for action, observation in steps:
                    tool_query = action.tool_input.get('query', '')
                    st.write(f"🔍 AI 搜索了：**{tool_query}**")
                    
                    # 把搜到的网页链接以折叠面板展示，免得页面太长
                    with st.expander("展开查看 AI 查到的原始网页信息"):
                        if isinstance(observation, list):
                            for item in observation:
                                title = item.get('title', '无标题')
                                url = item.get('url', '')
                                content = item.get('content', '')
                                st.markdown(f"**[{title}]({url})**")
                                st.caption(content[:200] + "...")