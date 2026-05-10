import random
from datetime import datetime

from airflow.decorators import dag, task
from airflow.operators.python import BranchPythonOperator


@dag(schedule=None, start_date=datetime(2024, 1, 1), catchup=False, tags=["branching"])
def branching():
    """条件によって実行するタスクを切り替えるDAG。選ばれなかったタスクはスキップされる。"""

    def _choose_branch() -> str:
        score = random.randint(0, 100)
        print(f"スコア: {score}")
        # 返り値は次に実行するタスクのtask_id
        if score >= 80:
            return "high_score"
        elif score >= 50:
            return "mid_score"
        else:
            return "low_score"

    branch = BranchPythonOperator(
        task_id="branch",
        python_callable=_choose_branch,
    )

    @task
    def high_score() -> None:
        print("優秀！スコア80以上")

    @task
    def mid_score() -> None:
        print("合格。スコア50〜79")

    @task
    def low_score() -> None:
        print("不合格。スコア50未満")

    # BranchPythonOperatorの結果に応じていずれか1つだけ実行される
    # 残り2つはUI上で "skipped"（グレー）になる
    branch >> [high_score(), mid_score(), low_score()]


branching()
