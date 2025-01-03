from agents import Worker

worker = Worker()
state_summery = """
# Workspace Summary

The workspace is composed of several tools and scripts aimed at handling file operations and plan management, focusing primarily on automation through a connector with OpenAI's API.

## Key Components:

1. **tools.py**: It defines tools such as FileReader, FileWriter, PlanMaker, and ScriptExecuter, implementing the base class `Tool` with methods for reading, writing, executing commands, and making plans.

2. **workspace_plan.json**: Contains a task list that outlines the objectives, which include enhancing tool functionality, completing integration, implementing task execution, testing, and documenting processes.

3. **main.py**: Contains a placeholder for the main execution function, `main()`.

4. **agents.py**: Defines `Planner` and `Worker` classes responsible for generating plans and executing tasks, utilizing various tools and connecting to the OpenAI API.

5. **connector.py**: Implements the connection to OpenAI's services, allowing the tools to communicate with the AI for generating responses and executing plans.

6. **playground.ipynb**: A Jupyter notebook for interactive exploration, likely including tests or prototypes related to the planner and tools.

## Directory Structure:

The directory utilizes a typical Python environment with a `.venv` for dependencies and a `.git` for version control. It includes compiled files and various configuration scripts common in a development environment.

## Purpose

The workspace aims to automate task planning and execution using AI, facilitating file manipulation and integrating plan generation with OpenAI's API. It serves as a base for automated task execution informed by AI-derived insights and structured plans.
"""
plan = [{"name": "Integrate Tools and OpenAI API", "description": "Ensure all tools (FileReader, FileWriter, PlanMaker, ScriptExecuter) are properly integrated with OpenAI API using the Connector class.", "done_flg": False}]
response = worker.run(".", plan=plan, state_summery=state_summery)
for r in response:
        print("role:" + r["role"])
        if "content" in r:
            print(r["content"])
        if "tool_calls" in r :
            print(r["tool_calls"])