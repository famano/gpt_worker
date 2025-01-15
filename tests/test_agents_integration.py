import pytest
from agents import Worker
from dataholder import DataHolder

class MockDataHolder(DataHolder):
    def __init__(self, tasklist=None, state_summary="", workspace_dir="."):
        super().__init__(tasklist, state_summary, workspace_dir)
    
    def find_task(self, filter_dict):
        tasks = super().find_task(filter_dict)
        if tasks:
            return tasks
        else:
            return []

@pytest.fixture
def mock_dataholder():
    return MockDataHolder(
        tasklist=[
            {"task_id": 1, "name": "Test Task", "description": "A task for testing. do not do anything, just turn done_flg True.", "next_step":"turn done_flg True", "done_flg": False}
        ],
        state_summary="Test state",
        workspace_dir="../gpt_worker_test"
    )

def test_worker_logic(mock_dataholder):
    worker = Worker(dataholder=mock_dataholder)
    messages = worker.run()
    
    # We inspect the messages for confirmation
    assert len(messages) > 0
    
    # Verify that the task's done flag was updated
    assert mock_dataholder.tasklist[0]["done_flg"] is True