import os
import json
from typing import List, Dict, Type, Optional
from abc import ABC, abstractmethod
from gpt_worker.tools import FileReader, FileWriter, PlanMaker, ScriptExecutor, StateUpdater
from gpt_worker.connector import OpenAIConnector
from gpt_worker.dataholder import DataHolder
from gpt_worker.constants import MAX_ITERATIONS, DEFAULT_MODEL

# Base Agent class using Abstract Base Class
class Agent(ABC):
    @abstractmethod
    def __init__(self, dataholder: DataHolder, tools: Optional[List[Type]] = None):
        pass

    @abstractmethod
    def run(self, order: str = ""):
        pass

# Planner class that utilizes tools to create task plans
class Planner(Agent):
    DEFAULT_TOOLS = [FileReader, PlanMaker, StateUpdater]

    def __init__(self, dataholder: DataHolder, tools: Optional[List[Type]] = None):
        self.tools = tools if tools is not None else self.DEFAULT_TOOLS
        self.dataholder = dataholder

    def run(self, order: str = "", model=DEFAULT_MODEL):
        """
        Constructs instructions for LLM to generate intelligent plans. Fetches the current
        directory structure and state summary to provide context to the LLM.
        """
        if order == "":
            order = "Then expect purpose of your work. Then using PlanMaker tool, make a plan that completes expected purpose of your work.\n"
        else:
            order = (
                "Follow instruction below:\n"
                + order
                + "\n"
                "Then using PlanMaker tool, make a plan that completes expected purpose of your work.\n"
            )

        # Parse existing tasks and state summary for contextual information
        taskliststr = ""
        if self.dataholder.tasklist:
            for task in self.dataholder.tasklist:
                taskliststr += str(task) + "\n"

        instruction = (
            "Using FileReader tool, read an important file in the workspace directory. Read files one by one. Do not read multiple files at once. Repeat this until you understand what is going on in the directory.\n"
            "Then using StateUpdater tool, write a summary of what is going on in the directory."
            + order
            + "---\n"
            "Below is the current situation and task list. If you think these are enough to perform your work, do not change these.\n"
            "If tasks are all completed, delete all of them and make a new plan that makes progress."
            "---\n"
            + "current situation:\n"
            + self.dataholder.state_summary
            + "task list:\n"
            + taskliststr
            + "---\n"
            "Below is the structure of the directory.\n"
            "Each line means ('path', ['files'], ['directories'])\n"
            "---\n"
        )
        
        dir_structure = os.walk(self.dataholder.workspace_dir)
        for i in dir_structure:
            if ("/." in i[0]) or ("/__" in i[0]):
                continue
            instruction += str(i) + "\n"
        
        messages = [
            {"role": "system", "content": "You are a diligent worker good at making detailed plans. Use the supplied tools to assist the user."},
            {"role":"user", "content": instruction}
        ]

        for message in OpenAIConnector.CreateResponse(messages, self.tools, self.dataholder, model):
            yield message

# Worker class that executes tasks and utilizes various tools to assist 
class Worker(Agent):
    DEFAULT_TOOLS = [FileReader, FileWriter, ScriptExecutor, PlanMaker]

    def __init__(self, dataholder: DataHolder, tools: Optional[List[Type]] = None):
        self.tools = tools if tools is not None else self.DEFAULT_TOOLS
        self.dataholder = dataholder

    def run(self, order: str = "", max_iterations: int = MAX_ITERATIONS, model=DEFAULT_MODEL):
        """
        Executes tasks based on the current task list and updates their status iteratively. Stops execution in
case of stagnation in progress or upon reaching a maximum number of iterations.
        """
        iteration_count = 0
        previous_task_states = None

        while True:
            # Limit the number of iterations to prevent infinite loops
            if iteration_count >= max_iterations:
                yield {
                    "role": "assistant",
                    "content": f"Warning: Reached maximum number of iterations ({max_iterations}). Stopping execution to prevent infinite loop. Some tasks may remain incomplete."
                }
                break

            # Check for incomplete tasks
            incomplete_tasks = self.dataholder.find_task({"done_flg": False})
            if not incomplete_tasks:
                break

            current_task_states = [(task.get("task_id", ""), task.get("done_flg", False)) for task in self.dataholder.tasklist]

            if previous_task_states == current_task_states and iteration_count > 0:
                yield {
                    "role": "assistant",
                    "content": "Warning: No progress detected in tasks between iterations. Stopping execution to prevent infinite loop."
                }
                break

            previous_task_states = current_task_states

            current_order = ("Follow instruction below:\n" + order + "\n") if order else ""

            instruction = (
                "First, check whether you understand the current situation. If not, use tools to explore the directory until you understand. Read files one by one. Do not read multiple files at once.\n"
                "Then, work on the task using tools. If possible, do not ask the user anything. Do your work as far as you can.\n"
                + current_order
                + "At the end of your work, update the situation of the task using PlanMaker, and update the current situation using StateUpdater if needed."
                "Make sure to set done_flg to true for tasks that are actually completed.\n"
                "Current situation is below:\n"
                "---\n"
                + self.dataholder.state_summary
                + "---\n"
                "Your plan of task is below:\n"
                "---\n"
                + str(self.dataholder.tasklist)
                + "\nFocus on completing the remaining incomplete tasks."
            )

            messages = [
                {"role":"system", "content": f"You are a diligent worker working on Linux system directory :`{self.dataholder.workspace_dir}`. Use the supplied tools to assist the user."},
                {"role":"user", "content": instruction}
            ]

            for message in OpenAIConnector.CreateResponse(messages, self.tools, self.dataholder, model):
                yield message

            iteration_count += 1

# Orchestrator class that combines planning and working agents for comprehensive task management
class Orchestrator(Agent):
    def __init__(self, dataholder: DataHolder, tools: Optional[List[Type]] = None):
        self.tools = tools if tools is not None else []
        self.dataholder = dataholder

    def run(self, order: str = "", model: str=DEFAULT_MODEL):
        """
        Deploys the Planner to create an executable task list and then uses the Worker to fulfill the planned tasks.
        """
        planner = Planner(self.dataholder)
        for message in planner.run(order=order, model=model):
            yield message
        
        worker = Worker(self.dataholder)
        for message in worker.run(order=order, model=model):
            yield message
