from datetime import datetime

from airflow.decorators import dag, task
from airflow.sensors.python import PythonSensor


@dag(schedule=None, start_date=datetime(2024, 1, 1), catchup=False, tags=["sensor"])
def sensors_demo():
    """Sensorを確認するDAG。条件が満たされるまでポーリングし続ける。

    実際の用途例:
    - S3にファイルが届くまで待つ（S3KeySensor）
    - 上流のDAGが完了するまで待つ（ExternalTaskSensor）
    - 特定のURLが200を返すまで待つ（HttpSensor）

    ここでは PythonSensor で「ランダムに条件が成立する」状況を再現する。
    """

    attempt_log: list[int] = []

    def _check_data_ready() -> bool:
        import random
        attempt_log.append(1)
        attempt_count = len(attempt_log)
        # 3回目以降、50%の確率で準備完了とする
        if attempt_count >= 3 and random.random() < 0.5:
            print(f"チェック {attempt_count}回目: 準備完了！")
            return True
        print(f"チェック {attempt_count}回目: まだ未準備...")
        return False

    wait_for_data = PythonSensor(
        task_id="wait_for_data",
        python_callable=_check_data_ready,
        poke_interval=5,   # 5秒ごとにチェック
        timeout=120,       # 120秒でタイムアウト
        mode="poke",       # "reschedule" にするとポーリング中にワーカーを解放できる
    )

    @task
    def process_data() -> None:
        print("データが準備できました。処理を開始します。")

    wait_for_data >> process_data()


sensors_demo()
