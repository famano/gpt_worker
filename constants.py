"""
プロジェクト全体で使用される定数を定義するモジュール
"""
import os
from pathlib import Path

# ディレクトリパス
WORKSPACE_DIR = "." #暫定的、将来的にユーザーから受け取りたい
GPT_WORKER_DIR = os.path.join(WORKSPACE_DIR, ".gpt_worker")

# ファイルパス
PLAN_FILE = os.path.join(GPT_WORKER_DIR, "plan.json")
STATE_SUMMARY_FILE = os.path.join(GPT_WORKER_DIR, "state_summery.md")

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
