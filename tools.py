from abc import abstractmethod
import os
import json
from pydantic import BaseModel, Field

class Tool(BaseModel):
    @abstractmethod
    def Run(args: dict) -> dict:
        pass

class FileReader(Tool):
    "Read the contents of designated file. This function returns contents as text."
    path: str = Field(..., description="relative path of target file to read.")
    
    def Run(args: dict) -> dict:
        with open(args["path"]) as f:
            return {
                "path": args["path"],
                "content": f.read()
            }

class FileWriter(Tool):
    "write given content to designated file. This function overwrites the file."
    path: str = Field(..., description="relative path of target file to write.")
    content: str = Field(..., description="content to write.")

    def Run(args):
        dir = os.path.dirname(args["path"])
        if dir != "":
            os.makedirs(dir, exist_ok=True)
        with open(args["path"], mode="w") as f:
            f.write(args["content"])
        return {
            "path": args["path"],
            "success": True 
        }

class Task(BaseModel):
    name: str
    description: str
    done_flg: bool

class PlanMaker(Tool):
    tasklist: list[Task]
    path: str = Field(..., description="relative path of a file that you want to write a plan.")
    def __init__(self, tasklist:list[Task], path: str =""):
        super().__init__(tasklist=tasklist, path=path)
        self.tasklist = tasklist
        self.path = path

    def Run(args: dict) -> dict:
        dir = os.path.dirname(args["path"])
        if dir != "":
            os.makedirs(dir, exist_ok=True)
        with open(args["path"], mode="w") as f:
            f.write(json.dumps(args["tasklist"]))
        return {
            "path": args["path"],
            "success": True,
        }