from tools import ScriptExecutor, StateUpdater, PlanMaker, Task
from dataholder import DataHolder

print("Script Executor: ls")
result = ScriptExecutor.run({"script":"ls"})
print(result)

print("State Updater:")
result = StateUpdater.run({
    "dataholder": DataHolder(tasklist=[], state_summery="", workspace_dir="."),
    "state_summery": "test"
})
print(result)

print("Plan Maker:")
result = PlanMaker.run({
    "dataholder": DataHolder(tasklist=[], state_summery="", workspace_dir="."),
    "tasklist": [{
        "name":"testtask",
        "description":"testdescription",
        "next_step":"test_nextstep",
        "done_flg":False,
    }]
})
print(result)