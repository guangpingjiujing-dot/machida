from datetime import datetime, timedelta

from airflow.decorators import dag, task
from airflow.operators.python import get_current_context


@dag(schedule=None, start_date=datetime(2024, 1, 1), catchup=False, tags=["retry"])
def retry_demo():
    """リトライを確認するDAG。3回目の試行で成功する。

    UIのTask Instancesで試行回数とステータスの変化を確認できる。
    """

    @task(
        retries=2,  # 失敗後に最大2回リトライ（合計3回試行）
        retry_delay=timedelta(seconds=10),
    )
    def flaky_task() -> None:
        ctx = get_current_context()
        try_number = ctx["ti"].try_number  # 1始まりで試行ごとにインクリメント
        print(f"試行 {try_number} 回目")
        if try_number < 3:
            raise ValueError(f"失敗（{try_number}回目）- リトライします")
        print("成功！（3回目）")

    flaky_task()


retry_demo()


@dag(schedule=None, start_date=datetime(2024, 1, 1), catchup=False, tags=["timeout"])
def timeout_demo():
    """タイムアウトを確認するDAG。意図的にタイムアウトさせてエラーを発生させる。

    execution_timeout を超えると AirflowTaskTimeout が発生する。
    """

    @task(execution_timeout=timedelta(seconds=5))
    def slow_task() -> None:
        import time
        print("処理開始（10秒かかる処理）...")
        time.sleep(10)  # タイムアウト(5秒)を超えるため例外が発生する
        print("この行は実行されない")

    slow_task()


timeout_demo()
