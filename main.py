import os
import argparse
import json
from agents import DataHolder, Orchestrator
from constants import DEFAULT_WORKSPACE_DIR, PLAN_FILE, STATE_SUMMARY_FILE, DEFAULT_MODEL

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--order", type=str, help="order that pass to gpt_worker")
    parser.add_argument("-m", "--model", type=str, help="llm model name")
    parser.add_argument("-d", "-directory", help="directory that gpt_worker shold working on")
    args = parser.parse_args()

    if args.order:
        order = args.order
    else:
        order = ""

    if args.model:
        model = args.model
    else:
        model = DEFAULT_MODEL

    if args.directory:
        directory = args.directory
    else:
        directory = DEFAULT_WORKSPACE_DIR

    tasklist = []
    state_summary = ""

    plan_dir = os.path.join(directory, PLAN_FILE)
    if os.path.isfile(plan_dir):
        with open(plan_dir, encoding="utf-8") as f:
            tasklist = json.loads(f.read())
    summary_dir = os.path.join(directory, STATE_SUMMARY_FILE)
    if os.path.isfile(summary_dir):
        with open(summary_dir, encoding="utf-8") as f:
            state_summary = f.read()

    dataholder = DataHolder(tasklist=tasklist, state_summary=state_summary, workspace_dir=directory)
    orchestrator = Orchestrator(dataholder=dataholder)
    messages = orchestrator.run(order=order)
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
