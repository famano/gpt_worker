import os
import json
from agents import DataHolder, Orchestrator
from constants import WORKSPACE_DIR, PLAN_FILE, STATE_SUMMARY_FILE

def main():
    tasklist = []
    state_summery = ""

    if os.path.isfile(PLAN_FILE):
        with open(PLAN_FILE, encoding="utf-8") as f:
            tasklist = json.loads(f.read())
    if os.path.isfile(STATE_SUMMARY_FILE):
        with open(STATE_SUMMARY_FILE, encoding="utf-8") as f:
            state_summery = f.read()

    dataholder = DataHolder(tasklist=tasklist, state_summery=state_summery, workspace_dir=WORKSPACE_DIR)
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
