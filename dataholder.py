class DataHolder():
    tasklist: list[dict]
    state_summery: str
    workspace_dir: str
    
    def __init__(self, tasklist: list[dict], state_summery: str, workspace_dir: str):
        self.tasklist = tasklist
        self.state_summery = state_summery
        self.workspace_dir = workspace_dir
    
    def find_task(self, condition:dict) -> list[dict]:
        result = []
        if "assign" in condition:
            result += list(filter(lambda task: task["assign"] == condition["assign"], self.tasklist))
        if "done_flg" in condition:
            result += list(filter(lambda task: task["done_flg"] == condition["done_flg"], self.tasklist))

        return result
    
    def update_task(self, task_id: int, content: dict) -> None:
        for task in self.tasklist:
            if task["task_id"] == task_id:
                task.update(content)