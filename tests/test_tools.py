import os
import pytest
from tools import FileReader, FileWriter, StateUpdater, PlanMaker, ScriptExecutor, Task
from dataholder import DataHolder

def test_file_reader_success(tmp_path):
    # \\u30c6\\u30b9\\u30c8\\u7528\\u306e\\u30d5\\u30a1\\u30a4\\u30eb\\u3092\\u4f5c\\u6210
    test_file = tmp_path / "test.txt"
    test_content = "\\u30c6\\u30b9\\u30c8\\u5185\\u5bb9"
    test_file.write_text(test_content)
    
    # FileReader\\u306e\\u30c6\\u30b9\\u30c8
    result = FileReader.run({"path": str(test_file)})
    assert result["path"] == str(test_file)
    assert result["content"] == test_content

def test_file_reader_failure():
    # \\u5b58\\u5728\\u3057\\u306a\\u3044\\u30d5\\u30a1\\u30a4\\u30eb\\u3092\\u8aad\\u3082\\u3046\\u3068\\u3059\\u308b
    result = FileReader.run({"path": "non_existent.txt"})
    assert result["success"] == False
    assert "No such file or directory" in result["content"]

def test_file_writer_success(tmp_path):
    # FileWriter\\u306e\\u30c6\\u30b9\\u30c8
    test_file = tmp_path / "test_write.txt"
    test_content = "\\u66f8\\u304d\\u8fbc\\u307f\\u30c6\\u30b9\\u30c8"
    
    result = FileWriter.run({
        "path": str(test_file),
        "content": test_content
    })
    
    assert result["success"] == True
    assert result["path"] == str(test_file)
    assert test_file.read_text() == test_content

def test_file_writer_failure(tmp_path):
    # \\u66f8\\u304d\\u8fbc\\u307f\\u6a29\\u9650\\u306e\\u306a\\u3044\\u30c7\\u30a3\\u30ec\\u30af\\u30c8\\u30ea\\u306b\\u30d5\\u30a1\\u30a4\\u30eb\\u3092\\u4f5c\\u6210\\u3057\\u3088\\u3046\\u3068\\u3059\\u308b
    result = FileWriter.run({
        "path": "/root/test.txt",
        "content": "test"
    })
    assert result["success"] == False

def test_state_updater(tmp_path):
    # StateUpdater\\u306e\\u30c6\\u30b9\\u30c8
    dataholder = DataHolder(
        tasklist=[],
        state_summery="",
        workspace_dir=str(tmp_path)
    )
    test_state = "\\u73fe\\u5728\\u306e\\u72b6\\u614b"
    
    result = StateUpdater.run({
        "dataholder": dataholder,
        "state_summery": test_state
    })
    
    assert result["success"] == True
    assert dataholder.state_summery == test_state
    
    # \\u30d5\\u30a1\\u30a4\\u30eb\\u304c\\u4f5c\\u6210\\u3055\\u308c\\u305f\\u3053\\u3068\\u3092\\u78ba\\u8a8d
    state_file = tmp_path / ".gpt_worker/state_summery.md"
    assert state_file.exists()
    assert state_file.read_text() == test_state

def test_plan_maker(tmp_path):
    # PlanMaker\\u306e\\u30c6\\u30b9\\u30c8
    dataholder = DataHolder(
        tasklist=[],
        state_summery="",
        workspace_dir=str(tmp_path)
    )
    
    test_task = {
        "name": "\\u30c6\\u30b9\\u30c8\\u30bf\\u30b9\\u30af",
        "description": "\\u30c6\\u30b9\\u30c8\\u7528\\u306e\\u30bf\\u30b9\\u30af",
        "next_step": "\\u6b21\\u306e\\u30b9\\u30c6\\u30c3\\u30d7",
        "done_flg": False
    }
    
    result = PlanMaker.run({
        "dataholder": dataholder,
        "tasklist": [test_task]
    })
    
    assert result["success"] == True
    assert len(dataholder.tasklist) == 1
    assert dataholder.tasklist[0]["name"] == test_task["name"]
    assert dataholder.tasklist[0]["task_id"] == 0

def test_script_executor_success(monkeypatch):
    # \\u30e6\\u30fc\\u30b6\\u30fc\\u5165\\u529b\\u3092\\u30b7\\u30df\\u30e5\\u30ec\\u30fc\\u30c8
    monkeypatch.setattr('builtins.input', lambda: 'y')
    
    result = ScriptExecutor.run({"script": "echo '\\u30c6\\u30b9\\u30c8'"})
    assert result["success"] == True
    assert "\\u30c6\\u30b9\\u30c8" in result["content"]

def test_script_executor_denied(monkeypatch):
    # \\u30e6\\u30fc\\u30b6\\u30fc\\u5165\\u529b\\u3092\\u30b7\\u30df\\u30e5\\u30ec\\u30fc\\u30c8\\uff08\\u5b9f\\u884c\\u3092\\u62d2\\u5426\\uff09
    monkeypatch.setattr('builtins.input', lambda: 'n')
    
    result = ScriptExecutor.run({"script": "echo '\\u30c6\\u30b9\\u30c8'"})
    assert result["success"] == False
    assert "user aborted" in result["content"]
