import os
from tools import FileReader, FileWriter, PlanMaker, ScriptExecuter, StateUpdater
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
            )

        instruction = (
            "Using FileReader tool, read an important file in the workspace directory. Repeat this until you understand what is going on the directory.\n"
            "Then using StateUpdater tool, write a summery of what is going on the directory. If there already is one, overwrite it."
            + order
            + "---\n"
            "Below is structure of the the directory.\n"
            "Each line means ('path', ['files'], ['directories'])\n"
            "---\n"
        )
        
        # get directory structure and append it to instruction
        dir_structure = os.walk(dataholder.workspace_dir)
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
            self.tools = [FileReader, FileWriter, ScriptExecuter, PlanMaker]
        self.dataholder = dataholder

    def run(self, order: str = "") -> list[dict]:
        if order != "":
            order = (
                "Follow instruction below:\n"
                + order
                + "\n"
            )
        
        instruction = (
            "First, check whether you understand current situation. If not, use tools to explore directory until you understand.\n"
            #"Then, If you think the plan of the task is not detail enough, use PlanUpdater to update the task.\n"
            "Then, Working on the task with using tools. If possible, do not ask user anything, do your work as far as you can.\n"
            + order
            + "At the end of your work, update situation of task by using PlanMaker."
            "Current situation is below:\n"
            "---\n"
            + self.dataholder.state_summery
            + "---\n"
            "Your plan of task is below:\n"
            "---\n"
            + str(self.dataholder.tasklist)
        )

        messages = [
            {"role":"system", "content": f"You are a deligent worker working on linux system directory :`{self.dataholder.workspace_dir}`. Use the supplied tools to assist the user."},
            {"role":"user", "content": instruction}
        ]
        return OpenAIConnector.CreateResponse(messages, self.tools, self.dataholder)

if __name__ == "__main__":
    workspace_dir = "../gpt_worker_test"
    dataholder = DataHolder(tasklist=[],state_summery="",workspace_dir=workspace_dir)
    planner = Planner(dataholder=dataholder)
    worker = Worker(dataholder=dataholder)
    messages = planner.run()
    for message in messages:
        print("role:" + message["role"])
        if "content" in message:
            print("content:")
            print(message["content"])
        if "tool_calls" in message:
            print("tool_calls:")
            print(message["tool_calls"])

    messages = worker.run()
    for message in messages:
        print("role:" + message["role"])
        if "content" in message:
            print("content:")
            print(message["content"])
        if "tool_calls" in message:
            print("tool_calls:")
            print(message["tool_calls"])
