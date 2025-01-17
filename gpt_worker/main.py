import os
import argparse
import json
from gpt_worker.agents import DataHolder, Orchestrator
from gpt_worker.constants import DEFAULT_WORKSPACE_DIR, PLAN_FILE, STATE_SUMMARY_FILE, DEFAULT_MODEL

# Main script for task automation
# Orchestrates task execution by reading task lists and state summaries,
# and utilizes agents to perform tasks using the OpenAI API

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--order", type=str, help="order that pass to gpt_worker")
    parser.add_argument("-m", "--model", type=str, help="llm model name")
    parser.add_argument("-d", "--directory", help="directory that gpt_worker should work on")
    args = parser.parse_args()

    # Determine the task order, model, and workspace directory
    order = args.order if args.order else ""
    model = args.model if args.model else DEFAULT_MODEL
    directory = args.directory if args.directory else DEFAULT_WORKSPACE_DIR

    # Initialize task list and state summary
    tasklist = []
    state_summary = ""

    # Retrieve task list from PLAN_FILE
    plan_dir = os.path.join(directory, PLAN_FILE)
    if os.path.isfile(plan_dir):
        with open(plan_dir, encoding="utf-8") as f:
            tasklist = json.loads(f.read())

    # Retrieve state summary from STATE_SUMMARY_FILE
    summary_dir = os.path.join(directory, STATE_SUMMARY_FILE)
    if os.path.isfile(summary_dir):
        with open(summary_dir, encoding="utf-8") as f:
            state_summary = f.read()

    # Initialize DataHolder and Orchestrator
    dataholder = DataHolder(tasklist=tasklist, state_summary=state_summary, workspace_dir=directory)
    orchestrator = Orchestrator(dataholder=dataholder)

    # Execute tasks using Orchestrator's run method
    messages = orchestrator.run(order=order, model=model)
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
