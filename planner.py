from abc import abstractmethod
import os
import openai
from openai import OpenAI
from tools import FileReader, PlanMaker
from connector import OpenAIConnector

class Planner:
    def __init__(self, tools: list[type] =None):
        # toolsの要素はTool型のクラス名であることが期待される
        # 将来的にLLMの種類も選べるようにしたい
        if tools != None:
            self.tools = tools
        else:
            self.tools = [FileReader, PlanMaker]

    def MakePlan(self, workspace_dir: str, order: str ="", plan=None):
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

if __name__ == "__main__":
    planner = Planner()
    response = planner.MakePlan(".")
    print(response)
