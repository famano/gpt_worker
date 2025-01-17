import pytest
from gpt_worker.agents import Planner, Worker
from gpt_worker.dataholder import DataHolder
from gpt_worker.tools import FileReader, FileWriter, PlanMaker, ScriptExecutor, StateUpdater

def test_planner_initialization():
    dataholder = DataHolder(tasklist=[], state_summary="", workspace_dir=".")
    planner = Planner(dataholder=dataholder)
    
    # デフォルトのツールが正しく設定されているか確認
    assert FileReader in planner.tools
    assert PlanMaker in planner.tools
    assert StateUpdater in planner.tools
    
    # カスタムツールでの初期化
    custom_tools = [FileReader, FileWriter]
    custom_planner = Planner(dataholder=dataholder, tools=custom_tools)
    assert custom_planner.tools == custom_tools

def test_worker_initialization():
    dataholder = DataHolder(tasklist=[], state_summary="", workspace_dir=".")
    worker = Worker(dataholder=dataholder)
    
    # デフォルトのツールが正しく設定されているか確認
    assert FileReader in worker.tools
    assert FileWriter in worker.tools
    assert ScriptExecutor in worker.tools
    assert PlanMaker in worker.tools
    
    # カスタムツールでの初期化
    custom_tools = [FileReader, FileWriter]
    custom_worker = Worker(dataholder=dataholder, tools=custom_tools)
    assert custom_worker.tools == custom_tools

def test_worker_max_iterations():
    dataholder = DataHolder(
        tasklist=[
            {
                "name": "永続タスク",
                "description": "終わらないタスク。nameのみを変更し、done_flgは常にFalseに保つこと。",
                "next_step": "次のステップ",
                "done_flg": False,
                "task_id": 0
            }
        ],
        state_summary="テスト状態",
        workspace_dir="."
    )
    
    worker = Worker(dataholder=dataholder)
    messages = worker.run(max_iterations=2)
    
    # 最大イテレーション到達時の警告メッセージを確認
    warning_messages = [
        msg for msg in messages 
        if msg.get("role") == "assistant" and "Warning: Reached maximum number of iterations" in msg.get("content", "")
    ]
    assert len(warning_messages) > 0

def test_worker_no_progress_detection():
    dataholder = DataHolder(
        tasklist=[
            {
                "name": "変化しないタスク",
                "description": "状態が変化しないタスク。一切変更を加えず、なにもしないこと。",
                "next_step": "なし",
                "done_flg": False,
                "task_id": 0
            }
        ],
        state_summary="テスト状態",
        workspace_dir="."
    )
    
    worker = Worker(dataholder=dataholder)
    messages = worker.run()
    
    # 進捗なしの警告メッセージを確認
    warning_messages = [
        msg for msg in messages 
        if msg.get("role") == "assistant" and "Warning: No progress detected in tasks" in msg.get("content", "")
    ]
    assert len(warning_messages) > 0
