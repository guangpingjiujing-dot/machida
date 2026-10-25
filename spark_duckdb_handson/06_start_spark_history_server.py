"""WSL 上で Spark History Server を起動する。"""

# 子プロセスの環境変数を引き継いで設定するために使う
import os

# 実行コマンドを起動するために使う
import subprocess

# PySpark パッケージ内の Spark 配布物とイベントログのパスを扱うために使う
from pathlib import Path

# インストール済み PySpark の場所を取得するために使う
import pyspark

from spark_history import get_event_log_directory


# History Server の画面を開くポート。Spark の標準値と同じ
HISTORY_SERVER_PORT = 18080


def main() -> None:
    """イベントログを読む History Server をバックグラウンドで起動する。"""

    event_log_directory = get_event_log_directory()
    event_log_directory.mkdir(parents=True, exist_ok=True)

    # pip でインストールした PySpark に同梱される Spark の起動スクリプトを使う
    spark_home = Path(pyspark.__file__).resolve().parent
    start_script = spark_home / "sbin" / "start-history-server.sh"

    if not start_script.is_file():
        raise FileNotFoundError(
            f"History Server の起動スクリプトが見つかりません: {start_script}"
        )

    # Spark の Java プロセスへ、ログの保存先と UI ポートを渡す
    environment = os.environ.copy()
    history_options = environment.get("SPARK_HISTORY_OPTS", "")
    server_options = (
        f"-Dspark.history.fs.logDirectory={event_log_directory.as_uri()} "
        f"-Dspark.history.ui.port={HISTORY_SERVER_PORT}"
    )
    environment["SPARK_HISTORY_OPTS"] = f"{history_options} {server_options}".strip()

    subprocess.run([str(start_script)], check=True, env=environment)

    print("Spark History Server を起動しました。")
    print(f"URL: http://localhost:{HISTORY_SERVER_PORT}")
    print(f"イベントログ: {event_log_directory}")
    print("Spark のスクリプトを実行した後、ブラウザを更新して完了済みアプリを開いてください。")
    print("停止するには `python 07_stop_spark_history_server.py` を実行します。")


if __name__ == "__main__":
    main()
