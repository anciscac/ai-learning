from typing import TypedDict
from langgraph.graph import StateGraph, END
#1,定义“记事本（state)
#我们用一个字典，里面有个key叫“number”
class MyState(TypedDict):
    number: int

#2.定义两个干活节点（node）
def node_a(state: MyState):
    print("---正在执行节点A---")
    new_number = state["number"] + 10
    return {"number": new_number}

def node_b(state: MyState):
    print("---正在执行节点B---")
    new_number = state["number"] * 2
    return {"number":new_number}

#3定义一个”交警函数“
def decide_path(state: MyState):
    if state["number"] > 50:
        return "go_b"
    else:
        return "go_a"

#4.开始画图
print("正在编译流程图。。。")
workflow = StateGraph(MyState)

workflow.add_node("node_a",node_a)
workflow.add_node("node_b",node_b)

workflow.set_entry_point("node_a")
#设置条件边
workflow.add_conditional_edges(
    "node_a",   #从node_a出发
    decide_path, #用哪个函数决定
    {              #根据返回值，映射到对应的点
        "go_a": "node_a", #如果返回"go_a"，继续回node_a
        "go_b": "node_b"   #如果返回"go_b”，去node_b
    }
)
workflow.add_edge("node_b",END)
app = workflow.compile()
print("\n---第一次测试：初始数字10---")
result = app.invoke({"number": 10})
print("最终结果",result)

print("\n----第二次测试：初始数字 60---")
result = app.invoke({"number":60})
print("最终结果",result)