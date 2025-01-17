"""
プロジェクト全体で使用される定数を定義するモジュール
"""
import os

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
COMMAND_TIMEOUT = 30  # seconds
