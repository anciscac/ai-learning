import streamlit as st
import os
import sqlite3
import pandas as pd
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# 1. 页面配置与加载
load_dotenv()
st.set_page_config(page_title="智能数据分析师", page_icon="📊")
st.title("📊 AI 智能数据分析师")
st.write("直接问我关于销售数据的任何问题，我将为你自动编写 SQL 并查询数据库。")

llm = ChatOpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com/v1",
    model="deepseek-chat",
    temperature=0
)

# 2. 数据库表结构说明书
db_schema = """
表名：sales (销售表)
字段：
- id (整数，主键)
- product_name (文本，产品名称)
- category (文本，产品类别，如'电子产品'、'服装'、'家居')
- sales_amount (整数，销售额)
- sale_date (文本，销售日期，格式'YYYY-MM-DD')
"""

# 3. 提示词模板
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个极其资深的数据库工程师。请根据用户的问题，结合以下数据库表结构，编写一条 SQLite 查询语句。\n"
               "【重要要求】：只输出纯 SQL 语句！绝对不要输出任何解释，不要加 ```sql 等任何修饰符！\n\n"
               "【表结构】：\n{schema}"),
    ("user", "问题：{question}")
])

chain = prompt | llm | StrOutputParser()

# 4. 执行 SQL 并返回 Pandas DataFrame 的函数
def get_data_from_db(sql_query):
    try:
        conn = sqlite3.connect('company.db')
        # 直接用 pandas 读取 SQL 结果，自动带列名，极度方便！
        df = pd.read_sql_query(sql_query, conn)
        conn.close()
        return True, df, ""
    except Exception as e:
        return False, None, str(e)

# ==================== 网页交互界面 ====================
# 底部输入框
question = st.text_input("请输入你的问题：", placeholder="例如：查一下销量最高的三个产品是什么？")

if st.button("🚀 开始分析"):
    if not question:
        st.warning("请先输入问题！")
    else:
        with st.spinner("AI 正在思考并生成 SQL..."):
            # 1. 生成 SQL
            sql = chain.invoke({"schema": db_schema, "question": question}).strip()
            
            # 把 AI 写的 SQL 展示出来，增加系统的透明度（商业产品标配）
            st.subheader("💻 AI 生成的 SQL 语句：")
            st.code(sql, language="sql")
            
            # 2. 执行查询
            success, df, error_msg = get_data_from_db(sql)
            
            if success:
                st.subheader("📈 查询结果：")
                # 使用 st.dataframe 渲染漂亮的交互式表格
                st.dataframe(df, use_container_width=True)
                st.success(f"✅ 共查询到 {len(df)} 条记录。")
            else:
                st.error(f"❌ SQL 执行失败，错误原因：{error_msg}")
                st.info("💡 提示：可能是 AI 生成的字段名有误，请尝试换一种问法。")