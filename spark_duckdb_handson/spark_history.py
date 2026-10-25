"""Spark History Server 用のイベントログ設定を共通化する。"""

# 環境変数とホームディレクトリを扱うために使う
import os

# OS に依存しないファイルパスを組み立てるために使う
from pathlib import Path


# 環境変数が指定されない場合に、WSL 側へイベントログを保存する場所
DEFAULT_EVENT_LOG_DIRECTORY = Path.home() / "workspace" / "spark_history_events"


def get_event_log_directory() -> Path:
    """Spark のイベントログを保存する絶対パスを返す。"""

    # 必要なら環境変数で保存先を変更できる。通常は既定値をそのまま使う
    configured_directory = os.environ.get("SPARK_EVENT_LOG_DIR")
    if configured_directory:
        return Path(configured_directory).expanduser().resolve()

    return DEFAULT_EVENT_LOG_DIRECTORY.resolve()


def configure_event_logging(builder):
    """SparkSession の Builder に、終了後も確認できるイベントログ設定を加える。"""

    event_log_directory = get_event_log_directory()

    # Spark を起動する前に保存先を作成する。WSL 側のホームディレクトリを使う
    event_log_directory.mkdir(parents=True, exist_ok=True)

    # as_uri() により file:///home/... 形式となり、Spark が確実に解釈できる
    return (
        builder
        .config("spark.eventLog.enabled", "true")
        .config("spark.eventLog.dir", event_log_directory.as_uri())
    )
