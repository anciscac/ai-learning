import os
import requests
from dotenv import load_dotenv

#加载环境变量
load_dotenv()
api_key = os.getenv("ZHIPU_API_KEY")

if not api_key:
    print("没找到密钥，请检查 .env路径！")
    exit()

print("正在呼叫免费大模型。。。。")

#智谱的API地址
url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
headers = {
    "Content-Type": "application/json",
    "Authorization":f"Bearer {api_key}"
}

#这次我们让他做点实事
data = {
    "model": "glm-4-flash",#免费模型
    "messages": [{"role": "user","content": "请用一句简短的话来鼓励一下我。"}
    ]
}

#发送请求
response = requests.post(url,headers=headers,json = data)
result = response.json()

#检查是否出错
if "choices" in result:
    print("\n免费AI回复：")
    print(result["choices"][0]["message"]["content"])
else:
    print("\n服务器拒绝了请求，错误信息如下：")
    print(result)