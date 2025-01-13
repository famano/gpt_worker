import os
import json
from tools import FileReader, FileWriter, PlanMaker, ScriptExecutor, StateUpdater
from connector import OpenAIConnector
from abc import abstractmethod
from dataholder import DataHolder

class Agent:
    @abstractmethod
    def __init__(self, tools: list[type], dataholder: DataHolder):
        pass
    @abstractmethod
    def run(self, order: str) -> list[dict]:
        pass

class Planner(Agent):
    def __init__(self, dataholder: DataHolder, tools: list[type] =None):
        # toolsの要素はTool型のクラス名であることが期待される
        # 将来的にLLMの種類も選べるようにしたい
        if tools != None:
            self.tools = tools
        else:
            self.tools = [FileReader, PlanMaker, StateUpdater]
        self.dataholder = dataholder

    def run(self, order: str ="") -> list[dict]:        
        # making instruction for llm
        if order == "":
            order = "Then expect purpose of your work. Then using PlanMaker tool, make a plan that completes expected purpose of your work.\n"
        else:
            order = (
                "Follow instruction below:\n"
                + order
                + "\n"
                "Then using PlanMaker tool, make a plan that completes expected purpose of your work.\n"
            )

        if self.dataholder.tasklist:
            tasklist = self.dataholder.tasklist
            taskliststr = ""
            for task in tasklist:
                taskliststr += str(task) + "\n"
        else:
            taskliststr = ""

        instruction = (
            "Using FileReader tool, read an important file in the workspace directory. Repeat this until you understand what is going on the directory.\n"
            "Then using StateUpdater tool, write a summery of what is going on in the directory."
            + order
            + "---\n"
            "Below is current situation and task list. If you think these are enough to perform your work, do not change these.\n"
            "If tasks are all completed, delete all of them and make new plan that makes a progress."
            "---\n"
            + "current situation:\n"
            + self.dataholder.state_summery
            + "task list:\n"
            + taskliststr
            + "---\n"
            "Below is structure of the the directory.\n"
            "Each line means ('path', ['files'], ['directories'])\n"
            "---\n"
        )
        
        # get directory structure and append it to instruction
        dir_structure = os.walk(self.dataholder.workspace_dir)
        for i in dir_structure:
            if ("/." in i[0]) or ("/__" in i[0]):
                pass
            else:
                instruction += str(i) + "\n"
        
        messages = [
            {"role": "system", "content": "You are a deligent worker good at make a detailed plan. Use the supplied tools to assist the user."},
            {"role":"user", "content": instruction}
        ]
        # 現状OpenAI限定
        return OpenAIConnector.CreateResponse(messages, self.tools, self.dataholder)

class Worker(Agent):
    def __init__(self, dataholder: DataHolder, tools: list[type] =None):
        if tools != None:
            self.tools = tools
        else:
            self.tools = [FileReader, FileWriter, ScriptExecutor, PlanMaker]
        self.dataholder = dataholder

    def run(self, order: str = "", max_iterations: int = 10) -> list[dict]:
        all_messages = []
        iteration_count = 0
        previous_task_states = None
        
        while True:
            # 実行回数の上限チェック
            if iteration_count >= max_iterations:
                warning_message = {
                    "role": "assistant",
                    "content": f"Warning: Reached maximum number of iterations ({max_iterations}). Stopping execution to prevent infinite loop. Some tasks may remain incomplete."
                }
                all_messages.append(warning_message)
                break
            
            # 未完了のタスクを確認
            incomplete_tasks = self.dataholder.find_task({"done_flg": False})
            if not incomplete_tasks:
                break
            
            # 現在のタスク状態を取得
            current_task_states = [(task.get("task_id", ""), task.get("done_flg", False)) 
                                 for task in self.dataholder.tasklist]
            
            # 前回の状態と比較して変更がないか確認
            if previous_task_states == current_task_states and iteration_count > 0:
                warning_message = {
                    "role": "assistant",
                    "content": "Warning: No progress detected in tasks between iterations. Stopping execution to prevent infinite loop."
                }
                all_messages.append(warning_message)
                break
            
            previous_task_states = current_task_states
            
            if order != "":
                current_order = (
                    "Follow instruction below:\n"
                    + order
                    + "\n"
                )
            else:
                current_order = ""
            
            instruction = (
                "First, check whether you understand current situation. If not, use tools to explore directory until you understand.\n"
                "Then, Working on the task with using tools. If possible, do not ask user anything, do your work as far as you can.\n"
                + current_order
                + "At the end of your work, update situation of task by using PlanMaker, and update current situation using StateUpdater if you needed."
                "Make sure to set done_flg to true for tasks that are actually completed.\n"
                "Current situation is below:\n"
                "---\n"
                + self.dataholder.state_summery
                + "---\n"
                "Your plan of task is below:\n"
                "---\n"
                + str(self.dataholder.tasklist)
                + "\nFocus on completing the remaining incomplete tasks."
            )

            messages = [
                {"role":"system", "content": f"You are a deligent worker working on linux system directory :`{self.dataholder.workspace_dir}`. Use the supplied tools to assist the user."},
                {"role":"user", "content": instruction}
            ]
            
            response = OpenAIConnector.CreateResponse(messages, self.tools, self.dataholder)
            all_messages.extend(response)
            
            iteration_count += 1
            
        return all_messages

class Orchestrator(Agent):
    def __init__(self, dataholder, tools=None):
        # toolsの要素はTool型のクラス名であることが期待される
        # 将来的にLLMの種類も選べるようにしたい
        if tools != None:
            self.tools = tools
        else:
            self.tools = []
        
        self.dataholder = dataholder
    
    def run(self, order=""):
        planner = Planner(self.dataholder)
        messages = planner.run(order=order)
        worker = Worker(self.dataholder)
        messages += worker.run(order=order)
        return messages