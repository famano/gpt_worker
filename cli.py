"""
GPT Workerのコマンドラインインターフェース
"""
import os
import sys
import click
from typing import Optional

from constants import DEFAULT_MODEL, DEFAULT_WORKSPACE_DIR
from agents import DataHolder, Orchestrator

class CLIContext:
    def __init__(self):
        self.verbose = False

pass_context = click.make_pass_decorator(CLIContext, ensure=True)

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
    ctx.obj = CLIContext()
    ctx.obj.verbose = verbose

@cli.command()
@click.argument('order', required=False)
@click.option('--model', '-m', default=DEFAULT_MODEL, help='使用するLLMモデル')
@click.option('--directory', '-d', default=DEFAULT_WORKSPACE_DIR, help='作業ディレクトリ')
@pass_context
def run(ctx, order: Optional[str], model: str, directory: str):
    """タスクを実行する"""
    try:
        setup_workspace(directory)
        
        # 既存のmain.pyの処理を移植
        dataholder = DataHolder(
            tasklist=[],  # TODO: タスクリストの読み込み処理を移植
            state_summary="",  # TODO: 状態サマリーの読み込み処理を移植
            workspace_dir=directory
        )
        orchestrator = Orchestrator(dataholder=dataholder)
        
        if ctx.obj.verbose:
            click.echo(f"モデル: {model}")
            click.echo(f"ディレクトリ: {directory}")
        
        messages = orchestrator.run(order=order if order else "", model=model)
        for message in messages:
            if ctx.obj.verbose:
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
def init(directory: str):
    """新しいワークスペースを初期化する"""
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
        
        # TODO: .gpt_workerディレクトリとその中の必要なファイルを作成
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
        # TODO: タスクリストの読み込みと表示を実装
        click.echo("タスクリスト表示機能は実装中です")
        
    except Exception as e:
        click.echo(f"エラー: タスクリストの表示に失敗しました: {str(e)}", err=True)
        sys.exit(1)

@cli.command()
@click.option('--directory', '-d', default=DEFAULT_WORKSPACE_DIR, help='作業ディレクトリ')
def status(directory: str):
    """現在の状態サマリーを表示する"""
    try:
        setup_workspace(directory)
        # TODO: 状態サマリーの読み込みと表示を実装
        click.echo("状態サマリー表示機能は実装中です")
        
    except Exception as e:
        click.echo(f"エラー: 状態サマリーの表示に失敗しました: {str(e)}", err=True)
        sys.exit(1)

if __name__ == '__main__':
    cli()
