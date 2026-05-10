from datetime import datetime

from airflow.decorators import dag, task


@dag(schedule=None, start_date=datetime(2024, 1, 1), catchup=False, tags=["dependencies"])
def task_dependencies():
    """タスクの依存関係（直列・並列・ファンイン）を確認するDAG。"""

    @task
    def extract_db() -> str:
        print("DBからデータ取得")
        return "db_data"

    @task
    def extract_api() -> str:
        print("APIからデータ取得")
        return "api_data"

    @task
    def extract_file() -> str:
        print("ファイルからデータ取得")
        return "file_data"

    @task
    def merge(db: str, api: str, file: str) -> str:
        # 3つのタスクがすべて完了してから実行される（ファンイン）
        result = f"merged({db}, {api}, {file})"
        print(f"マージ完了: {result}")
        return result

    @task
    def load(data: str) -> None:
        print(f"書き込み: {data}")

    # extract_db / extract_api / extract_file は並列実行
    # merge は3つすべてが完了してから実行（ファンイン）
    # load は merge の後に実行（直列）
    load(merge(extract_db(), extract_api(), extract_file()))


task_dependencies()
