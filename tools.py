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
        try:
            with open(args["path"]) as f:
                return {
                    "path": args["path"],
                    "content": f.read()
                }
        except Exception as e:
            return {
                "success": False,
                "content": str(e)
            }

class FileWriter(Tool):
    "write given content to designated file. This function overwrites the file."
    path: str = Field(..., description="relative path of target file to write.")
    content: str = Field(..., description="content to write.")

    def run(args):
        try:
            dir = os.path.dirname(args["path"])
            if dir != "":
                os.makedirs(dir, exist_ok=True)
            with open(args["path"], mode="w") as f:
                f.write(args["content"])
            return {
                "path": args["path"],
                "success": True 
            }
        except Exception as e:
            return {
                "success": False,
                "content": str(e)
            }

class StateUpdater(Tool):
    state_summery: str = Field(..., description="summery of current situation.")

    def run(args):
        dataholder = args["dataholder"]
        dataholder.state_summery = args["state_summery"]

        try:    
            target_path = dataholder.workspace_dir + "/.gpt_worker/state_summery.md"
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            with open(target_path, mode="w") as f:
                f.write(args["state_summery"])
            return {
                "success": True 
            }
        except Exception as e:
            return {
                "success": False,
                "content": str(e)
            }

class Task(BaseModel):
    name: str
    description: str
    next_step :str = Field(..., description="concrete and detailed explanation of what to do next.")
    done_flg: bool
    #生成時にtask_idが足されることに注意

class PlanMaker(Tool):
    "Make a plan as list of tasks. If a plan already exists, overwrite it."
    tasklist: list[Task]

    def run(args: dict) -> dict:
        dataholder = args["dataholder"]
        target_path = dataholder.workspace_dir + "/.gpt_worker/plan.json"
        tasklist = args["tasklist"]
        #indexをそのままidにしている。要改善。LLMが認識可能なら短めのUUIDでもよいか
        for i, task in enumerate(tasklist):
            task["task_id"] = i

        try:
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            with open(target_path, mode="w") as f:
                f.write(json.dumps(tasklist))
            
            dataholder.tasklist = tasklist

            return {
                "success": True,
            }
        except Exception as e:
            return {
                "success": False,
                "content": str(e)
            }
    
class ScriptExecutor(Tool):
    "Execute shell script and return result if user permitted"
    script: str = Field(..., description="Linux shell script to execute")
        
    def run(args: dict) -> dict:
        print("The agent want to execute following script.")
        print("---")
        print(args["script"])
        print("---")
        print("Enter 'y' to permission. If else, abort.")
        usr_permit = input()
        if usr_permit == "y":
            try:
                byte = subprocess.Popen(args["script"], stdout=subprocess.PIPE, shell=True).communicate()[0]
                result = {
                    "user_permitted": True,
                    "result": byte.decode("utf-8")
                }
            except Exception as e:
                return {
                    "success": False,
                    "content": str(e)
                }
        else:
            result = {
                "user_permitted": False,
                "result": ""
            }
        return result