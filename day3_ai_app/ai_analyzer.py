import os
import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("DEEPSEEK_API_KEY")
df = pd.read_csv("users.csv")
unhappy_users = df[df['满意度'] == '不满意']
unhappy_names = unhappy_users['用户名'].tolist()

if not unhappy_names:
    print("数据中没有不满意的用户，不需要分析")
    exit()
print(f"发现不满意客户:{unhappy_names},正在请求AI生成挽回策略。。。\n")

url = "https://api.deepseek.com/chat/completions"
headers = {
    "Content-Type":"application/json",
    "Authorization":f"Bearer {api_key}"
    }
prompt_text = f"我们的产品有以下几个不满意的用户:{unhappy_names}。请帮我写一段简短的用户回访话术，安抚他们的情绪并了解具体情况。"

data = {
    "model":"deepseek-chat",
    "message": [
        {"role": "system","content":"你是一个资深的用户运营专家。"},
        {"role": "user","content": prompt_text}
    ]
}

try:
    response = requests.post(url,headers=headers,json=data)
    result = response.json()

    ai_reply = result["choices"][0]["messages"]["content"]

    print("----AI生成的挽回话术----")
    print(ai_reply)
    print("============================")
except Exception as e:
    print(f"请求AI失败，请检查网络或API KEY。错误信息：{e}")