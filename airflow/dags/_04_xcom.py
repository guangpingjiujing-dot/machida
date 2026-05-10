from datetime import datetime

from airflow.decorators import dag, task
from airflow.operators.python import PythonOperator


@dag(schedule=None, start_date=datetime(2024, 1, 1), catchup=False, tags=["xcom"])
def xcom_demo():
    """タスク間のデータ受け渡し（XCom）を2種類の方法で確認するDAG。

    方法1: TaskFlow API（暗黙的） - 関数の戻り値/引数がそのままXComに使われる
    方法2: 明示的なxcom_push / xcom_pull
    """

    # --- 方法1: TaskFlow API（推奨） ---
    @task
    def implicit_push() -> dict:
        data = {"user": "Alice", "score": 95}
        print(f"送信: {data}")
        return data  # 戻り値が自動的にXComに保存される

    @task
    def implicit_pull(data: dict) -> None:
        # 引数に渡すだけで自動的にXComから取得される
        print(f"受信: {data}")
        print(f"ユーザー: {data['user']}, スコア: {data['score']}")

    # --- 方法2: 明示的なxcom_push / xcom_pull ---
    # @task デコレータを使わない旧来の書き方。
    # Airflow は実行時に **context を自動で渡す。
    # context["ti"] は Task Instance（実行中のタスク自身）を表すオブジェクトで、
    # xcom_push / xcom_pull などタスクに紐づいた操作はここ経由で行う。
    def _explicit_push(**context) -> None:
        # key を指定して任意の値を XCom に保存する
        context["ti"].xcom_push(key="result", value="明示的に保存した値")
        print("xcom_pushしました")

    def _explicit_pull(**context) -> None:
        # どのタスク（task_ids）のどのキー（key）か両方指定して取得する
        value = context["ti"].xcom_pull(task_ids="explicit_push", key="result")
        print(f"xcom_pullで取得: {value}")

    # @task デコレータを使わない通常の関数は PythonOperator でラップして
    # Airflow タスクとして登録する（@task はこの登録を自動でやるシンタックスシュガー）
    explicit_push = PythonOperator(task_id="explicit_push", python_callable=_explicit_push)
    explicit_pull = PythonOperator(task_id="explicit_pull", python_callable=_explicit_pull)

    implicit_pull(implicit_push())
    explicit_push >> explicit_pull


xcom_demo()
