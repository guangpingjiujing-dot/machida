from datetime import datetime

from airflow.decorators import dag, task


@dag(
    schedule="@daily",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["example"],
)
def hello_world():
    """最小限のDAGサンプル。2タスクをデータを渡しながら順番に実行する。"""

    @task
    def greet() -> str:
        message = "Hello, Airflow!"
        print(message)
        return message

    @task
    def farewell(message: str) -> None:
        print(f"受け取ったメッセージ: {message}")
        print("Bye, Airflow!")

    farewell(greet())


hello_world()
