import os
from dotenv import load_dotenv
from langchain_community.tools.tavily_search import TavilySearchResults

# 1. 加载环境变量
load_dotenv()

# 2. 初始化搜索工具
# max_results=3 表示每次搜索返回最相关的 3 个网页的结果
search_tool = TavilySearchResults(max_results=3)

# 3. 执行搜索
if __name__ == "__main__":
    query = "2024年巴黎奥运会中国代表团金牌数"
    print(f"🔍 正在联网搜索：{query}...")
    
    # invoke 执行搜索
    results = search_tool.invoke(query)
    
    print("\n✅ 搜索成功！返回的原始数据如下：")
    # 打印前 2 条结果的摘要，看看长什么样
    for i, res in enumerate(results[:2]):
        print(f"\n--- 结果 {i+1} ---")
        print(f"标题: {res.get('title')}")
        print(f"链接: {res.get('url')}")
        # content 是搜索引擎帮我们提取的网页正文精华
        print(f"内容片段: {res.get('content')[:200]}...") 