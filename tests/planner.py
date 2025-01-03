from agents import Planner

planner = Planner()
response = planner.run(".")
for r in response:
    print("role:" + r["role"])
    if "content" in r:
        print(r["content"])
    if "tool_calls" in r :
        print(r["tool_calls"])