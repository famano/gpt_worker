from abc import abstractmethod
import os
import json
import logging
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
import subprocess
from constants import STATE_SUMMARY_FILE, PLAN_FILE, ALLOWED_COMMANDS, COMMAND_TIMEOUT

logger = logging.getLogger(__name__)

class ToolError(Exception):
    """Base exception class for Tool errors"""
    pass

class FileOperationError(ToolError):
    """Raised when file operations fail"""
    pass

class ValidationError(ToolError):
    """Raised when input validation fails"""
    pass

class Tool(BaseModel):
    """
    ツールの基底クラス。
    全てのツールはこのクラスを継承し、run()メソッドを実装する必要があります。
    """
    
    @abstractmethod
    def run(args: Dict[str, Any]) -> Dict[str, Any]:
        """
        ツールを実行します。

        Args:
            args: ツールの実行に必要な引数を含む辞書

        Returns:
            実行結果を含む辞書。必ず'success'キーを含み、成功/失敗を示す

        Raises:
            ToolError: ツールの実行中にエラーが発生した場合
        """
        pass

    @staticmethod
    def validate_path(path: str) -> None:
        """
        ファイルパスのバリデーションを行います。

        Args:
            path: 検証するファイルパス

        Raises:
            ValidationError: パスが不正な場合
        """
        if not path or not isinstance(path, str):
            raise ValidationError("Invalid file path")
        

class FileReader(Tool):
    """
    指定されたファイルの内容を読み取るツール。

    Attributes:
        path: 読み取り対象のファイルの相対パス
    """
    path: str = Field(..., description="relative path of target file to read.")
    
    def run(args: Dict[str, Any]) -> Dict[str, Any]:
        """
        ファイルを読み取り、その内容を返します。

        Args:
            args: 必要なパラメータを含む辞書
                - path: 読み取るファイルのパス

        Returns:
            実行結果を含む辞書
            - success: 実行が成功したかどうか
            - path: 読み取ったファイルのパス（成功時のみ）
            - content: ファイルの内容または失敗時のエラーメッセージ

        Raises:
            FileOperationError: ファイル操作に失敗した場合
            ValidationError: パスの検証に失敗した場合
        """
        try:
            Tool.validate_path(args["path"])
            
            if not os.path.exists(args["path"]):
                raise FileOperationError(f"File not found: {args['path']}")
                
            with open(args["path"], encoding="utf-8") as f:
                content = f.read()
                logger.debug(f"Successfully read file: {args['path']}")
                return {
                    "success": True,
                    "path": args["path"],
                    "content": content
                }
        except (ValidationError, FileOperationError) as e:
            logger.error(f"Error reading file: {e}")
            return {
                "success": False,
                "content": str(e)
            }
        except Exception as e:
            logger.error(f"Unexpected error reading file: {e}")
            return {
                "success": False,
                "content": f"Unexpected error: {str(e)}"
            }

class FileWriter(Tool):
    """
    指定されたファイルに内容を書き込むツール。
    既存のファイルは上書きされます。

    Attributes:
        path: 書き込み先のファイルの相対パス
        content: 書き込む内容
    """
    path: str = Field(..., description="relative path of target file to write.")
    content: str = Field(..., description="content to write.")

    def run(args: Dict[str, Any]) -> Dict[str, Any]:
        """
        ファイルに内容を書き込みます。

        Args:
            args: 必要なパラメータを含む辞書
                - path: 書き込み先のファイルパス
                - content: 書き込む内容

        Returns:
            実行結果を含む辞書
            - success: 実行が成功したかどうか
            - path: 書き込んだファイルのパス（成功時のみ）
            - content: 失敗時のエラーメッセージ

        Raises:
            FileOperationError: ファイル操作に失敗した場合
            ValidationError: パスの検証に失敗した場合
        """
        try:
            Tool.validate_path(args["path"])
            
            dir = os.path.dirname(args["path"])
            if dir:
                os.makedirs(dir, exist_ok=True)
                
            with open(args["path"], mode="w", encoding="utf-8") as f:
                f.write(args["content"])
                
            logger.debug(f"Successfully wrote to file: {args['path']}")
            return {
                "success": True, 
                "path": args["path"],
            }
        except (ValidationError, FileOperationError) as e:
            logger.error(f"Error writing file: {e}")
            return {
                "success": False,
                "content": str(e)
            }
        except Exception as e:
            logger.error(f"Unexpected error writing file: {e}")
            return {
                "success": False,
                "content": f"Unexpected error: {str(e)}"
            }

class StateUpdater(Tool):
    """
    現在の状態サマリーを更新するツール。
    更新内容はファイルに保存され、DataHolderにも反映されます。

    Attributes:
        state_summery: 新しい状態サマリー
    """
    state_summery: str = Field(..., description="summery of current situation.")

    def run(args: Dict[str, Any]) -> Dict[str, Any]:
        """
        状態サマリーを更新します。

        Args:
            args: 必要なパラメータを含む辞書
                - dataholder: DataHolderインスタンス
                - state_summery: 新しい状態サマリー

        Returns:
            実行結果を含む辞書
            - success: 実行が成功したかどうか
            - content: 失敗時のエラーメッセージ

        Raises:
            FileOperationError: ファイル操作に失敗した場合
        """
        try:
            dataholder = args["dataholder"]
            if not args.get("state_summery"):
                raise ValidationError("state_summery is required")
                
            dataholder.state_summery = args["state_summery"]
            
            os.makedirs(os.path.dirname(STATE_SUMMARY_FILE), exist_ok=True)
            with open(STATE_SUMMARY_FILE, mode="w", encoding="utf-8") as f:
                f.write(args["state_summery"])
                
            logger.debug("Successfully updated state summary")
            return {
                "success": True 
            }
        except ValidationError as e:
            logger.error(f"Validation error: {e}")
            return {
                "success": False,
                "content": str(e)
            }
        except Exception as e:
            logger.error(f"Error updating state: {e}")
            return {
                "success": False,
                "content": f"Error updating state: {str(e)}"
            }

class Task(BaseModel):
    """
    タスクを表すモデル。
    タスクIDは生成時に自動的に付与されます。

    Attributes:
        name: タスクの名前
        description: タスクの説明
        next_step: 次に実行すべき具体的な手順
        done_flg: タスクの完了フラグ
    """
    name: str = Field(..., description="Name of the task")
    description: str = Field(..., description="Detailed description of the task")
    next_step: str = Field(..., description="Concrete and detailed explanation of what to do next")
    done_flg: bool = Field(False, description="Flag indicating if the task is completed")

class PlanMaker(Tool):
    """
    タスクリストを作成・保存するツール。
    既存のプランがある場合は上書きされます。

    Attributes:
        tasklist: タスクのリスト
    """
    tasklist: List[Task] = Field(..., description="List of tasks to create or update")

    def run(args: Dict[str, Any]) -> Dict[str, Any]:
        """
        タスクリストを作成し、ファイルに保存します。

        Args:
            args: 必要なパラメータを含む辞書
                - dataholder: DataHolderインスタンス
                - tasklist: タスクのリスト

        Returns:
            実行結果を含む辞書
            - success: 実行が成功したかどうか
            - content: 失敗時のエラーメッセージ

        Raises:
            ValidationError: タスクリストの検証に失敗した場合
            FileOperationError: ファイル操作に失敗した場合
        """
        try:
            dataholder = args["dataholder"]
            tasklist = args["tasklist"]
            
            if not isinstance(tasklist, list):
                raise ValidationError("tasklist must be a list")
            
            # タスクIDの付与
            for i, task in enumerate(tasklist):
                task["task_id"] = i
            
            # ファイルへの保存
            os.makedirs(os.path.dirname(PLAN_FILE), exist_ok=True)
            with open(PLAN_FILE, mode="w", encoding="utf-8") as f:
                f.write(json.dumps(tasklist))
            
            dataholder.tasklist = tasklist
            logger.info(f"Successfully created plan with {len(tasklist)} tasks")
            
            return {
                "success": True,
            }
        except (ValidationError, FileOperationError) as e:
            logger.error(f"Error creating plan: {e}")
            return {
                "success": False,
                "content": str(e)
            }
        except Exception as e:
            logger.error(f"Unexpected error creating plan: {e}")
            return {
                "success": False,
                "content": f"Unexpected error: {str(e)}"
            }

class PlanUpdater(Tool):
    """
    既存のタスクリストを更新するツール。
    同じタスクIDを持つタスクのみが更新され、他のタスクは変更されません。

    Attributes:
        tasklist: 更新するタスクのリスト
    """
    tasklist: List[Task] = Field(..., description="Part of the task list to update. Only tasks with matching task_ids will be updated.")

    def run(args: Dict[str, Any]) -> Dict[str, Any]:
        """
        タスクリストを更新します。

        Args:
            args: 必要なパラメータを含む辞書
                - dataholder: DataHolderインスタンス
                - tasklist: 更新するタスクのリスト

        Returns:
            実行結果を含む辞書
            - success: 実行が成功したかどうか
            - content: 更新後のタスクリストまたはエラーメッセージ

        Raises:
            ValidationError: タスクリストの検証に失敗した場合
        """
        try:
            tasklist = args["tasklist"]
            dataholder = args["dataholder"]
            
            if not isinstance(tasklist, list):
                raise ValidationError("tasklist must be a list")
            
            update_count = 0
            for original_task in dataholder.tasklist:
                update_task = next((task for task in tasklist if task.get("task_id") == original_task.get("task_id")), None)
                if update_task:
                    original_task.update(update_task)
                    update_count += 1
            
            logger.info(f"Successfully updated {update_count} tasks")
            return {
                "success": True,
                "content": str(dataholder.tasklist),
            }
        except ValidationError as e:
            logger.error(f"Validation error: {e}")
            return {
                "success": False,
                "content": str(e)
            }
        except Exception as e:
            logger.error(f"Error updating plan: {e}")
            return {
                "success": False,
                "content": f"Error updating plan: {str(e)}"
            }


class ScriptExecutor(Tool):
    """
    シェルスクリプトを安全に実行するツール。
    以下のセキュリティ制限が適用されます：
    1. 許可されたコマンドのみ実行可能
    2. タイムアウトによる実行時間の制限
    3. シェルインジェクション対策
    4. ユーザーの承認が必要

    Attributes:
        script: 実行するLinuxシェルスクリプト
    """
    script: str = Field(..., description="Linux shell script to execute")
    
    @staticmethod
    def is_command_allowed(script: str) -> bool:
        """
        コマンドが許可リストに含まれているか確認します。

        Args:
            script: 確認するスクリプト

        Returns:
            コマンドが許可されている場合はTrue、それ以外はFalse
        """
        if not script:
            return False
        first_word = script.split()[0]
        return first_word in ALLOWED_COMMANDS
    
    def run(args: Dict[str, Any]) -> Dict[str, Any]:
        """
        スクリプトを実行します。

        Args:
            args: 必要なパラメータを含む辞書
                - script: 実行するスクリプト

        Returns:
            実行結果を含む辞書
            - success: 実行が成功したかどうか
            - content: 実行結果または失敗時のエラーメッセージ

        Raises:
            ValidationError: スクリプトの検証に失敗した場合
            ToolError: スクリプトの実行に失敗した場合
        """
        try:
            if not args.get("script"):
                raise ValidationError("Script is required")
            
            script = args["script"].strip()
            logger.info(f"Validating script: {script}")
            
            # コマンドの検証と承認の要否判断
            requires_approval = not ScriptExecutor.is_command_allowed(script)
            
            if requires_approval:
                print("The agent wants to execute the following non-allowed script that requires approval:")
                print("---")
                print(script)
                print("---")
                print("Enter 'y' to permit execution. Any other input will abort.")
                
                usr_permit = input().strip().lower()
                if usr_permit != "y":
                    logger.info("User aborted script execution")
                    return {
                        "success": False,
                        "content": "User aborted execution"
                    }
            else:
                logger.info(f"Executing allowed command without approval: {script}")
            
            logger.info(f"Executing script: {script}")
            
            # サブプロセスの実行（シェル機能を無効化）
            process = subprocess.Popen(
                script.split(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=False,
                text=True
            )
            
            # タイムアウト付きで実行
            try:
                stdout, stderr = process.communicate(timeout=COMMAND_TIMEOUT)
                
                if process.returncode != 0:
                    logger.error(f"Command failed: {stderr}")
                    return {
                        "success": False,
                        "content": f"Command failed with error: {stderr}"
                    }
                
                logger.info("Command executed successfully")
                return {
                    "success": True,
                    "content": stdout
                }
                
            except subprocess.TimeoutExpired:
                process.kill()
                logger.error(f"Command timed out after {COMMAND_TIMEOUT} seconds")
                return {
                    "success": False,
                    "content": f"Command timed out after {COMMAND_TIMEOUT} seconds"
                }
                
        except ValidationError as e:
            logger.error(f"Validation error: {e}")
            return {
                "success": False,
                "content": str(e)
            }
        except Exception as e:
            logger.error(f"Unexpected error executing command: {e}")
            return {
                "success": False,
                "content": f"Error executing command: {str(e)}"
            }
