from abc import abstractmethod
import os
import json
import logging
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
import subprocess
from gpt_worker.constants import STATE_SUMMARY_FILE, PLAN_FILE, ALLOWED_COMMANDS, COMMAND_TIMEOUT

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Log format configuration
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(formatter)

# File handler
file_handler = logging.FileHandler('tools.log')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

# Add handlers
logger.addHandler(console_handler)
logger.addHandler(file_handler)

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
    Base class for all tools.
    All tools must inherit from this class and implement the run() method.
    """
    
    @abstractmethod
    def run(args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the tool.

        Args:
            args: Dictionary containing the required arguments for tool execution

        Returns:
            Dictionary containing execution results, must include 'success' key indicating success/failure

        Raises:
            ToolError: When an error occurs during tool execution
        """
        pass

    @staticmethod
    def validate_path(path: str) -> None:
        """
        Validate file path.

        Args:
            path: File path to validate

        Raises:
            ValidationError: When path is invalid
        """
        if not path or not isinstance(path, str):
            raise ValidationError("Invalid file path")
        

class FileReader(Tool):
    """
    Tool for reading contents of a specified file.
    """
    path: str = Field(..., description="relative path of target file to read.")
    
    def run(args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Read and return the contents of a file.

        Args:
            args: Dictionary containing required parameters
                - path: Path of the file to read

        Returns:
            Dictionary containing execution results
            - success: Whether execution was successful
            - path: Path of the read file (only on success)
            - content: File contents or error message on failure

        Raises:
            FileOperationError: When file operation fails
            ValidationError: When path validation fails
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
    Tool for writing content to a specified file.
    Existing files will be overwritten.
    """
    path: str = Field(..., description="relative path of target file to write. note that path should be in working directory.")
    content: str = Field(..., description="content to write.")

    def run(args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Write content to a file.

        Args:
            args: Dictionary containing required parameters
                - path: Path of the file to write to
                - content: Content to write

        Returns:
            Dictionary containing execution results
            - success: Whether execution was successful
            - path: Path of the written file (only on success)
            - content: Error message on failure

        Raises:
            FileOperationError: When file operation fails
            ValidationError: When path validation fails
        """
        try:
            Tool.validate_path(args["path"])
            dataholder = args["dataholder"]

            if not args["path"].startswith(dataholder.workspace_dir):
                path = os.path.join(dataholder.workspace_dir, args["path"])
            else:
                path = args["path"]

            dir = os.path.dirname(path)
            if dir:
                os.makedirs(dir, exist_ok=True)
                
            with open(path, mode="w", encoding="utf-8") as f:
                f.write(args["content"])
                
            logger.debug(f"Successfully wrote to file: {path}")
            return {
                "success": True, 
                "path": path,
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
    Tool for updating the current state summary.
    Updates are saved to a file and reflected in the DataHolder.
    """
    state_summary: str = Field(..., description="summary of current situation.")

    def run(args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update the state summary.

        Args:
            args: Dictionary containing required parameters
                - dataholder: DataHolder instance
                - state_summary: New state summary

        Returns:
            Dictionary containing execution results
            - success: Whether execution was successful
            - content: Error message on failure

        Raises:
            FileOperationError: When file operation fails
        """
        try:
            dataholder = args["dataholder"]
            if not args.get("state_summary"):
                raise ValidationError("state_summary is required")
                
            dataholder.state_summary = args["state_summary"]
            
            summery_file = os.path.join(dataholder.workspace_dir, STATE_SUMMARY_FILE)
            os.makedirs(os.path.dirname(summery_file), exist_ok=True)
            with open(summery_file, mode="w", encoding="utf-8") as f:
                f.write(args["state_summary"])
                
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
    Model representing a task.
    Task IDs are automatically assigned when created.
    """
    name: str = Field(..., description="Name of the task")
    description: str = Field(..., description="Detailed description of the task")
    next_step: str = Field(..., description="Concrete and detailed explanation of what to do next")
    done_flg: bool = Field(..., description="Flag indicating if the task is completed")

class PlanMaker(Tool):
    """
    Tool for creating and saving a task list.
    Existing plans will be overwritten.
    """
    tasklist: List[Task] = Field(..., description="List of tasks to create or update")

    def run(args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create and save a task list to a file.

        Args:
            args: Dictionary containing required parameters
                - dataholder: DataHolder instance
                - tasklist: List of tasks

        Returns:
            Dictionary containing execution results
            - success: Whether execution was successful
            - content: Error message on failure

        Raises:
            ValidationError: When task list validation fails
            FileOperationError: When file operation fails
        """
        try:
            dataholder = args["dataholder"]
            tasklist = args["tasklist"]
            
            if not isinstance(tasklist, list):
                raise ValidationError("tasklist must be a list")
            
            # Assign task IDs
            for i, task in enumerate(tasklist):
                task["task_id"] = i
            
            # Save to file
            plan_file = os.path.join(dataholder.workspace_dir, PLAN_FILE)
            os.makedirs(os.path.dirname(plan_file), exist_ok=True)
            with open(plan_file, mode="w", encoding="utf-8") as f:
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
    Tool for updating an existing task list.
    Only tasks with matching task IDs will be updated, other tasks remain unchanged.
    """
    tasklist: List[Task] = Field(..., description="Part of the task list to update. Only tasks with matching task_ids will be updated.")

    def run(args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update the task list.

        Args:
            args: Dictionary containing required parameters
                - dataholder: DataHolder instance
                - tasklist: List of tasks to update

        Returns:
            Dictionary containing execution results
            - success: Whether execution was successful
            - content: Updated task list or error message

        Raises:
            ValidationError: When task list validation fails
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
    Tool for safely executing shell scripts. Note that this is not a shell executor (it is actually subprocess),
    so shell-specific commands like 'cd' cannot be used.
    Current directory is already set to the workspace directory.
    The following security restrictions apply:
    1. Execution time limit through timeout
    2. Protection against shell injection
    3. Commands not in the pre-approved list require user approval
    """
    script: str = Field(..., description="Linux shell script to execute")
    
    @staticmethod
    def is_command_allowed(script: str) -> bool:
        """
        Check if the command is in the allowed list.

        Args:
            script: Script to check

        Returns:
            True if command is allowed, False otherwise
        """
        if not script:
            return False
        first_word = script.split()[0]
        return first_word in ALLOWED_COMMANDS
    
    def run(args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the script.

        Args:
            args: Dictionary containing required parameters
                - script: Script to execute

        Returns:
            Dictionary containing execution results
            - success: Whether execution was successful
            - content: Execution output or error message

        Raises:
            ValidationError: When script validation fails
            ToolError: When script execution fails
        """
        try:
            if not args.get("script"):
                raise ValidationError("Script is required")
            
            script = args["script"].strip()
            logger.info(f"Validating script: {script}")
            
            # Validate command and check if approval is required
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
            
            # Execute subprocess (with shell features disabled)
            process = subprocess.Popen(
                script.split(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=False,
                text=True,
                cwd=args.get("dataholder").workspace_dir
            )
            
            # Execute with timeout
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
