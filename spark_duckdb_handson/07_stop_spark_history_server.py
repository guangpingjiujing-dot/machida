"""WSL 上で起動した Spark History Server を停止する。"""

# 停止コマンドを実行するために使う
import subprocess

# PySpark パッケージ内の Spark 配布物の場所を扱うために使う
from pathlib import Path

# インストール済み PySpark の場所を取得するために使う
import pyspark


def main() -> None:
    """PySpark に同梱された停止スクリプトを実行する。"""

    spark_home = Path(pyspark.__file__).resolve().parent
    stop_script = spark_home / "sbin" / "stop-history-server.sh"

    if not stop_script.is_file():
        raise FileNotFoundError(
            f"History Server の停止スクリプトが見つかりません: {stop_script}"
        )

    subprocess.run([str(stop_script)], check=True)
    print("Spark History Server を停止しました。")


if __name__ == "__main__":
    main()
