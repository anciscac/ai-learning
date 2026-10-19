import pandas as pd
df = pd.read_csv("users.csv")
print("----第一部分：查看原始数据前3行---")
print(df.head(3))

print("\n----第二部分：数据统计---")
avg_time = df['使用时长'].mean()
print(f"所有用户的平均使用时长是:{avg_time}分钟")

print("\n----第三部分：条件筛选---")
#df['使用时长'] > 60会判断每一行，把ture的行保留下来
active_users = df[df['使用时长'] > 60]
print(active_users)

print("\n---第四部分:精准定位到不满意的用户----")
unhappy_users = df[df['满意度'] == '不满意']
unhappy_names = unhappy_users['用户名'].tolist()
print(f"发现不满意用户：{unhappy_names}")