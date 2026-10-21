import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("ZHIPU_API_KEY")

def add_numbers(a,b):
    print(f"[后台运行]工具被调用了：计算 {a} + {b}")
    return a + b

tools = [
    {
        "type": "function",
        "function": {
            "name": "add_numbers",
            "description": "计算两个数字的加法",
            "parameters":{
                "type": "object",
                "properties": {
                    "a": {"type": "number","description": "第一个数字"},
                    "b": {"type": "number","description": "第二个数字"}
            },
                 "required": ["a", "b"]
        }
    }}
]

user_question = "帮我算一下 1234 加上 5678 等于多少？"
messages = [{"role": "user", "content": user_question}]

print(f"🙋‍♂️ 用户提问：{user_question}\n")

# 4. 第一次请求大模型，带上 tools 说明书
url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
data = {
    "model": "glm-4-flash",
    "messages": messages,
    "tools": tools # 重点：把说明书传给 AI
}

response = requests.post(url, headers=headers, json=data)
result = response.json()
message = result["choices"][0]["message"]

# 5. 检查 AI 是正常回答，还是申请调用工具
if message.get("tool_calls"):
    print("🤖 AI 决定调用工具！")
    
    # 提取 AI 申请调用的工具信息
    tool_call = message["tool_calls"][0]
    function_name = tool_call["function"]["name"]
    # AI 会返回一个 JSON 字符串，我们把它转成 Python 字典
    arguments = json.loads(tool_call["function"]["arguments"])
    
    print(f"➡️ AI 申请调用的函数是：{function_name}")
    print(f"➡️ AI 提取的参数是：{arguments}\n")
    
    # 6. 在本地真正执行工具函数（假设 AI 传的参数是对的）
    if function_name == "add_numbers":
        tool_result = add_numbers(arguments["a"], arguments["b"])
        print(f"✅ [后台结果] 计算完成，结果是：{tool_result}\n")
        
        # 7. 把工具执行的结果，追加到对话历史里
        # 注意：智谱要求 tool 消息必须包含 tool_call_id
        messages.append(message) # 先存入 AI 刚才的调用申请
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call["id"],
            "content": str(tool_result)
        })
        
        # 8. 第二次请求大模型，把算好的结果告诉它，让它总结
        print("🤖 正在把结果发给 AI 进行总结...")
        data_final = {
            "model": "glm-4-flash",
            "messages": messages
        }
        final_response = requests.post(url, headers=headers, json=data_final)
        final_answer = final_response.json()["choices"][0]["message"]["content"]
        
        print(f"\n🎉 AI 最终回复：{final_answer}")

else:
    # 如果 AI 没调用工具，直接回答了
    print(f"🤖 AI 直接回复：{message['content']}")