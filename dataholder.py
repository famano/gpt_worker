from typing import List, Dict, Optional, Union
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class DataHolderError(Exception):
    """Base exception class for DataHolder errors"""
    pass

class TaskNotFoundError(DataHolderError):
    """Raised when a task is not found"""
    pass

class InvalidTaskError(DataHolderError):
    """Raised when task data is invalid"""
    pass

class DataHolder:
    """
    タスクリストと状態サマリーを管理するクラス。
    
    Attributes:
        tasklist (List[Dict]): タスクのリスト
        state_summery (str): 現在の状態のサマリー
        workspace_dir (str): ワークスペースディレクトリのパス
    """
    
    def __init__(self, tasklist: List[Dict], state_summery: str, workspace_dir: str):
        """
        DataHolderの初期化

        Args:
            tasklist: タスクのリスト。各タスクは辞書形式で、必須キーは'task_id'と'done_flg'
            state_summery: 現在の状態を説明するテキスト
            workspace_dir: ワークスペースディレクトリのパス

        Raises:
            InvalidTaskError: タスクリストの形式が不正な場合
        """
        self._validate_tasklist(tasklist)
        self.tasklist = tasklist
        self.state_summery = state_summery
        self.workspace_dir = workspace_dir
        logger.info(f"DataHolder initialized with {len(tasklist)} tasks")
    
    @staticmethod
    def _validate_tasklist(tasklist: List[Dict]) -> None:
        """タスクリストのバリデーション"""
        if not isinstance(tasklist, list):
            raise InvalidTaskError("Tasklist must be a list")
        
        for task in tasklist:
            if not isinstance(task, dict):
                raise InvalidTaskError("Each task must be a dictionary")
            
            # task_idとdone_flgは必須
            if "task_id" not in task:
                raise InvalidTaskError("Task must have 'task_id'")
            if "done_flg" not in task:
                raise InvalidTaskError("Task must have 'done_flg'")
    
    def find_task(self, condition: Dict) -> List[Dict]:
        """
        条件に一致するタスクを検索

        Args:
            condition: 検索条件を含む辞書。'task_id'または'done_flg'をキーとして使用

        Returns:
            条件に一致するタスクのリスト

        Raises:
            InvalidTaskError: 検索条件が不正な場合
        """
        if not isinstance(condition, dict):
            raise InvalidTaskError("Search condition must be a dictionary")
        
        result = []
        try:
            if "task_id" in condition:
                result += list(filter(lambda task: task["task_id"] == condition["task_id"], self.tasklist))
            if "done_flg" in condition:
                result += list(filter(lambda task: task["done_flg"] == condition["done_flg"], self.tasklist))
            
            logger.debug(f"Found {len(result)} tasks matching condition: {condition}")
            return result
            
        except Exception as e:
            logger.error(f"Error finding tasks: {e}")
            raise DataHolderError(f"Error finding tasks: {e}")
    
    def update_task(self, task_id: int, content: Dict) -> None:
        """
        指定されたタスクを更新

        Args:
            task_id: 更新対象のタスクID
            content: 更新する内容を含む辞書

        Raises:
            TaskNotFoundError: 指定されたIDのタスクが見つからない場合
            InvalidTaskError: 更新内容が不正な場合
        """
        if not isinstance(content, dict):
            raise InvalidTaskError("Update content must be a dictionary")
        
        target_task = None
        for task in self.tasklist:
            if task["task_id"] == task_id:
                target_task = task
                break
        
        if target_task is None:
            logger.error(f"Task not found: {task_id}")
            raise TaskNotFoundError(f"Task not found: {task_id}")
        
        try:
            target_task.update(content)
            logger.info(f"Updated task {task_id}")
        except Exception as e:
            logger.error(f"Error updating task {task_id}: {e}")
            raise DataHolderError(f"Error updating task: {e}")
