import os
import pytest
from tools import FileReader, FileWriter, StateUpdater, PlanMaker, ScriptExecutor, Task
from dataholder import DataHolder

def test_file_reader_success(tmp_path):
    # テスト用のファイルを作成
    test_file = tmp_path / "test.txt"
    test_content = "テスト内容"
    test_file.write_text(test_content)
    
    # FileReaderのテスト
    result = FileReader.run({"path": str(test_file)})
    assert result["path"] == str(test_file)
    assert result["content"] == test_content

def test_file_reader_failure():
    # 存在しないファイルを読もうとする
    result = FileReader.run({"path": "non_existent.txt"})
    assert result["success"] == False
    assert "No such file or directory" in result["content"]

def test_file_writer_success(tmp_path):
    # FileWriterのテスト
    test_file = tmp_path / "test_write.txt"
    test_content = "書き込みテスト"
    
    result = FileWriter.run({
        "path": str(test_file),
        "content": test_content
    })
    
    assert result["success"] == True
    assert result["path"] == str(test_file)
    assert test_file.read_text() == test_content

def test_file_writer_failure(tmp_path):
    # 書き込み権限のないディレクトリにファイルを作成しようとする
    result = FileWriter.run({
        "path": "/root/test.txt",
        "content": "test"
    })
    assert result["success"] == False

def test_state_updater(tmp_path):
    # StateUpdaterのテスト
    dataholder = DataHolder(
        tasklist=[],
        state_summery="",
        workspace_dir=str(tmp_path)
    )
    test_state = "現在の状態"
    
    result = StateUpdater.run({
        "dataholder": dataholder,
        "state_summery": test_state
    })
    
    assert result["success"] == True
    assert dataholder.state_summery == test_state
    
    # ファイルが作成されたことを確認
    state_file = tmp_path / ".gpt_worker/state_summery.md"
    assert state_file.exists()
    assert state_file.read_text() == test_state

def test_plan_maker(tmp_path):
    # PlanMakerのテスト
    dataholder = DataHolder(
        tasklist=[],
        state_summery="",
        workspace_dir=str(tmp_path)
    )
    
    test_task = {
        "name": "テストタスク",
        "description": "テスト用のタスク",
        "next_step": "次のステップ",
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
    # ユーザー入力をシミュレート
    monkeypatch.setattr('builtins.input', lambda: 'y')
    
    result = ScriptExecutor.run({"script": "echo 'テスト'"})
    assert result["user_permitted"] == True
    assert "テスト" in result["result"]

def test_script_executor_denied(monkeypatch):
    # ユーザー入力をシミュレート（実行を拒否）
    monkeypatch.setattr('builtins.input', lambda: 'n')
    
    result = ScriptExecutor.run({"script": "echo 'テスト'"})
    assert result["user_permitted"] == False
    assert result["result"] == ""
