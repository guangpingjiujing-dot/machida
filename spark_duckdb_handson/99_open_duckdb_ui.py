"""ローカルの DuckDB UI を起動し、野球集計テーブルをブラウザで確認する。"""

# OS に依存しないファイルパスを組み立てるために使う
from pathlib import Path

# Ctrl+C を受けたときも UI サーバーを停止できるように使う
import sys

# キーボード入力に依存せず、UI サーバーを待機させるために使う
from threading import Event

# DuckDB のデータベース接続と SQL 実行に使う
import duckdb


# 05 番で作成した、Ubuntu 側のローカル DuckDB ファイルを指定する
DATABASE_PATH = (
    Path.home()
    / "workspace"
    / "spark_duckdb_output"
    / "baseball"
    / "baseball.duckdb"
)

# DuckDB UI が待ち受けるローカルポートを指定する
UI_PORT = 4213


def main() -> None:
    """ローカル DB に接続して DuckDB UI サーバーを開始する。"""

    # DB がない状態で空の DB を作らないように、先に存在だけを確認する
    if not DATABASE_PATH.is_file():
        print(f"DuckDB ファイルが見つかりません: {DATABASE_PATH}")
        print("先に `python 05_duckdb_query_baseball_summary.py` を実行してください。")
        sys.exit(1)

    # 05 番で作ったローカル DB を開く。MotherDuck には接続しない
    connection = duckdb.connect(database=str(DATABASE_PATH))

    try:
        # UI で見る対象テーブルがあることを、起動前に確認する
        table_exists = connection.execute(
            """
            SELECT EXISTS (
                SELECT 1
                FROM information_schema.tables
                WHERE table_schema = 'main'
                  AND table_name = 'baseball_year_summary'
            )
            """
        ).fetchone()[0]

        if not table_exists:
            print("baseball_year_summary テーブルが見つかりません。")
            print("先に `python 05_duckdb_query_baseball_summary.py` を実行してください。")
            sys.exit(1)

        # 初回だけ公式の ui 拡張機能をダウンロードしてインストールする
        # 2 回目以降はインストール済みの拡張機能をそのまま利用する
        connection.execute("INSTALL ui")
        connection.execute("LOAD ui")

        # ブラウザを自動起動せず、WSL からアクセスできるローカル URL で待ち受ける
        connection.execute(f"SET ui_local_port = {UI_PORT}")
        connection.execute("CALL start_ui_server()")

        print("DuckDB UI をローカルで起動しました。")
        print(f"URL: http://localhost:{UI_PORT}")
        print(f"データベース: {DATABASE_PATH}")
        print("テーブル: baseball_year_summary")
        print("このターミナルは開いたままにしてください。停止するには Ctrl+C を押します。")
        print("MotherDuck へのサインインやクラウドへのデータ送信は行いません。")

        # DuckDB 接続を維持する間だけ UI サーバーも利用できるようにする
        # 入力待ちにしないため、VS Code のターミナルでもバックグラウンドでも動作する
        Event().wait()
    except (KeyboardInterrupt, EOFError):
        # Ctrl+C または入力ストリーム終了時は、ローカル UI サーバーを停止する
        print("\nDuckDB UI を停止します。")
        connection.execute("CALL stop_ui_server()")
    finally:
        # DB 接続を閉じ、ローカルの DuckDB ファイルを安全に閉じる
        connection.close()


if __name__ == "__main__":
    # このファイルを直接実行したときだけ UI を起動する
    main()
