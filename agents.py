import os
from tools import FileReader, FileWriter, PlanMaker, ScriptExecuter
from connector import OpenAIConnector

class Planner:
    def __init__(self, tools: list[type] =None):
        # toolsの要素はTool型のクラス名であることが期待される
        # 将来的にLLMの種類も選べるようにしたい
        if tools != None:
            self.tools = tools
        else:
            self.tools = [FileReader, FileWriter, PlanMaker]

    def MakePlan(self, workspace_dir: str, order: str ="", plan: list[dict] =None) -> list[str]:
        # get directory structure as tree
        dir_structure = os.walk(workspace_dir)
        
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
            "Then using FileWriter tool, write a summery of what is going on the directory. If there already is one, overwrite it."
            + order
            + "---\n"
            "Below is structure of the the directory.\n"
            "Each line means ('path', ['files'], ['directories'])\n"
            "---\n"
        )
        for i in dir_structure:
            instruction += str(i) + "\n"
        
        messages = [
            {"role": "system", "content": "You are a deligent worker good at make a detailed plan. Use the supplied tools to assist the user."},
            {"role":"user", "content": instruction}
        ]
        # 現状OpenAI限定
        return OpenAIConnector.CreateResponse(messages, self.tools)

class Worker:
    def __init__(self, tools: list[type] =None):
        if tools != None:
            self.tools = tools
        else:
            self.tools = [FileReader, FileWriter, ScriptExecuter]

    def Work(self, wokspace_dir: str, state_summery: str, plan: list[dict]):
        instruction=(
            "First, check whether you understand current situation. If not, use ScriptExecuter to explore directory until you understand.\n"
            #"Then, If you think the plan of the task is not detail enough, use PlanUpdater to update the task.\n"
            "Then, Working on the task with using tools.\n"
            "Current situation is below:\n"
            "---\n"
            + state_summery
            + "---\n"
            "Your plan of task is below:\n"
            "---\n"
            + str(plan)
        )

        messages = [
            {"role":"system", "content": "You are a deligent worker working on linux system directory :`{workspace_dir}`. Use the supplied tools to assist the user."},
            {"role":"user", "content": instruction}
        ]
        return OpenAIConnector.CreateResponse(messages, self.tools)

class ContactPerson:
    pass

if __name__ == "__main__":
    planner = Planner()
    response = planner.MakePlan(".")
    for r in response:
        print("role:" + r["role"])
        print(r["content"])
