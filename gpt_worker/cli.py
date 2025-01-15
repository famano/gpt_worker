"""
GPT Workerのコマンドラインインターフェース
"""
import os
import sys
import json
import click
from typing import Optional

from gpt_worker.constants import DEFAULT_MODEL, DEFAULT_WORKSPACE_DIR, GPT_WORKER_DIR, PLAN_FILE, STATE_SUMMARY_FILE
from gpt_worker.agents import DataHolder, Orchestrator

def setup_workspace(directory: str) -> None:
    """ワークスペースディレクトリの設定と検証"""
    if not os.path.exists(directory):
        click.echo(f"エラー: ディレクトリ '{directory}' が存在しません", err=True)
        sys.exit(1)

@click.group()
@click.option('--verbose', is_flag=True, help='詳細な出力を有効にする')
@click.pass_context
def cli(ctx, verbose):
    """GPT Worker - AIによるタスク自動化ツール"""
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose

@cli.command()
@click.argument('order', required=False)
@click.option('--model', '-m', default=DEFAULT_MODEL, help='使用するLLMモデル')
@click.option('--directory', '-d', default=DEFAULT_WORKSPACE_DIR, help='作業ディレクトリ')
@click.pass_context
def run(ctx, order: Optional[str], model: str, directory: str):
    """タスクを実行する"""
    try:
        setup_workspace(directory)
        
        # タスクリストと状態サマリーの読み込み
        tasklist = []
        state_summary = ""

        # タスクリストの読み込み
        plan_dir = os.path.join(directory, PLAN_FILE)
        if os.path.exists(plan_dir):
            with open(plan_dir, encoding="utf-8") as f:
                tasklist = json.loads(f.read())
            if ctx.obj["verbose"]:
                click.echo(f"タスクリストを読み込みました: {plan_dir}")

        # 状態サマリーの読み込み
        summary_dir = os.path.join(directory, STATE_SUMMARY_FILE)
        if os.path.exists(summary_dir):
            with open(summary_dir, encoding="utf-8") as f:
                state_summary = f.read()
            if ctx.obj["verbose"]:
                click.echo(f"状態サマリーを読み込みました: {summary_dir}")

        dataholder = DataHolder(
            tasklist=tasklist,
            state_summary=state_summary,
            workspace_dir=directory
        )
        orchestrator = Orchestrator(dataholder=dataholder)
        
        if ctx.obj["verbose"]:
            click.echo(f"モデル: {model}")
            click.echo(f"ディレクトリ: {directory}")
        
        messages = orchestrator.run(order=order if order else "", model=model)
        for message in messages:
            if ctx.obj["verbose"]:
                click.echo(f"role: {message['role']}")
            
            if "content" in message:
                click.echo("content:")
                click.echo(message["content"])
            
            if "tool_calls" in message:
                click.echo("tool_calls:")
                click.echo(message["tool_calls"])
                
    except Exception as e:
        click.echo(f"エラー: {str(e)}", err=True)
        sys.exit(1)

@cli.command()
@click.argument('directory', required=False, default=DEFAULT_WORKSPACE_DIR)
@click.pass_context
def init(ctx, directory: str):
    """新しいワークスペースを初期化する"""
    try:
        # ベースディレクトリの作成
        if not os.path.exists(directory):
            os.makedirs(directory)
            if ctx.obj["verbose"]:
                click.echo(f"ディレクトリを作成しました: {directory}")
        
        # .gpt_workerディレクトリの作成
        gpt_worker_dir = os.path.join(directory, GPT_WORKER_DIR)
        if not os.path.exists(gpt_worker_dir):
            os.makedirs(gpt_worker_dir)
            if ctx.obj["verbose"]:
                click.echo(f"GPT Workerディレクトリを作成しました: {gpt_worker_dir}")
        
        # 初期ファイルの作成
        plan_path = os.path.join(directory, PLAN_FILE)
        if not os.path.exists(plan_path):
            with open(plan_path, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
            if ctx.obj["verbose"]:
                click.echo(f"タスクリストファイルを作成しました: {plan_path}")
        
        summary_path = os.path.join(directory, STATE_SUMMARY_FILE)
        if not os.path.exists(summary_path):
            with open(summary_path, 'w', encoding='utf-8') as f:
                f.write("")
            if ctx.obj["verbose"]:
                click.echo(f"状態サマリーファイルを作成しました: {summary_path}")
        
        click.echo(f"ワークスペース '{directory}' を初期化しました")
        
    except Exception as e:
        click.echo(f"エラー: ワークスペースの初期化に失敗しました: {str(e)}", err=True)
        sys.exit(1)

@cli.command()
@click.option('--directory', '-d', default=DEFAULT_WORKSPACE_DIR, help='作業ディレクトリ')
def list(directory: str):
    """現在のタスクリストを表示する"""
    try:
        setup_workspace(directory)
        
        plan_path = os.path.join(directory, PLAN_FILE)
        if not os.path.exists(plan_path):
            click.echo("タスクリストが存在しません")
            return

        with open(plan_path, encoding="utf-8") as f:
            tasks = json.loads(f.read())
            
        if not tasks:
            click.echo("タスクリストは空です")
            return
            
        for i, task in enumerate(tasks, 1):
            click.echo(f"\nタスク {i}:")
            click.echo(json.dumps(task, ensure_ascii=False, indent=2))
        
    except Exception as e:
        click.echo(f"エラー: タスクリストの表示に失敗しました: {str(e)}", err=True)
        sys.exit(1)

@cli.command()
@click.option('--directory', '-d', default=DEFAULT_WORKSPACE_DIR, help='作業ディレクトリ')
def status(directory: str):
    """現在の状態サマリーを表示する"""
    try:
        setup_workspace(directory)
        
        summary_path = os.path.join(directory, STATE_SUMMARY_FILE)
        if not os.path.exists(summary_path):
            click.echo("状態サマリーが存在しません")
            return

        with open(summary_path, encoding="utf-8") as f:
            summary = f.read()
            
        if not summary:
            click.echo("状態サマリーは空です")
            return
            
        click.echo("\n=== 状態サマリー ===\n")
        click.echo(summary)
        
    except Exception as e:
        click.echo(f"エラー: 状態サマリーの表示に失敗しました: {str(e)}", err=True)
        sys.exit(1)

if __name__ == '__main__':
    cli(obj={})
