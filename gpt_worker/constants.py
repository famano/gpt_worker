"""
プロジェクト全体で使用される定数を定義するモジュール
"""
import os
from pathlib import Path

# ディレクトリパス
DEFAULT_WORKSPACE_DIR = "."
GPT_WORKER_DIR = ".gpt_worker"

# ファイルパス
PLAN_FILE = os.path.join(GPT_WORKER_DIR, "plan.json")
STATE_SUMMARY_FILE = os.path.join(GPT_WORKER_DIR, "state_summary.md")

# OpenAI設定
DEFAULT_MODEL = "gpt-4o"
MAX_ITERATIONS = 10

# ScriptExecutor設定
ALLOWED_COMMANDS = [
    "ls", "cat", "echo", "pwd", "mkdir", "cp", "mv",
    "git", "npm", "tree", "grep", "head", "tail",
    "touch", "wc"
]
COMMAND_TIMEOUT = 30  # seconds
