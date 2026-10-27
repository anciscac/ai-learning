import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# 1. 加载模型
load_dotenv()
llm = ChatOpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com/v1",
    model="deepseek-chat",
    temperature=0 # 写 SQL 必须严谨，温度设为 0
)

# 2. 定义数据库的“说明书”（Schema）
db_schema = """
表名：sales (销售表)
字段：
- id (整数，主键)
- product_name (文本，产品名称)
- category (文本，产品类别，如'电子产品'、'服装'、'家居')
- sales_amount (整数，销售额)
- sale_date (文本，销售日期，格式'YYYY-MM-DD')
"""

# 3. 构造超级 Prompt
# 注意：这里强制要求 AI 只输出 SQL 代码，不要带任何 Markdown 格式（比如 ```sql）
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个极其资深的数据库工程师。请根据用户的问题，结合以下数据库表结构，编写一条 SQLite 查询语句。\n"
               "【重要要求】：只输出纯 SQL 语句！绝对不要输出任何解释，不要加 ```sql 等任何修饰符！\n\n"
               "【表结构】：\n{schema}"),
    ("user", "问题：{question}")
])

# 4. 构建链
chain = prompt | llm | StrOutputParser()

# 5. 测试提问
if __name__ == "__main__":
    questions = [
        "电子产品总共卖了多少钱？",
        "查一下销量最高的那个产品的名字",
        "10月15号之后卖出的商品有哪些？"
    ]
    
    for q in questions:
        print(f"\n🙋‍♂️ 用户提问：{q}")
        # 调用链，生成 SQL
        sql = chain.invoke({"schema": db_schema, "question": q}).strip()
        print(f"🤖 AI 生成的 SQL：\n{sql}")