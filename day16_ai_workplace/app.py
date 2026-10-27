import streamlit as st
import os
import json
import requests
import sqlite3
import pandas as pd
import base64
from dotenv import load_dotenv
from langchain_community.tools.tavily_search import TavilySearchResults

# 1. 页面基础配置（必须是第一个 Streamlit 命令）
st.set_page_config(page_title="全能 AI 工作台", page_icon="🧠", layout="wide")
load_dotenv()
deepseek_key = os.getenv("DEEPSEEK_API_KEY")
silicon_key = os.getenv("SILICON_API_KEY")
tavily_key = os.getenv("TAVILY_API_KEY")

# ==================== 核心：本地持久化模块 ====================
HISTORY_FILE = "chat_history.json"

# 读取本地聊天记录
def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

# 保存聊天记录到本地
def save_history(messages):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(messages, f, ensure_ascii=False, indent=2)

# 初始化 session_state（如果内存里没有，就去本地硬盘读）
if "messages" not in st.session_state:
    st.session_state.messages = load_history()

# ==================== 侧边栏导航 ====================
with st.sidebar:
    st.title("🧠 全能 AI 工作台")
    st.write("---")
    # 使用单选按钮做页面路由
    app_mode = st.radio(
        "请选择功能模式：",
        ["💬 智能聊天", "📊 数据分析 (Text-to-SQL)", "🌐 联网情报官", "🖼️ 图像识别"],
        index=0
    )
    st.write("---")
    if st.button("🗑️ 清空当前聊天记录"):
        st.session_state.messages = []
        save_history([]) # 把空列表存进硬盘
        st.rerun() # 强制刷新页面

# ==================== 主界面渲染 ====================

# 模式一：智能聊天
if app_mode == "💬 智能聊天":
    st.header("💬 与 AI 自由对话")
    
    # 1. 渲染历史聊天记录（从本地读出来的）
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # 2. 接收用户输入
    if prompt := st.chat_input("请输入你的问题..."):
        # 存入内存并显示
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)
        
        # 发送 API 请求
        url = "https://api.deepseek.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {deepseek_key}", "Content-Type": "application/json"}
        data = {
            "model": "deepseek-chat", 
            "messages": st.session_state.messages,
            "stream": True 
        }
        
        response = requests.post(url, headers=headers, json=data, stream=True)

        def generate_chunks():
            for line in response.iter_lines():
                if line:
                    decoded = line.decode('utf-8')
                    if decoded.startswith("data: "):
                        json_str = decoded[6:]
                        if json_str != "[DONE]":
                            try:
                                chunk = json.loads(json_str)
                                delta = chunk["choices"][0]["delta"].get("content", "")
                                yield delta
                            except Exception:
                                pass

        # 3. 流式输出并显示
        with st.chat_message("assistant"):
            full_response = st.write_stream(generate_chunks())
            
        # 4. 将 AI 回答存入内存，并保存到本地硬盘
        st.session_state.messages.append({"role": "assistant", "content": full_response})
        save_history(st.session_state.messages)

# 其他模式的占位符（我们明天来实现）
elif app_mode == "📊 数据分析 (Text-to-SQL)":
    st.header("📊 智能数据分析系统")
    st.write("直接问我关于销售数据的任何问题，我将为你自动编写 SQL 并查询数据库。")
    
    # 数据库表结构说明书
    db_schema = """
    表名:sales (销售表)
    字段：
    - id (整数，主键)
    - product_name (文本，产品名称)
    - category (文本，产品类别，如'电子产品'、'服装'、'家居')
    - sales_amount (整数，销售额)
    - sale_date (文本，销售日期，格式'YYYY-MM-DD')
    """
    
    # 独立的输入框（不和聊天模式的输入框冲突）
    sql_question = st.text_input("请输入你的问题：", placeholder="例如：查一下销量最高的三个产品是什么？", key="sql_input")
    
    if st.button("🚀 开始分析", key="sql_btn"):
        if not sql_question:
            st.warning("请先输入问题！")
        else:
            with st.spinner("AI 正在思考并生成 SQL..."):
                # 1. 构造 Prompt 让 AI 写 SQL (直接调 API，不用 LangChain 也能写)
                url = "https://api.deepseek.com/v1/chat/completions"
                headers = {"Authorization": f"Bearer {deepseek_key}", "Content-Type": "application/json"}
                
                prompt = f"""你是一个极其资深的数据库工程师。请根据用户的问题，结合以下数据库表结构，编写一条 SQLite 查询语句。
【重要要求】：只输出纯 SQL 语句！绝对不要输出任何解释，不要加 ```sql 等任何修饰符！
【表结构】：
{db_schema}
【问题】：
{sql_question}"""
                
                data = {
                    "model": "deepseek-chat",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0
                }
                
                response = requests.post(url, headers=headers, json=data)
                sql_query = response.json()["choices"][0]["message"]["content"].strip()
                
                # 展示生成的 SQL
                st.subheader("💻 AI 生成的 SQL 语句：")
                st.code(sql_query, language="sql")
                
                # 2. 执行 SQL 查询数据
                try:
                    conn = sqlite3.connect('company.db')
                    df = pd.read_sql_query(sql_query, conn)
                    conn.close()
                    
                    st.subheader("📈 查询结果：")
                    st.dataframe(df, use_container_width=True)
                    st.success(f"✅ 共查询到 {len(df)} 条记录。")
                except Exception as e:
                    st.error(f"❌ SQL 执行失败，请换个问法。错误原因：{e}")
elif app_mode == "🌐 联网情报官":
    st.header("🌐 AI 联网情报官")
    st.write("输入任何最新发生的事件或新闻，AI 将自动联网搜索并为你生成总结报告。")
    
    search_query = st.text_input("你想查什么最新资讯？", placeholder="例如：今天科技圈有什么大新闻？", key="search_input")
    
    if st.button("🚀 开始联网搜索", key="search_btn"):
        if not search_query:
            st.warning("请输入搜索内容！")
        elif not tavily_key:
            st.error("未配置 TAVILY_API_KEY，请检查 .env 文件。")
        else:
            with st.spinner("AI 正在疯狂查资料中..."):
                try:
                    # 1. 调用 Tavily 搜索 (使用 LangChain 封装好的工具)
                    search_tool = TavilySearchResults(max_results=3)
                    results = search_tool.invoke(search_query)
                    
                    # 2. 把搜到的网页内容拼接起来
                    context = "\n\n".join([f"来源: {r.get('url')}\n内容: {r.get('content')}" for r in results])
                    
                    # 3. 让 DeepSeek 总结搜索结果
                    url = "https://api.deepseek.com/v1/chat/completions"
                    headers = {"Authorization": f"Bearer {deepseek_key}", "Content-Type": "application/json"}
                    
                    prompt = f"请根据以下联网搜索到的资料，用中文回答用户的问题：{search_query}\n\n参考资料：\n{context}"
                    data = {
                        "model": "deepseek-chat",
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.3
                    }
                    
                    response = requests.post(url, headers=headers, json=data)
                    answer = response.json()["choices"][0]["message"]["content"]
                    
                    # 4. 展示结果
                    st.success("🤖 AI 总结报告：")
                    st.write(answer)
                    
                    # 5. 展示参考来源（商业产品标配）
                    st.subheader("🔗 参考来源：")
                    for r in results:
                        st.markdown(f"- [{r.get('title')}]({r.get('url')})")
                        
                except Exception as e:
                    st.error(f"联网搜索失败：{e}")
elif app_mode == "🖼️ 图像识别":
    st.header("🖼️ AI 视觉分析师")
    st.write("上传任意图片，向 AI 提问！")
    
    uploaded_file = st.file_uploader("请上传一张图片 (JPG/PNG)", type=["jpg", "jpeg", "png"])
    
    if uploaded_file is not None:
        # 预览图片
        st.image(uploaded_file, caption="已上传的图片", use_container_width=True)
        
        vision_question = st.text_input("你想对这张图片问什么？", value="请详细描述一下这张图片里的内容。", key="vision_input")
        
        if st.button("🚀 开始分析图片", key="vision_btn"):
            if not silicon_key:
                st.error("未配置 SILICON_API_KEY，请检查 .env 文件。")
            else:
                with st.spinner("AI 正在仔细端详这张图片..."):
                    try:
                        # 1. 将图片转为 Base64
                        image_bytes = uploaded_file.getvalue()
                        base64_image = base64.b64encode(image_bytes).decode('utf-8')
                        
                        # 2. 调用硅基流动视觉模型（注意：用你之前测试成功的模型ID）
                        url = "https://api.siliconflow.cn/v1/chat/completions"
                        headers = {
                            "Authorization": f"Bearer {silicon_key}",
                            "Content-Type": "application/json"
                        }
                        
                        data = {
                            "model": "Qwen/Qwen3-VL-8B-Instruct", # 如果你这边报错找不到模型，换成 "Qwen/Qwen3-VL-8B-Instruct" 或你测试成功的其他ID
                            "messages": [
                                {
                                    "role": "user",
                                    "content": [
                                        {"type": "text", "text": vision_question},
                                        {
                                            "type": "image_url",
                                            "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                                        }
                                    ]
                                }
                            ]
                        }
                        
                        response = requests.post(url, headers=headers, json=data)
                        result = response.json()
                        
                        if "choices" in result:
                            st.success("🤖 AI 的分析结果：")
                            st.write(result["choices"][0]["message"]["content"])
                        else:
                            st.error(f"API 报错：{result}")
                            
                    except Exception as e:
                        st.error(f"请求失败：{e}")