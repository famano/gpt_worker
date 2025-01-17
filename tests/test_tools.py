import os
import pytest
from gpt_worker.tools import FileReader, FileWriter, StateUpdater, PlanMaker, ScriptExecutor, Task
from gpt_worker.dataholder import DataHolder

def test_file_reader_success(tmp_path):
    dataholder = DataHolder(
        tasklist=[],
        state_summary="",
        workspace_dir=str(tmp_path)
    )
    
    # テスト用のファイルを作成
    test_file = tmp_path / "test.txt"
    test_content = "テスト内容"
    test_file.write_text(test_content)
    
    # FileReaderのテスト
    result = FileReader.run({"path": str(test_file), "dataholder": dataholder})
    assert result["path"] == str(test_file)
    assert result["content"] == test_content

def test_file_reader_corrects_path(tmp_path):
    dataholder = DataHolder(
        tasklist=[],
        state_summary="",
        workspace_dir=str(tmp_path)
    )
    
    # テスト用のファイルを作成
    test_file = tmp_path / "test.txt"
    test_content = "テスト内容"
    test_file.write_text(test_content)
    
    # FileReaderのテスト
    result = FileReader.run({"path": "test.txt", "dataholder": dataholder})
    assert result["path"] == str(test_file)
    assert result["content"] == test_content

def test_file_reader_failure(tmp_path):
    dataholder = DataHolder(
        tasklist=[],
        state_summary="",
        workspace_dir=str(tmp_path)
    )
    
    # 存在しないファイルを読もうとする
    result = FileReader.run({"path": "non_existent.txt", "dataholder": dataholder})
    assert result["success"] == False
    assert "File not found:" in result["content"]

def test_file_writer_success(tmp_path):
    # FileWriterのテスト
    dataholder = DataHolder(
        tasklist=[],
        state_summary="",
        workspace_dir=str(tmp_path)
    )
    
    test_file = tmp_path / "test_write.txt"
    test_content = "書き込みテスト"
    
    result = FileWriter.run({
        "path": str(test_file),
        "content": test_content,
        "dataholder": dataholder,
    })
    
    assert result["success"] == True
    assert result["path"] == str(test_file)
    assert test_file.read_text() == test_content

def test_file_writer_failure(tmp_path):
    # 書き込み権限のないディレクトリにファイルを作成しようとする
    dataholder = DataHolder(
        tasklist=[],
        state_summary="",
        workspace_dir=str(tmp_path)
    )
    
    result = FileWriter.run({
        "path": "/root/test.txt",
        "content": "test",
        "dataholder": dataholder,
    })
    assert result["success"] == False

def test_state_updater(tmp_path):
    # StateUpdaterのテスト
    dataholder = DataHolder(
        tasklist=[],
        state_summary="",
        workspace_dir=str(tmp_path)
    )
    test_state = "現在の状態"
    
    result = StateUpdater.run({
        "dataholder": dataholder,
        "state_summary": test_state
    })
    
    assert result["success"] == True
    assert dataholder.state_summary == test_state
    
    # ファイルが作成されたことを確認
    state_file = tmp_path / ".gpt_worker/state_summary.md"
    assert state_file.exists()
    assert state_file.read_text() == test_state

def test_plan_maker(tmp_path):
    # PlanMakerのテスト
    dataholder = DataHolder(
        tasklist=[],
        state_summary="",
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

def test_script_executor_without_permission(tmp_path):
    dataholder = DataHolder(
        tasklist=[],
        state_summary="",
        workspace_dir=str(tmp_path)
    )

    result = ScriptExecutor.run({"script": "echo 'テスト'", "ask_user": False, "dataholder": dataholder})
    assert result["success"] == True
    assert "テスト" in result["content"]

def test_script_executor_success(monkeypatch, tmp_path):
    # ユーザー入力をシミュレート
    dataholder = DataHolder(
        tasklist=[],
        state_summary="",
        workspace_dir=str(tmp_path)
    )
    
    monkeypatch.setattr('builtins.input', lambda: 'y')
    
    result = ScriptExecutor.run({"script": "python -h", "ask_user": True, "dataholder": dataholder})
    assert result["success"] == True

def test_script_executor_denied(monkeypatch, tmp_path):
    dataholder = DataHolder(
        tasklist=[],
        state_summary="",
        workspace_dir=str(tmp_path)
    )

    # ユーザー入力をシミュレート（実行を拒否）
    monkeypatch.setattr('builtins.input', lambda: 'n')
    
    result = ScriptExecutor.run({"script": "python nonexestent.py", "ask_user": True, "dataholder": dataholder})
    assert result["success"] == False
    assert "User aborted execution" in result["content"]
