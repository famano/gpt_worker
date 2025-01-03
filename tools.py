from abc import abstractmethod
import os
import json
from pydantic import BaseModel, Field
import subprocess

class Tool(BaseModel):
    @abstractmethod
    def run(args: dict) -> dict:
        pass

class FileReader(Tool):
    "Read the contents of designated file. This function returns contents as text."
    path: str = Field(..., description="relative path of target file to read.")
    
    def run(args: dict) -> dict:
        with open(args["path"]) as f:
            return {
                "path": args["path"],
                "content": f.read()
            }

class FileWriter(Tool):
    "write given content to designated file. This function overwrites the file."
    path: str = Field(..., description="relative path of target file to write.")
    content: str = Field(..., description="content to write.")

    def run(args):
        dir = os.path.dirname(args["path"])
        if dir != "":
            os.makedirs(dir, exist_ok=True)
        with open(args["path"], mode="w") as f:
            f.write(args["content"])
        return {
            "path": args["path"],
            "success": True 
        }

class StateUpdater(Tool):
    state_summery: str = Field(..., description="summery of current situation.")

    def run(args):
        dataholder = args["dataholder"]
        dataholder.state_summery = args["state_summery"]

        target_path = dataholder.workspace_dir + "/.gpt_worker/state_summery.md"
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        with open(target_path, mode="w") as f:
            f.write(args["state_summery"])
        return {
            "success": True 
        }

class Task(BaseModel):
    name: str
    description: str
    next_step :str = Field(..., description="concrete and detailed explanation of what to do next.")
    done_flg: bool

class PlanMaker(Tool):
    "Make a plan as list of tasks. If a plan already exists, overwrite it."
    tasklist: list[Task]

    def run(args: dict) -> dict:
        dataholder = args["dataholder"]
        
        target_path = dataholder.workspace_dir + "/.gpt_worker/plan.json"
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        with open(target_path, mode="w") as f:
            f.write(json.dumps(args["tasklist"]))
        
        dataholder.tasklist = args["tasklist"]

        return {
            "success": True,
        }
    
class ScriptExecutor(Tool):
    "Execute shell script and return result if user permitted"
    script: str = Field(..., description="Linux shell script to execute")
        
    def run(args: dict) -> dict:
        print("The agent want to execute following script.")
        print("---")
        print(args["script"])
        print("---")
        print("enter 'y' to permission. If else, abort.")
        usr_permit = input()
        if usr_permit == "y":
            byte = subprocess.Popen(args["script"], stdout=subprocess.PIPE, shell=True).communicate()[0]
            result = {
                "user_permitted": True,
                "result": byte.decode("utf-8")
            }
        else:
            result = {
                "user_permitted": False,
                "result": ""
            }
        return result