import os
import json
from agents import DataHolder, Orchestrator

def main():
    workspace_dir = "."
    tasklist=[]
    state_summery=""

    #.gpt_workerまわりのpathはあとで定数化する
    if os.path.isfile(workspace_dir + "/.gpt_worker/plan.json"):
        with open(workspace_dir + "/.gpt_worker/plan.json", encoding="utf-8") as f:
            tasklist = json.loads(f.read())
    if os.path.isfile(workspace_dir + "/.gpt_worker/state_summery.md"):
        with open(workspace_dir + "/.gpt_worker/state_summery.md", encoding="utf-8") as f:
            state_summery = f.read()

    dataholder = DataHolder(tasklist=tasklist,state_summery=state_summery,workspace_dir=workspace_dir)
    orchestrator = Orchestrator(dataholder=dataholder)
    messages = orchestrator.run()
    for message in messages:
        print("role:" + message["role"])
        if "content" in message:
            print("content:")
            print(message["content"])
        if "tool_calls" in message:
            print("tool_calls:")
            print(message["tool_calls"])

if __name__ == "__main__":
    main()