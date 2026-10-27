import os
import sqlite3
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()
llm = ChatOpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com/v1",
    model="deepseek-chat",
    temperature=0
)

db_schema = """
表名：sales (销售表)
字段：
- id (整数，主键)
- product_name (文本，产品名称)
- category (文本，产品类别，如'电子产品'、'服装'、'家居')
- sales_amount (整数，销售额)
- sale_date (文本，销售日期，格式'YYYY-MM-DD')
"""

prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个极其资深的数据库工程师。请根据用户的问题，结合以下数据库表结构，编写一条 SQLite 查询语句。\n"
               "【重要要求】：只输出纯 SQL 语句！绝对不要输出任何解释，不要加 ```sql 等任何修饰符！\n\n"
               "【表结构】：\n{schema}"),
    ("user", "问题：{question}")
])

chain = prompt | llm | StrOutputParser()

# ==================== 核心：执行 SQL 函数 ====================
def execute_sql(sql_query):
    """连接数据库并执行 SQL，返回查询结果"""
    try:
        conn = sqlite3.connect('company.db')
        cursor = conn.cursor()
        cursor.execute(sql_query)
        # fetchall() 获取所有查询到的数据行
        results = cursor.fetchall()
        # 获取查询结果的列名（为了后面输出好看）
        columns = [description[0] for description in cursor.description]
        conn.close()
        return True, columns, results
    except Exception as e:
        # 如果报错，返回 False 和错误信息
        return False, [], str(e)

# ==================== 运行测试 ====================
if __name__ == "__main__":
    question = "查一下电子产品总共卖了多少钱？"
    print(f"🙋‍♂️ 用户提问：{question}")
    
    # 1. 生成 SQL
    sql = chain.invoke({"schema": db_schema, "question": question}).strip()
    print(f"🤖 AI 生成的 SQL：{sql}")
    
    # 2. 执行 SQL
    success, columns, data = execute_sql(sql)
    
    if success:
        print("\n✅ 查询成功！结果如下：")
        print(f"【列名】：{columns}")
        for row in data:
            print(f"【数据】：{row}")
    else:
        print(f"\n❌ SQL 执行失败，错误信息：{data}")
        # 进阶玩法：你可以在这里把错误信息 data 再次发给大模型，让它修复 SQL